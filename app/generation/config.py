import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    provider: str = os.getenv(
        "LLM_PROVIDER",
        "groq"
    )

    model_name: str = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )

    temperature: float = 0.2

    max_tokens: int = 512

    max_context_documents: int = 5

    api_key_env_name: str = "GROQ_API_KEY"

    def get_api_key(self) -> str:
        if self.provider.lower() == "gemini":
            self.api_key_env_name = "GOOGLE_API_KEY"
        else:
            self.api_key_env_name = "GROQ_API_KEY"

        return os.getenv(
            self.api_key_env_name,
            ""
        )


DEFAULT_LLM_CONFIG = LLMConfig()