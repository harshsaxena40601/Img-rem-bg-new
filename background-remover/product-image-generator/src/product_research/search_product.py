from pathlib import Path
import json
import os

from dotenv import load_dotenv
from serpapi import GoogleSearch


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

OUTPUT_DIR = PROJECT_ROOT / "output" / "search_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def search_google_lens(image_url):
    """
    Search a Cloudinary/public image URL using Google Lens.
    """

    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        raise ValueError("SERPAPI_KEY is missing from .env")

    if not image_url:
        raise ValueError("Image URL is required")

    print("\nSearching Google Lens...")
    print(f"Image URL: {image_url}")

    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": api_key,
    }

    search = GoogleSearch(params)

    return search.get_dict()


def save_results(results):
    """
    Save the complete Google Lens response.
    """

    output_path = OUTPUT_DIR / "raw_results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nResults saved:")
    print(output_path)


def search_product(image_url):
    """
    Main reusable function.

    Input:
        Public product image URL

    Output:
        Google Lens search results
    """

    results = search_google_lens(image_url)

    save_results(results)

    return results


def main():

    print("\n" + "=" * 55)
    print("PRODUCT VISUAL SEARCH")
    print("=" * 55)

    image_url = input(
        "\nPaste a public product image URL: "
    ).strip()

    if not image_url:
        print("ERROR: No image URL provided.")
        return

    results = search_product(image_url)

    visual_matches = results.get("visual_matches", [])

    print("\n" + "=" * 55)
    print("SEARCH COMPLETE")
    print("=" * 55)

    print(f"\nVisual matches found: {len(visual_matches)}")


if __name__ == "__main__":
    main()