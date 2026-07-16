from dotenv import load_dotenv
import os

#加载.env文件
load_dotenv()

class Config:
    """Jarvis 配置类"""

    def __init__(self):
        self.name = os.getenv("APP_NAME", "Jarvis")
        self.version = os.getenv("APP_VERSION", "0.1.0")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")
        self.base_url = os.getenv("BASE_URL", "https://api.openai.com/v1")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")
        self.embedding_model_api_key = os.getenv("EMBEDDING_MODEL_API_KEY", self.openai_api_key)
        self.embedding_model_base_url = os.getenv("EMBEDDING_MODEL_BASE_URL", self.base_url)

        