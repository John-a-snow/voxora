import os
import time
import logging
import pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"
    settings = Settings()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%levelname)s] %(message)s"
    )

    logger = logging.getLogger("voice_rag_telemetry")

    class TelemetryTimer:
        def __init__(self, operation_name: str):
            self.operation_name = operation_name
            self.start_time = 0.0
            self.elapsed_ms = 0.0

        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.elapsed_ms = round