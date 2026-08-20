import json
import re


def extract_json(text):

    if not text:
        raise ValueError(
            "AI returned an empty response."
        )

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL,
    ).strip()

    text = re.sub(
        r"```json",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.replace(
        "```",
        ""
    ).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        pass

    object_match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if object_match:

        json_text = object_match.group()

        return json.loads(
            json_text
        )

    array_match = re.search(
        r"\[.*\]",
        text,
        flags=re.DOTALL,
    )

    if array_match:

        json_text = array_match.group()

        return json.loads(
            json_text
        )

    raise ValueError(
        "No valid JSON found in AI response."
    )