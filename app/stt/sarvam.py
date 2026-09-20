import os
import time
from dataclasses import dataclass

import requests


SARVAM_URL = "https://api.sarvam.ai/speech-to-text"


@dataclass
class STTResult:
    transcript: str
    detected_language: str
    latency_ms: float
    request_id: str = ""


class SarvamSTTProvider:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "saaras:v4"
    ):
        self.api_key = (
            api_key
            or os.getenv("SARVAM_API_KEY")
        )

        self.model = model

        if not self.api_key:
            raise ValueError(
                "SARVAM_API_KEY is not configured."
            )

    def transcribe(
        self,
        file_path: str
    ) -> STTResult:

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Audio file not found: {file_path}"
            )

        start = time.perf_counter()

        headers = {
            "api-subscription-key": self.api_key
        }

        data = {
            "model": self.model,
            "language_code": "unknown",
            "mode": "transcribe"
        }

        with open(file_path, "rb") as audio_file:
            files = {
                "file": (
                    os.path.basename(file_path),
                    audio_file,
                    self._content_type(file_path)
                )
            }

            response = requests.post(
                SARVAM_URL,
                headers=headers,
                data=data,
                files=files,
                timeout=60
            )

        latency_ms = round(
            (time.perf_counter() - start) * 1000.0,
            2
        )

        if not response.ok:
            try:
                error_data = response.json()
            except Exception:
                error_data = {}

            message = (
                error_data.get("error", {}).get("message")
                if isinstance(
                    error_data.get("error"),
                    dict
                )
                else None
            )

            if not message:
                message = response.text

            raise RuntimeError(
                f"Sarvam STT request failed "
                f"({response.status_code}): {message}"
            )

        result = response.json()

        transcript = (
            result.get("transcript") or ""
        ).strip()

        language = (
            result.get("language_code")
            or "unknown"
        )

        request_id = (
            result.get("request_id")
            or ""
        )

        return STTResult(
            transcript=transcript,
            detected_language=language,
            latency_ms=latency_ms,
            request_id=request_id
        )

    @staticmethod
    def _content_type(file_path: str) -> str:
        extension = os.path.splitext(
            file_path
        )[1].lower()

        content_types = {
            ".wav": "audio/wav",
            ".webm": "audio/webm",
            ".ogg": "audio/ogg",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".aac": "audio/aac",
            ".flac": "audio/flac"
        }

        return content_types.get(
            extension,
            "application/octet-stream"
        )