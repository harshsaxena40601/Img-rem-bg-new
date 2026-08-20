from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ==========================================================
# INPUT FILES
# ==========================================================

ANALYSIS_FILE = (
    PROJECT_ROOT
    / "output"
    / "product_research"
    / "image_analysis.json"
)

FINAL_MATCH_FILE = (
    PROJECT_ROOT
    / "output"
    / "product_brain"
    / "final_match.json"
)

LINK_RESULT_FILE = (
    PROJECT_ROOT
    / "output"
    / "product_research"
    / "product_link_result.json"
)


# ==========================================================
# OUTPUT
# ==========================================================

OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
    / "product_profile"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "product_profile.json"
)


# ==========================================================
# JSON HELPERS
# ==========================================================

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


def save_json(data):

    OUTPUT_DIR.mkdir(
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

    print("\nSaved:")
    print(OUTPUT_FILE)


# ==========================================================
# DATA EXTRACTION
# ==========================================================

def get_matched_product(final_match):
    """
    Get the winning product.

    Current pipeline uses:
    matched_product

    Future compatibility:
    selected_candidate
    """

    return (
        final_match.get("matched_product")
        or final_match.get("selected_candidate")
        or {}
    )


def get_primary_product_url(offers):
    """
    Select the first valid seller URL.
    """

    for offer in offers:

        product_url = offer.get(
            "product_url"
        )

        if product_url:
            return product_url

    return None


def build_product_name(
    image_analysis,
    matched_product
):
    """
    Prefer verified product title.
    Fall back to AI analysis.
    """

    title = matched_product.get(
        "title"
    )

    if title:
        return title

    brand = image_analysis.get(
        "possible_brand",
        ""
    )

    product_type = image_analysis.get(
        "product_type",
        ""
    )

    return f"{brand} {product_type}".strip()


# ==========================================================
# BUILD PRODUCT PROFILE
# ==========================================================

def build_product_profile():

    print("\n" + "=" * 60)
    print("PRODUCT PROFILE BUILDER")
    print("=" * 60)

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    print("\nLoading image analysis...")

    image_analysis = load_json(
        ANALYSIS_FILE
    )

    print("Loading final match...")

    final_match = load_json(
        FINAL_MATCH_FILE
    )

    print("Loading product link result...")

    link_result = load_json(
        LINK_RESULT_FILE
    )

    # ------------------------------------------------------
    # EXTRACT DATA
    # ------------------------------------------------------

    matched_product = get_matched_product(
        final_match
    )

    offers = link_result.get(
        "offers",
        []
    )

    primary_product_url = get_primary_product_url(
        offers
    )

    product_name = build_product_name(
        image_analysis,
        matched_product
    )

    # ------------------------------------------------------
    # BUILD COMPLETE PROFILE
    # ------------------------------------------------------

    profile = {

        # ==================================================
        # PRODUCT IDENTITY
        # ==================================================

        "product": {

            "name": product_name,

            "brand": image_analysis.get(
                "possible_brand"
            ),

            "category": image_analysis.get(
                "product_type"
            ),

            "material": image_analysis.get(
                "material"
            ),

            "primary_color": image_analysis.get(
                "primary_color"
            ),

            "secondary_colors": image_analysis.get(
                "secondary_colors",
                []
            ),

            "texture": image_analysis.get(
                "pattern_or_texture"
            ),

            "shape": image_analysis.get(
                "shape"
            ),

            "size_clues": image_analysis.get(
                "size_clues"
            ),

            "handles_or_straps": image_analysis.get(
                "handle_or_strap"
            ),

            "hardware": image_analysis.get(
                "hardware"
            ),
        },


        # ==================================================
        # VISUAL DETAILS
        # ==================================================

        "distinctive_features": image_analysis.get(
            "distinctive_features",
            []
        ),

        "search_keywords": image_analysis.get(
            "search_keywords",
            []
        ),


        # ==================================================
        # VERIFIED MATCH
        # ==================================================

        "verified_match": {

            "status": final_match.get(
                "decision"
            ),

            "confidence": final_match.get(
                "confidence"
            ),

            "candidate_number": final_match.get(
                "candidate_number"
            ),

            "reason": final_match.get(
                "reason"
            ),

            "visual_similarity": matched_product.get(
                "visual_similarity"
            ),
        },


        # ==================================================
        # MATCHED GOOGLE PRODUCT
        # ==================================================

        "matched_product": {

            "position": matched_product.get(
                "position"
            ),

            "title": matched_product.get(
                "title"
            ),

            "source": matched_product.get(
                "source"
            ),

            "price": matched_product.get(
                "price"
            ),

            "thumbnail": matched_product.get(
                "thumbnail"
            ),

            "google_product_link": matched_product.get(
                "product_link"
            ),

            "product_id": matched_product.get(
                "product_id"
            ),

            "immersive_product_page_token": (
                matched_product.get(
                    "immersive_product_page_token"
                )
            ),
        },


        # ==================================================
        # VERIFIED SELLER INFORMATION
        # ==================================================

        "seller_information": {

            "primary_product_url": (
                primary_product_url
            ),

            "total_offers": link_result.get(
                "total_offers",
                len(offers)
            ),

            "offers": offers,
        },
    }


    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    save_json(profile)

    print("\n" + "=" * 60)
    print("PRODUCT PROFILE CREATED")
    print("=" * 60)

    print(
        json.dumps(
            profile,
            indent=4,
            ensure_ascii=False
        )
    )

    return profile


# ==========================================================
# MAIN
# ==========================================================

def main():

    return build_product_profile()


if __name__ == "__main__":
    main()