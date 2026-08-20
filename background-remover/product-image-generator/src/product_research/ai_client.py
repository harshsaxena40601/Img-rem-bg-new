import os
import time

from dotenv import load_dotenv
from google import genai

from ai_usage import (
    record_request,
    record_attempt,
    record_retry,
    record_success,
    record_failure,
)


load_dotenv()


# MODEL_NAMES = [
#     "gemini-2.5-flash",
#     "gemini-2.5-flash-lite",
# ]
MODEL_NAMES = [
    "fake-model-for-testing",
    "gemini-2.5-flash-lite",
]


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found in .env")

    return genai.Client(api_key=api_key)


def safe_generate_content(contents, max_attempts=3):
    record_request()

    client = get_client()

    last_error = None
    retry_delays = [2, 5, 10]
    total_attempts = 0

    for model_index, model_name in enumerate(MODEL_NAMES):
        for attempt in range(1, max_attempts + 1):
            total_attempts += 1

            try:
                print(
                    f"\nAI request attempt {attempt}/{max_attempts} "
                    f"using model '{model_name}'..."
                )

                record_attempt()

                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                )

                current_usage, usage = record_success(response)

                print("\n" + "=" * 55)
                print("AI USAGE")
                print("=" * 55)

                print(
                    f"\nModel used: {model_name}"
                )

                print(
                    f"This request input tokens: "
                    f"{current_usage['input_tokens']}"
                )

                print(
                    f"This request output tokens: "
                    f"{current_usage['output_tokens']}"
                )

                print(
                    f"This request total tokens: "
                    f"{current_usage['total_tokens']}"
                )

                print("\nCUMULATIVE USAGE:")

                print(
                    f"Logical requests: "
                    f"{usage['logical_requests']}"
                )

                print(
                    f"API attempts: "
                    f"{usage['api_attempts']}"
                )

                print(
                    f"Successful requests: "
                    f"{usage['successful_requests']}"
                )

                print(
                    f"Failed requests: "
                    f"{usage['failed_requests']}"
                )

                print(
                    f"Total tokens used: "
                    f"{usage['total_tokens']}"
                )

                return {
                    "success": True,
                    "response": response,
                    "error": None,
                    "attempts": total_attempts,
                    "model": model_name,
                    "used_fallback": model_index > 0,
                }

            except Exception as error:
                last_error = error

                print(
                    f"\nAI attempt {attempt} failed."
                )

                print(
                    f"Model: {model_name}"
                )

                print(
                    f"{type(error).__name__}: {error}"
                )

                if attempt < max_attempts:
                    record_retry()

                    delay = retry_delays[
                        min(
                            attempt - 1,
                            len(retry_delays) - 1,
                        )
                    ]

                    print(
                        f"\nRetrying in {delay} seconds..."
                    )

                    time.sleep(delay)

        # Current model exhausted
        if model_index < len(MODEL_NAMES) - 1:
            next_model = MODEL_NAMES[model_index + 1]

            print("\n" + "=" * 55)
            print(f"MODEL FAILED: {model_name}")
            print(f"SWITCHING TO FALLBACK: {next_model}")
            print("=" * 55)

    record_failure(last_error)

    print("\n" + "=" * 55)
    print("AI REQUEST FAILED")
    print("=" * 55)

    print("\nAll configured models failed.")

    return {
        "success": False,
        "response": None,
        "error": str(last_error),
        "attempts": total_attempts,
        "model": None,
        "used_fallback": False,
    }