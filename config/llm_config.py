import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic

load_dotenv()

class LLMConfig:
    def __init__(self):
        self.use_api = os.getenv("USE_API", "false").lower() == "true"
        self.api_provider = os.getenv("API_PROVIDER", "openai")
        self.api_key = os.getenv("API_KEY", "")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        # Timeout (seconds) to wait for Ollama responses. Can be configured via OLLAMA_TIMEOUT.
        self.ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "300"))
        # Number of retries for transient read timeouts when calling Ollama.
        self.ollama_max_retries = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))
    
    def get_llm(self):
        """
        Returns configured LLM instance based on environment settings.
        """
        if not self.use_api:
            # Use Ollama (local)
            print(f"Using Ollama with model: {self.ollama_model}")
            return Ollama(
                model=self.ollama_model,
                base_url=self.ollama_base_url,
                timeout=300,
                temperature=0.7
            )
        else:
            # Use API-based LLM
            print(f"Using API provider: {self.api_provider}")
            
            if self.api_provider == "openai":
                return ChatOpenAI(
                    model="gpt-4",
                    temperature=0.7,
                    openai_api_key=self.api_key
                )
            elif self.api_provider == "anthropic":
                return ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    temperature=0.7,
                    anthropic_api_key=self.api_key
                )
            elif self.api_provider == "groq":
                from langchain_community.chat_models import ChatGroq
                return ChatGroq(
                    model="mixtral-8x7b-32768",
                    temperature=0.7,
                    groq_api_key=self.api_key
                )
            else:
                raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def get_config_info(self):
        """Returns configuration information as a dictionary."""
        info = {
            "use_api": self.use_api,
            "provider": self.api_provider if self.use_api else "ollama",
            "model": self.ollama_model if not self.use_api else "API-based",
            "base_url": self.ollama_base_url if not self.use_api else "N/A"
        }
        if not self.use_api:
            info["timeout"] = self.ollama_timeout
            info["max_retries"] = self.ollama_max_retries
        return info