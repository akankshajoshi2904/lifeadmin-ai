
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = None
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(
        api_key=api_key,
        max_retries=0,
        timeout=15.0,
    )


def ask_ai(prompt: str) -> str:
    """Request a response from OpenAI or raise a clear error."""
    if client is None:
        raise RuntimeError(
            "OpenAI API key is missing. Check your local .env configuration."
        )

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )
        return response.output_text

    except Exception as exc:
        raise RuntimeError(
            "OpenAI request failed. Check API quota, credentials, "
            "network connection, and model access."
        ) from exc
