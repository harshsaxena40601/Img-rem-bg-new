from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[3]

USAGE_FILE = (
    PROJECT_ROOT
    / "output"
    / "ai_usage"
    / "ai_usage.json"
)


def get_default_provider_usage():

    return {
        "api_attempts": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "total_retries": 0,

        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,

        "errors": {
            "503": 0,
            "429": 0,
            "other": 0,
        }
    }


def get_default_usage():

    return {
        "logical_requests": 0,

        "fallbacks": 0,

        "providers": {}
    }


def load_usage():

    if not USAGE_FILE.exists():
        return get_default_usage()

    with open(
        USAGE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        usage = json.load(file)

    default_usage = get_default_usage()

    for key, value in default_usage.items():

        if key not in usage:
            usage[key] = value

    return usage


def save_usage(usage):

    USAGE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        USAGE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            usage,
            file,
            indent=4
        )


def get_provider_usage(
    usage,
    provider
):

    providers = usage["providers"]

    if provider not in providers:

        providers[provider] = (
            get_default_provider_usage()
        )

    return providers[provider]


def record_request():

    usage = load_usage()

    usage["logical_requests"] += 1

    save_usage(usage)


def record_attempt(provider):

    usage = load_usage()

    provider_usage = get_provider_usage(
        usage,
        provider
    )

    provider_usage["api_attempts"] += 1

    save_usage(usage)


def record_retry(provider):

    usage = load_usage()

    provider_usage = get_provider_usage(
        usage,
        provider
    )

    provider_usage["total_retries"] += 1

    save_usage(usage)


def record_fallback():

    usage = load_usage()

    usage["fallbacks"] += 1

    save_usage(usage)


def record_success(
    provider,
    usage_data
):

    usage = load_usage()

    provider_usage = get_provider_usage(
        usage,
        provider
    )

    provider_usage[
        "successful_requests"
    ] += 1

    provider_usage[
        "total_input_tokens"
    ] += (
        usage_data.get(
            "input_tokens",
            0
        )
    )

    provider_usage[
        "total_output_tokens"
    ] += (
        usage_data.get(
            "output_tokens",
            0
        )
    )

    provider_usage[
        "total_tokens"
    ] += (
        usage_data.get(
            "total_tokens",
            0
        )
    )

    save_usage(usage)


def record_failure(
    provider,
    error
):

    usage = load_usage()

    provider_usage = get_provider_usage(
        usage,
        provider
    )

    provider_usage[
        "failed_requests"
    ] += 1

    error_text = str(error)

    if "503" in error_text:

        provider_usage[
            "errors"
        ]["503"] += 1

    elif "429" in error_text:

        provider_usage[
            "errors"
        ]["429"] += 1

    else:

        provider_usage[
            "errors"
        ]["other"] += 1

    save_usage(usage)


def get_statistics():

    return load_usage()


def print_usage():

    usage = get_statistics()

    print("\n" + "=" * 60)
    print("AI RELIABILITY & USAGE")
    print("=" * 60)

    print(
        f"\nLogical requests: "
        f"{usage['logical_requests']}"
    )

    print(
        f"Fallbacks used: "
        f"{usage['fallbacks']}"
    )

    print("\nPROVIDERS:")

    for provider, stats in (
        usage["providers"].items()
    ):

        print("\n" + "-" * 40)

        print(
            f"Provider: "
            f"{provider.upper()}"
        )

        print(
            f"API attempts: "
            f"{stats['api_attempts']}"
        )

        print(
            f"Successful requests: "
            f"{stats['successful_requests']}"
        )

        print(
            f"Failed requests: "
            f"{stats['failed_requests']}"
        )

        print(
            f"Retries: "
            f"{stats['total_retries']}"
        )

        print(
            f"Input tokens: "
            f"{stats['total_input_tokens']}"
        )

        print(
            f"Output tokens: "
            f"{stats['total_output_tokens']}"
        )

        print(
            f"Total tokens: "
            f"{stats['total_tokens']}"
        )

        print("\nErrors:")

        print(
            f"503: "
            f"{stats['errors']['503']}"
        )

        print(
            f"429: "
            f"{stats['errors']['429']}"
        )

        print(
            f"Other: "
            f"{stats['errors']['other']}"
        )

    print("\nUsage file:")

    print(USAGE_FILE)