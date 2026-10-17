import json
from botocore.exceptions import ClientError
from src.config.config import AWSConfig

class BedrockService:
    """Service for interacting with AWS Bedrock models"""

    def __init__(self):
        """Initialize the Bedrock service"""
        aws_config = AWSConfig()
        self.client = aws_config.get_bedrock_client()
        self.model_id = aws_config.bedrock_model_id
        self.embedding_model_id = aws_config.embedding_model_id
        self.embedding_dimensions = aws_config.embedding_dimensions

    def embed_text(self, text):
        """
        Embed text with Amazon Titan Text Embeddings V2

        Args:
            text (str): The text to embed

        Returns:
            list: Unit-length embedding vector (so dot product == cosine similarity)
        """
        response = self.client.invoke_model(
            modelId=self.embedding_model_id,
            body=json.dumps({
                "inputText": text,
                "dimensions": self.embedding_dimensions,
                "normalize": True
            })
        )
        return json.loads(response.get('body').read())["embedding"]

    def invoke_model(self, prompt, max_tokens=1000, temperature=0.7):
        """
        Invoke the Bedrock model with a prompt

        Args:
            prompt (str): The prompt to send to the model
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for generation (0.0-1.0)

        Returns:
            dict: The model response
        """
        try:
            # Prepare request body based on model type
            if "anthropic.claude" in self.model_id:
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            else:
                raise ValueError(f"Unsupported model: {self.model_id}")

            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # Parse and return response
            response_body = json.loads(response.get('body').read())

            if "anthropic.claude" in self.model_id:
                return {
                    "content": response_body.get("content", [{}])[0].get("text", ""),
                    "raw_response": response_body
                }
            else:
                return {"content": "", "raw_response": response_body}

        except ClientError as e:
            print(f"Error invoking Bedrock model: {e}")
            return {"content": "", "error": str(e)}

    def create_agent_knowledge_base(self, name, description, s3_bucket, s3_prefix):
        """
        Create a knowledge base for an agent

        Args:
            name (str): Name of the knowledge base
            description (str): Description of the knowledge base
            s3_bucket (str): S3 bucket where documents are stored
            s3_prefix (str): S3 prefix for the documents

        Returns:
            str: The knowledge base ID
        """
        try:
            bedrock_agent = AWSConfig().get_bedrock_agent_client()

            response = bedrock_agent.create_knowledge_base(
                name=name,
                description=description,
                roleArn="arn:aws:iam::123456789012:role/BedrockKnowledgeBaseRole",  # Replace with actual role
                knowledgeBaseConfiguration={
                    "type": "VECTOR",
                    "vectorKnowledgeBaseConfiguration": {
                        "embeddingModelArn": f"arn:aws:bedrock:{AWSConfig().aws_region}::foundation-model/amazon.titan-embed-text-v1"
                    }
                },
                storageConfiguration={
                    "type": "S3",
                    "s3Configuration": {
                        "bucketName": s3_bucket,
                        "prefix": s3_prefix
                    }
                }
            )

            return response.get("knowledgeBase", {}).get("knowledgeBaseId", "")

        except ClientError as e:
            print(f"Error creating knowledge base: {e}")
            return ""
