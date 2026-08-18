from pathlib import Path
import json
import os

from dotenv import load_dotenv
from serpapi import GoogleSearch


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

OUTPUT_DIR = PROJECT_ROOT / "output" / "search_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def search_google_products(query):
    """
    Search Google Shopping for a product.
    """

    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        raise ValueError("SERPAPI_KEY is missing from .env")

    if not query:
        raise ValueError("Product search query is required")

    print("\nSearching Google Products...")
    print(f"Query: {query}")

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    return results


def save_results(results):
    """
    Save Google Shopping results.
    """

    output_path = OUTPUT_DIR / "google_products.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nResults saved:")
    print(output_path)


def main():

    print("\n" + "=" * 55)
    print("GOOGLE PRODUCT SEARCH")
    print("=" * 55)

    query = input(
        "\nEnter product name to search: "
    ).strip()

    if not query:
        print("ERROR: No search query provided.")
        return

    results = search_google_products(query)

    save_results(results)

    shopping_results = results.get(
        "shopping_results",
        []
    )

    print("\n" + "=" * 55)
    print("SEARCH COMPLETE")
    print("=" * 55)

    print(
        f"\nProducts found: {len(shopping_results)}"
    )

    for index, product in enumerate(
        shopping_results[:5],
        start=1
    ):
        print(f"\n{index}. {product.get('title')}")
        print(f"   Source: {product.get('source')}")
        print(f"   Price: {product.get('price')}")


if __name__ == "__main__":
    main()