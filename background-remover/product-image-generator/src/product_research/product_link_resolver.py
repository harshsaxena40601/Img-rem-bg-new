from pathlib import Path
import json
import os

from dotenv import load_dotenv
from serpapi import GoogleSearch


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


FINAL_MATCH_FILE = (
    PROJECT_ROOT
    / "output"
    / "product_brain"
    / "final_match.json"
)


OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
    / "product_research"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR
    / "product_link_result.json"
)


def load_final_match():
    """
    Load the winning product selected by Product Brain.
    """

    if not FINAL_MATCH_FILE.exists():
        raise FileNotFoundError(
            f"Final match file not found:\n"
            f"{FINAL_MATCH_FILE}"
        )

    with open(
        FINAL_MATCH_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_product_token(final_match):
    """
    Get the immersive product page token.
    """

    matched_product = final_match.get(
        "matched_product",
        {}
    )

    token = matched_product.get(
        "immersive_product_page_token"
    )

    if not token:
        raise ValueError(
            "immersive_product_page_token "
            "not found in final_match.json"
        )

    return token


def search_immersive_product(token):
    """
    Request detailed product information
    using the Google Immersive Product API.
    """

    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        raise ValueError(
            "SERPAPI_KEY is missing from .env"
        )

    print("\nSearching product details...")

    params = {
        "engine": "google_immersive_product",
        "page_token": token,
        "api_key": api_key,
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    return results


def extract_offers(results):
    """
    Extract merchant offers and real product URLs.
    """

    offers = []

    sellers = results.get(
        "sellers_results",
        []
    )

    for seller in sellers:

        product_url = (
            seller.get("link")
            or seller.get("product_link")
        )

        offers.append(
            {
                "seller": seller.get("name"),
                "price": seller.get("price"),
                "product_url": product_url,
                "source": seller,
            }
        )

    return offers


def save_result(data):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nProduct link result saved:")
    print(OUTPUT_FILE)


def resolve_product_link():

    print("\n" + "=" * 60)
    print("PRODUCT LINK RESOLVER")
    print("=" * 60)

    print("\nLoading final match...")

    final_match = load_final_match()

    matched_product = final_match.get(
        "matched_product",
        {}
    )

    print(
        f"\nProduct:\n"
        f"{matched_product.get('title')}"
    )

    token = get_product_token(
        final_match
    )

    print(
        "\nImmersive product token found."
    )

    results = search_immersive_product(
        token
    )

    offers = extract_offers(results)

    result = {
        "success": True,
        "product": {
            "title": matched_product.get("title"),
            "source": matched_product.get("source"),
            "price": matched_product.get("price"),
            "visual_similarity": matched_product.get(
                "visual_similarity"
            ),
        },
        "offers": offers,
        "total_offers": len(offers),
        "raw_response": results,
    }

    save_result(result)

    print("\n" + "=" * 60)
    print("SELLER OFFERS")
    print("=" * 60)

    print(
        f"\nTotal offers found: "
        f"{len(offers)}"
    )

    for index, offer in enumerate(
        offers,
        start=1
    ):
        print(f"\n{index}. {offer['seller']}")
        print(f"   Price: {offer['price']}")
        print(
            f"   URL: "
            f"{offer['product_url']}"
        )

    return result


def main():
    return resolve_product_link()


if __name__ == "__main__":
    main()