import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def generate(
    contents,
    model,
):

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "GEMINI_API_KEY was not found"
        )

    client = genai.Client(
        api_key=api_key
    )

    response = (
        client.models.generate_content(
            model=model,
            contents=contents,
        )
    )

    usage_metadata = getattr(
        response,
        "usage_metadata",
        None
    )

    input_tokens = getattr(
        usage_metadata,
        "prompt_token_count",
        0
    ) if usage_metadata else 0

    output_tokens = getattr(
        usage_metadata,
        "candidates_token_count",
        0
    ) if usage_metadata else 0

    total_tokens = getattr(
        usage_metadata,
        "total_token_count",
        0
    ) if usage_metadata else 0

    return {
        "text": response.text,

        "usage": {
            "input_tokens": input_tokens or 0,
            "output_tokens": output_tokens or 0,
            "total_tokens": total_tokens or 0,
        },
    }