import os
import base64
import io

from dotenv import load_dotenv
from groq import Groq

from PIL import Image


load_dotenv()


def get_client():

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY was not found in .env"
        )

    return Groq(
        api_key=api_key
    )


def image_to_data_url(image):

    if not isinstance(
        image,
        Image.Image
    ):

        return None

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG"
    )

    encoded_image = base64.b64encode(
        buffer.getvalue()
    ).decode(
        "utf-8"
    )

    return (
        "data:image/jpeg;base64,"
        + encoded_image
    )


def build_messages(contents):

    content_parts = []

    for item in contents:

        # TEXT
        if isinstance(
            item,
            str
        ):

            content_parts.append(
                {
                    "type": "text",
                    "text": item,
                }
            )

        # IMAGE
        elif isinstance(
            item,
            Image.Image
        ):

            image_url = image_to_data_url(
                item
            )

            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            )

    return [
        {
            "role": "user",
            "content": content_parts,
        }
    ]


def generate(
    model,
    contents,
):

    client = get_client()

    messages = build_messages(
        contents
    )

    response = (
        client.chat.completions.create(
            model=model,
            messages=messages,
        )
    )

    text = response.choices[
        0
    ].message.content

    usage = response.usage

    return {
        "text": text,
        "usage": {
            "input_tokens": (
                usage.prompt_tokens
                if usage
                else 0
            ),
            "output_tokens": (
                usage.completion_tokens
                if usage
                else 0
            ),
            "total_tokens": (
                usage.total_tokens
                if usage
                else 0
            ),
        },
    }