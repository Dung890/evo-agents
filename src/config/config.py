import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AWSConfig:
    """AWS Configuration and client setup for the UTD Career Advisory AI System"""

    def __init__(self):
        """Initialize AWS configuration from environment variables"""
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-2")
        self.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        self.bedrock_endpoint = os.getenv("BEDROCK_ENDPOINT") # Optional
        self.embedding_model_id = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
        self.embedding_dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "512"))

        # Scraping configuration
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.rapidapi_host = os.getenv("RAPIDAPI_HOST", "indeed12.p.rapidapi.com")
        self.scraping_delay_min = int(os.getenv("SCRAPING_DELAY_MIN", "2"))
        self.scraping_delay_max = int(os.getenv("SCRAPING_DELAY_MAX", "5"))
        self.max_jobs_per_source = int(os.getenv("MAX_JOBS_PER_SOURCE", "20"))
        self.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", "24"))
        
        # UTD Course Catalog configuration
        self.utd_course_catalog_url = os.getenv("UTD_COURSE_CATALOG_URL", "https://coursebook.utdallas.edu/")
        self.target_departments = os.getenv("TARGET_DEPARTMENTS", "CS,SE,MATH,STAT,BA,SYSM").split(",")

        # Validate required configuration
        self._validate_config()

    def _validate_config(self):
        """Validate that required AWS configuration is present for local development."""
        # In a deployed environment (like EC2 with an IAM role), keys may not be set.
        # Boto3 will automatically use the instance role.
        # We only enforce this for local development where a .env file is expected.
        if self.aws_access_key_id and not self.aws_secret_access_key:
            raise ValueError("AWS_SECRET_ACCESS_KEY must be set if AWS_ACCESS_KEY_ID is provided.")
        if not self.aws_region:
            raise ValueError("AWS_REGION must be set.")

        # Warn about optional but recommended configurations
        if not self.rapidapi_key:
            print("Warning: RAPIDAPI_KEY not set. Indeed scraping will be limited.")

    def get_bedrock_client(self):
        """Get an AWS Bedrock runtime client."""
        # If keys are provided, use them (local development).
        # Otherwise, let boto3 use the environment's IAM role (deployed).
        if self.aws_access_key_id and self.aws_secret_access_key:
            return boto3.client(
                service_name="bedrock-runtime",
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
        else:
            return boto3.client(
                service_name="bedrock-runtime",
                region_name=self.aws_region,
            )

    def get_s3_client(self):
        """Get an AWS S3 client"""
        return boto3.client(
            service_name="s3",
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def get_dynamodb_client(self):
        """Get an AWS DynamoDB client"""
        return boto3.client(
            service_name="dynamodb",
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def get_bedrock_agent_client(self):
        """Get an AWS Bedrock agent client"""
        return boto3.client(
            service_name="bedrock-agent",
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
    
    def get_scraping_config(self):
        """Get scraping configuration"""
        return {
            "rapidapi_key": self.rapidapi_key,
            "rapidapi_host": self.rapidapi_host,
            "delay_min": self.scraping_delay_min,
            "delay_max": self.scraping_delay_max,
            "max_jobs_per_source": self.max_jobs_per_source,
            "cache_ttl_hours": self.cache_ttl_hours,
            "utd_catalog_url": self.utd_course_catalog_url,
            "target_departments": self.target_departments
        }
