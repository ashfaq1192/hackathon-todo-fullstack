"""Gemini API client using OpenAI-compatible interface.

This module implements the HYBRID architecture: OpenAI SDK with Gemini API backend.
The AsyncOpenAI client is configured to use Gemini's OpenAI-compatible endpoint,
allowing us to use the Swarm framework with Gemini's free tier (1500 req/day).
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file at project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from openai import OpenAI


class GeminiClient:
    """HYBRID Gemini client using OpenAI SDK.

    This client uses the OpenAI SDK (synchronous) but points to Gemini's
    OpenAI-compatible endpoint. This enables:
    - Free tier Gemini API (1500 requests/day, 15 requests/minute)
    - Full compatibility with OpenAI Agents SDK (Swarm framework)
    - Native function calling support for MCP tools
    - No code changes required for future OpenAI API migration

    Environment Variables:
        GEMINI_API_KEY: Gemini API key from https://makersuite.google.com/app/apikey
        GEMINI_BASE_URL: Gemini OpenAI-compatible endpoint (default: https://generativelanguage.googleapis.com/v1beta/openai/)
        GEMINI_MODEL: Gemini model name (default: gemini-2.0-flash-exp)

    Example:
        >>> client = GeminiClient()
        >>> openai_client = client.get_client()
        >>> response = openai_client.chat.completions.create(
        ...     model=client.model,
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize Gemini client with OpenAI-compatible interface.

        Args:
            api_key: Gemini API key (default: from GEMINI_API_KEY env var)
            base_url: Gemini base URL (default: from GEMINI_BASE_URL env var)
            model: Gemini model name (default: from GEMINI_MODEL env var)

        Raises:
            ValueError: If GEMINI_API_KEY is not provided and not in environment
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY must be provided or set in environment variables. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )

        self.base_url = base_url or os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Initialize OpenAI client with Gemini endpoint (synchronous for Swarm compatibility)
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_client(self) -> OpenAI:
        """Get the configured OpenAI client.

        Returns:
            OpenAI: Client instance configured for Gemini API
        """
        return self._client

    @property
    def client(self) -> OpenAI:
        """OpenAI client property.

        Returns:
            OpenAI: Client instance configured for Gemini API
        """
        return self._client


# Singleton instance for application-wide use
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create singleton Gemini client instance.

    Returns:
        GeminiClient: Singleton client instance

    Example:
        >>> client = get_gemini_client()
        >>> async_openai = client.get_client()
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
