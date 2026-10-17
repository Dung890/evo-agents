#!/usr/bin/env python3
import os
import sys
import subprocess
import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_s3_assets as s3_assets,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_ecr_assets as ecr_assets,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    RemovalPolicy,
    Duration,
)
from constructs import Construct

# Configuration
APP_NAME = "aws-agetic-ai"
FRONTEND_PATH = "frontend"
DOCKERFILE_PATH = "."
ACCOUNT = os.environ.get("CDK_DEFAULT_ACCOUNT")
REGION = os.environ.get("CDK_DEFAULT_REGION")


def check_docker_running():
    """Checks if the Docker daemon is running."""
    try:
        subprocess.run("docker info", shell=True, check=True, capture_output=True)
        print("Docker daemon is running.")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Docker daemon is not running. Please start Docker and try again.")
        return False


class AgeticAiStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Backend Deployment (EC2 Instance with Load Balancer) ---

        # 1. Define the VPC
        vpc = ec2.Vpc(self, f"{APP_NAME}-Vpc", max_azs=2)

        # 2. Build and push the Docker image to ECR
        backend_image = ecr_assets.DockerImageAsset(
            self, f"{APP_NAME}-BackendImage", directory=DOCKERFILE_PATH
        )

        # 3. Create an IAM role for the EC2 instance
        ec2_role = iam.Role(
            self, f"{APP_NAME}-EC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        backend_image.repository.grant_pull(ec2_role)
        ec2_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                    f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0",
                ],
            )
        )

        # 4. Create security groups
        # ALB Security Group
        alb_sg = ec2.SecurityGroup(
            self,
            f"{APP_NAME}-ALBSG",
            vpc=vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=True  # Allow ALB to reach EC2 instances
        )
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP from internet")
        
        # EC2 Instance Security Group
        instance_sg = ec2.SecurityGroup(
            self,
            f"{APP_NAME}-InstanceSG",
            vpc=vpc,
            description="Security group for backend EC2 instance",
            allow_all_outbound=True
        )
        instance_sg.add_ingress_rule(alb_sg, ec2.Port.tcp(80), "Allow HTTP from ALB")
        instance_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH")

        # 5. Create the EC2 instance
        instance = ec2.Instance(
            self,
            f"{APP_NAME}-Instance",
            vpc=vpc,
            instance_type=ec2.InstanceType("t3.small"),  # Upgraded for better performance
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            role=ec2_role,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=instance_sg,
            key_pair=ec2.KeyPair.from_key_pair_name(self, f"{APP_NAME}-KeyPair", "aws-agetic-ai-key"),
        )

        # 6. Add User Data script to set up Docker and run the application
        instance.user_data.add_commands(
            "exec > /home/ec2-user/user-data.log 2>&1",
            "set -x",
            "dnf update -y",
            "dnf install -y docker",
            "systemctl start docker",
            "systemctl enable docker",
            "usermod -a -G docker ec2-user",
            f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {self.account}.dkr.ecr.{self.region}.amazonaws.com",
            f"docker pull {backend_image.image_uri}",
            f"docker run -d -p 80:8080 --restart unless-stopped "
            f"-e AWS_REGION={self.region} "
            f"-e BEDROCK_MODEL_ID='anthropic.claude-3-sonnet-20240229-v1:0' "
            f"{backend_image.image_uri}",
        )

        # 7. Create Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self,
            f"{APP_NAME}-ALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name=f"{APP_NAME}-alb",
            security_group=alb_sg
        )

        # 8. Create target group
        target_group = elbv2.ApplicationTargetGroup(
            self,
            f"{APP_NAME}-TargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(
                path="/health",
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=3
            )
        )
        
        # Add the EC2 instance to the target group
        target_group.add_target(targets.InstanceTarget(instance))

        # 9. Add listener to ALB
        listener = alb.add_listener(
            f"{APP_NAME}-Listener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[target_group]
        )

        # --- Frontend Deployment (S3 + CloudFront) ---

        # 1. Create environment file with empty API URL to use relative paths through CloudFront
        # This ensures all API requests go through CloudFront to the backend
        env_content = "VITE_API_URL=\n"
        
        env_file_path = os.path.join(FRONTEND_PATH, ".env.production")
        with open(env_file_path, "w") as f:
            f.write(env_content)
        print("Created frontend .env.production with relative API URL for CloudFront routing")

        # 2. Build the frontend application
        print("Building frontend application...")
        try:
            subprocess.run(
                "npm ci && npm run build",
                shell=True,
                check=True,
                cwd=FRONTEND_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("Frontend build successful.")
        except subprocess.CalledProcessError as e:
            print("ERROR: Frontend build failed.")
            print(e.stderr.decode())
            raise

        # 3. Create a private S3 bucket for the frontend static site
        frontend_bucket = s3.Bucket(
            self,
            f"{APP_NAME}-FrontendBucket",
            bucket_name=f"{APP_NAME.lower()}-frontend-{ACCOUNT}-{REGION}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # 4. Create a CloudFront Origin Access Identity (OAI)
        oai = cloudfront.OriginAccessIdentity(
            self, f"{APP_NAME}-OAI"
        )
        frontend_bucket.grant_read(oai)

        # 5. Create a CloudFront distribution
        # Note: /api/* pattern will catch all API routes including:
        #   - /api/career-guidance
        #   - /api/courses/all
        #   - /api/onboarding/* (quick-start, comprehensive, options, etc.)
        #   - /api/project-recommendations
        #   - /api/agents/status
        #   - /api/stats
        distribution = cloudfront.Distribution(
            self,
            f"{APP_NAME}-CloudFrontDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(frontend_bucket, origin_access_identity=oai),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            additional_behaviors={
                # Primary API endpoint - catches all /api/* routes
                "/api/*": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                # Authentication endpoints
                "/auth/*": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                # API Documentation endpoints
                "/docs": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                ),
                "/openapi.json": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                ),
                "/redoc": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                ),
                # Legacy direct endpoints (for backward compatibility)
                "/job-market": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                "/course-search": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                "/agent-capabilities": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                # Health check endpoint
                "/health": cloudfront.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(alb, protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                ),
            },
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0)
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0)
                )
            ]
        )

        # 6. Deploy the built frontend to the S3 bucket
        s3_deployment.BucketDeployment(
            self,
            f"{APP_NAME}-S3Deployment",
            sources=[s3_deployment.Source.asset(os.path.join(FRONTEND_PATH, "dist"))],
            destination_bucket=frontend_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # --- Outputs ---
        cdk.CfnOutput(
            self,
            "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="The URL for the frontend application (use this URL)",
        )
        cdk.CfnOutput(
            self,
            "LoadBalancerURL",
            value=f"http://{alb.load_balancer_dns_name}",
            description="The Load Balancer URL for the backend API",
        )
        cdk.CfnOutput(
            self,
            "EC2InstanceIP",
            value=instance.instance_public_ip,
            description="The Public IP of the backend EC2 instance for SSH access",
        )


def main():
    """Initializes and synthesizes the CDK app."""
    print("Starting CDK deployment...")

    if not check_docker_running():
        sys.exit(1)

    if not all([ACCOUNT, REGION]):
        raise EnvironmentError(
            "CDK environment variables CDK_DEFAULT_ACCOUNT and CDK_DEFAULT_REGION must be set."
            "Please configure your AWS CLI and environment."
        )

    app = cdk.App()
    AgeticAiStack(app, APP_NAME)
    app.synth()


if __name__ == "__main__":
    main()
