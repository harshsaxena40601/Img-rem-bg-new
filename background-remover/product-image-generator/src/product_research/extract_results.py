from pathlib import Path
import json
from collections import Counter
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = PROJECT_ROOT / "output" / "search_results"

RAW_RESULTS_FILE = RESULTS_DIR / "raw_results.json"
OUTPUT_FILE = RESULTS_DIR / "product_candidates.json"


STOP_WORDS = {
    "bag",
    "bags",
    "handbag",
    "handbags",
    "leather",
    "women",
    "womens",
    "woman",
    "sale",
    "shop",
    "buy",
    "new",
    "large",
    "small",
    "medium",
    "tote",
    "shoulder",
    "crossbody",
    "cross",
    "body",
    "top",
    "handle",
    "official",
}


def get_titles(results):
    """Extract titles from Google Lens visual matches."""

    titles = []

    for item in results.get("visual_matches", []):

        title = item.get("title")

        if title:
            titles.append(title)

    return titles


def extract_words(titles):
    """Extract meaningful words from product titles."""

    words = []

    for title in titles:

        cleaned = re.sub(
            r"[^a-zA-Z0-9\s]",
            " ",
            title.lower()
        )

        for word in cleaned.split():

            if (
                len(word) > 2
                and word not in STOP_WORDS
            ):
                words.append(word)

    return words


def create_candidates(word_counts, limit=20):
    """Create ranked keyword candidates."""

    return [
        {
            "word": word,
            "count": count
        }
        for word, count in word_counts.most_common(limit)
    ]


def build_product_query(word_counts):
    """Build a likely product search query."""

    top_words = [
        word
        for word, count in word_counts.most_common(10)
        if count >= 3
    ]

    query_words = top_words[:3]

    return " ".join(
        word.capitalize()
        for word in query_words
    )


def calculate_confidence(word_counts):
    """Estimate confidence from repeated keywords."""

    top_counts = [
        count
        for _, count in word_counts.most_common(3)
    ]

    if len(top_counts) < 3:
        return "low"

    average = sum(top_counts) / 3

    if average >= 20:
        return "high"

    if average >= 8:
        return "medium"

    return "low"


def save_results(data):
    """Save extracted product identity."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

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

    print(f"\nIdentity saved:")
    print(OUTPUT_FILE)


def extract_product_identity(results):
    """
    Main reusable function.

    Input:
        Google Lens results dictionary

    Output:
        Product identity dictionary
    """

    titles = get_titles(results)

    if not titles:
        raise ValueError(
            "No visual match titles found."
        )

    words = extract_words(titles)

    word_counts = Counter(words)

    candidates = create_candidates(word_counts)

    suggested_query = build_product_query(
        word_counts
    )

    confidence = calculate_confidence(
        word_counts
    )

    identity = {
        "total_visual_matches": len(
            results.get("visual_matches", [])
        ),
        "titles_analyzed": len(titles),
        "suggested_query": suggested_query,
        "confidence": confidence,
        "top_words": candidates,
        "sample_titles": titles[:20]
    }

    save_results(identity)

    return identity


def load_saved_results():
    """Load saved Google Lens results for standalone testing."""

    if not RAW_RESULTS_FILE.exists():
        raise FileNotFoundError(
            f"Google Lens results not found:\n"
            f"{RAW_RESULTS_FILE}"
        )

    with open(
        RAW_RESULTS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print("\n" + "=" * 60)
    print("PRODUCT IDENTITY EXTRACTION")
    print("=" * 60)

    results = load_saved_results()

    identity = extract_product_identity(
        results
    )

    print("\n" + "=" * 60)
    print("PRODUCT IDENTIFICATION")
    print("=" * 60)

    print(
        f"\nSuggested query: "
        f"{identity['suggested_query']}"
    )

    print(
        f"Confidence: "
        f"{identity['confidence']}"
    )


if __name__ == "__main__":
    main()