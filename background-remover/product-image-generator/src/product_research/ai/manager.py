import re
import time

from ai.config import AI_PROVIDERS

from ai.providers import gemini
from ai.providers import groq

from ai.ai_usage import (
    record_request,
    record_attempt,
    record_retry,
    record_fallback,
    record_success,
    record_failure,
)


PROVIDER_MAP = {
    "gemini": gemini,
    "groq": groq,
}


def clean_ai_text(text):
    if not text:
        return ""

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL,
    )

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return text.strip()


def get_enabled_providers(task_type=None):
    providers = [
        provider
        for provider in AI_PROVIDERS
        if provider.get("enabled", False)
    ]

    if task_type:
        providers = [
            provider
            for provider in providers
            if task_type in provider.get("capabilities", [])
        ]

    return providers


def generate_ai(contents, task_type="text"):
    total_attempts = 0
    errors = []

    enabled_providers = get_enabled_providers(task_type)

    if not enabled_providers:
        return {
            "success": False,
            "text": None,
            "provider": None,
            "model": None,
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            },
            "total_attempts": 0,
            "fallback_used": False,
            "error": f"No AI providers enabled for task type: '{task_type}'.",
        }

    record_request()

    primary_provider = enabled_providers[0]["provider"]
    fallback_recorded = False

    for provider_index, provider_config in enumerate(enabled_providers):
        provider_name = provider_config["provider"]
        model = provider_config["model"]
        max_attempts = provider_config["max_attempts"]

        provider = PROVIDER_MAP.get(provider_name)

        if not provider:
            error_message = f"Unknown provider: {provider_name}"
            errors.append(error_message)
            continue

        if provider_index > 0 and not fallback_recorded:
            record_fallback()
            fallback_recorded = True

        print("\n" + "=" * 60)
        print(f"TRYING PROVIDER: {provider_name.upper()}")
        print(f"MODEL: {model}")
        print(f"TASK TYPE: {task_type}")
        print("=" * 60)

        last_error = None

        for attempt in range(1, max_attempts + 1):
            total_attempts += 1
            record_attempt(provider_name)

            try:
                print(f"\nAttempt {attempt}/{max_attempts}")

                result = provider.generate(
                    contents=contents,
                    model=model,
                )

                clean_text = clean_ai_text(result["text"])

                record_success(
                    provider=provider_name,
                    usage_data=result["usage"],
                )

                print("\nAI REQUEST SUCCESSFUL")

                return {
                    "success": True,
                    "text": clean_text,
                    "provider": provider_name,
                    "model": model,
                    "usage": result["usage"],
                    "total_attempts": total_attempts,
                    "fallback_used": (provider_name != primary_provider),
                    "error": None,
                }

            except Exception as error:
                last_error = error

                error_message = (
                    f"{provider_name} ({model}) attempt {attempt} failed: "
                    f"{type(error).__name__}: {error}"
                )

                print("\n" + error_message)
                errors.append(error_message)

                if attempt < max_attempts:
                    record_retry(provider_name)
                    delay = attempt * 2
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

        if last_error:
            record_failure(
                provider=provider_name,
                error=last_error,
            )

        print("\nProvider failed.")

        if provider_index < len(enabled_providers) - 1:
            print("Trying next provider...")

    return {
        "success": False,
        "text": None,
        "provider": None,
        "model": None,
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
        "total_attempts": total_attempts,
        "fallback_used": len(enabled_providers) > 1,
        "error": "\n".join(errors),
    }