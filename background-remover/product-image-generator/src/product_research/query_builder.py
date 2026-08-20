from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "output"
    / "search_results"
)

ANALYSIS_FILE = (
    PROJECT_ROOT
    / "output"
    / "product_research"
    / "image_analysis.json"
)

IDENTITY_FILE = (
    RESULTS_DIR
    / "product_candidates.json"
)

OUTPUT_FILE = (
    RESULTS_DIR
    / "final_search_query.json"
)


def load_json(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found:\n{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def clean_text(value):
    if not value:
        return ""

    return str(value).strip()


def build_query(image_analysis, lens_identity):
    query_parts = []

    # Priority 1: Brand
    brand = clean_text(
        image_analysis.get("possible_brand")
    )

    if brand:
        query_parts.append(brand)

    # Priority 2: Google Lens identity
    suggested_query = clean_text(
        lens_identity.get("suggested_query")
    )

    if suggested_query:
        # Avoid repeating brand words
        brand_words = {
            word.lower()
            for word in brand.split()
        }

        identity_words = [
            word
            for word in suggested_query.split()
            if word.lower() not in brand_words
        ]

        query_parts.extend(identity_words)

    # Priority 3: Material
    material = clean_text(
        image_analysis.get("material")
    ).lower()

    if "suede" in material:
        query_parts.append("suede")
    elif "leather" in material:
        query_parts.append("leather")

    # Priority 4: Color
    color = clean_text(
        image_analysis.get("primary_color")
    )

    if color:
        query_parts.append(color)

    # Remove duplicates
    final_words = []
    seen = set()

    for word in query_parts:
        normalized = word.lower()

        if normalized not in seen:
            seen.add(normalized)
            final_words.append(word)

    return " ".join(final_words)


def save_query(query, image_analysis, lens_identity):
    output = {
        "final_query": query,
        "sources": {
            "ai_brand": image_analysis.get("possible_brand"),
            "ai_product_type": image_analysis.get("product_type"),
            "ai_material": image_analysis.get("material"),
            "ai_color": image_analysis.get("primary_color"),
            "google_lens_query": lens_identity.get("suggested_query"),
        },
    }

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
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output


def build_product_query():
    print("\n" + "=" * 60)
    print("PRODUCT QUERY BUILDER")
    print("=" * 60)

    print("\nLoading AI image analysis...")
    image_analysis = load_json(ANALYSIS_FILE)

    print("Loading Google Lens identity...")
    lens_identity = load_json(IDENTITY_FILE)

    print("\nBuilding combined search query...")
    query = build_query(image_analysis, lens_identity)

    result = save_query(
        query,
        image_analysis,
        lens_identity
    )

    print("\n" + "=" * 60)
    print("FINAL SEARCH QUERY")
    print("=" * 60)

    print(f"\nQuery:\n{query}")
    print(f"\nSaved:\n{OUTPUT_FILE}")

    return result


if __name__ == "__main__":
    build_product_query()