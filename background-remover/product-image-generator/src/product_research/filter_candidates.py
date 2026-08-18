import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

VISUAL_FILE = (
    BASE_DIR
    / "output"
    / "search_results"
    / "visual_verification.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "search_results"
    / "filtered_candidates.json"
)


# Variants that are clearly different products
REJECT_KEYWORDS = [
    "bucket",
    "clutch",
    "wallet",
    "phone pouch",
    "pouch",
    "voyager",
    "crossbody",
    "cross-body",
    "cross body",
    "chain bag",
    "chain",
]


# Features expected in the product family
PRODUCT_KEYWORDS = [
    "bottega",
    "veneta",
    "andiamo",
]


# These words indicate a structured handbag / tote
STRUCTURE_KEYWORDS = [
    "handbag",
    "tote",
    "top handle",
    "shoulder bag",
    "leather",
    "intrecciato",
]


def load_json(file_path):

    if not file_path.exists():
        print(f"\nERROR: File not found:\n{file_path}")
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text):

    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)

    return " ".join(text.split())


def contains_keyword(text, keyword):

    text = normalize(text)
    keyword = normalize(keyword)

    return keyword in text


def analyze_candidate(candidate):

    title = candidate.get("title", "")
    source = candidate.get("source", "")
    similarity = candidate.get("visual_similarity", 0)

    normalized_title = normalize(title)

    reasons = []
    rejected_features = []
    matched_features = []

    # -------------------------
    # PRODUCT IDENTITY
    # -------------------------

    identity_matches = 0

    for keyword in PRODUCT_KEYWORDS:

        if contains_keyword(normalized_title, keyword):

            identity_matches += 1
            matched_features.append(keyword)

    identity_score = (
        identity_matches
        / len(PRODUCT_KEYWORDS)
    ) * 100

    # -------------------------
    # REJECT WRONG VARIANTS
    # -------------------------

    for keyword in REJECT_KEYWORDS:

        if contains_keyword(normalized_title, keyword):

            rejected_features.append(keyword)

    # -------------------------
    # STRUCTURAL PRODUCT WORDS
    # -------------------------

    structure_matches = 0

    for keyword in STRUCTURE_KEYWORDS:

        if contains_keyword(normalized_title, keyword):

            structure_matches += 1
            matched_features.append(keyword)

    structure_score = min(
        100,
        structure_matches * 25
    )

    # -------------------------
    # VARIANT PENALTY
    # -------------------------

    variant_penalty = len(
        rejected_features
    ) * 25

    # -------------------------
    # FINAL SCORE
    # -------------------------

    final_score = (
        similarity * 0.55
        + identity_score * 0.30
        + structure_score * 0.15
        - variant_penalty
    )

    final_score = max(
        0,
        min(100, final_score)
    )

    # -------------------------
    # DECISION
    # -------------------------

    decision = "review"

    if rejected_features:

        decision = "reject"

        reasons.append(
            "Wrong product variant detected: "
            + ", ".join(rejected_features)
        )

    elif final_score >= 80:

        decision = "keep"

        reasons.append(
            "Strong visual and product identity match"
        )

    elif final_score >= 60:

        decision = "review"

        reasons.append(
            "Possible match but needs further verification"
        )

    else:

        decision = "reject"

        reasons.append(
            "Low combined confidence"
        )

    return {
        "position": candidate.get("position"),
        "title": title,
        "source": source,
        "price": candidate.get("price"),
        "thumbnail": candidate.get("thumbnail"),
        "visual_similarity": similarity,
        "identity_score": round(identity_score, 2),
        "structure_score": round(structure_score, 2),
        "variant_penalty": variant_penalty,
        "final_score": round(final_score, 2),
        "decision": decision,
        "matched_features": matched_features,
        "rejected_features": rejected_features,
        "reasons": reasons
    }


def filter_candidates():

    print("\n" + "=" * 60)
    print("PRODUCT CANDIDATE FILTERING")
    print("=" * 60)

    data = load_json(VISUAL_FILE)

    if not data:
        return

    candidates = data.get(
        "verified_results",
        []
    )

    print(
        f"\nCandidates found: "
        f"{len(candidates)}"
    )

    results = []

    for candidate in candidates:

        analyzed = analyze_candidate(candidate)

        results.append(analyzed)

    # Sort by final score
    results.sort(
        key=lambda item: item["final_score"],
        reverse=True
    )

    kept = [
        item
        for item in results
        if item["decision"] == "keep"
    ]

    review = [
        item
        for item in results
        if item["decision"] == "review"
    ]

    rejected = [
        item
        for item in results
        if item["decision"] == "reject"
    ]

    print("\n" + "=" * 60)
    print("FILTERING RESULTS")
    print("=" * 60)

    print(f"\nKEEP: {len(kept)}")
    print(f"REVIEW: {len(review)}")
    print(f"REJECT: {len(rejected)}")

    print("\n" + "-" * 60)
    print("KEPT CANDIDATES")
    print("-" * 60)

    for index, item in enumerate(kept, start=1):

        print(
            f"\n{index}. "
            f"{item['title']}"
        )

        print(
            f"   Visual: "
            f"{item['visual_similarity']}%"
        )

        print(
            f"   Identity: "
            f"{item['identity_score']}%"
        )

        print(
            f"   Structure: "
            f"{item['structure_score']}%"
        )

        print(
            f"   Final Score: "
            f"{item['final_score']}%"
        )

    output = {
        "total_candidates": len(results),
        "keep_count": len(kept),
        "review_count": len(review),
        "reject_count": len(rejected),
        "kept_candidates": kept,
        "review_candidates": review,
        "rejected_candidates": rejected
    }

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

    print("\n" + "=" * 60)
    print("FILTERING COMPLETE")
    print("=" * 60)

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    filter_candidates()