import json

from image_analyzer import analyze_product_image
from upload_image import (
    find_product_image,
    upload_product_image,
)
from search_product import search_product
from extract_results import extract_product_identity
from query_builder import build_product_query
from google_products import (
    search_google_products,
    save_results,
)
from fast_filter import fast_filter
from product_brain import main as run_product_brain


def main():
    print("\n" + "=" * 70)
    print("PRODUCT RESEARCH PIPELINE")
    print("=" * 70)

    try:
        # ==================================================
        # STEP 1: AI IMAGE ANALYSIS
        # ==================================================
        print("\nSTEP 1: AI IMAGE ANALYSIS")

        image_analysis = analyze_product_image()
        print("\nImage analysis completed.")

        # ==================================================
        # STEP 2: UPLOAD PRODUCT IMAGE
        # ==================================================
        print("\nSTEP 2: UPLOADING PRODUCT IMAGE")

        image_path = find_product_image()
        upload_result = upload_product_image(image_path)
        image_url = upload_result["secure_url"]

        # ==================================================
        # STEP 3: GOOGLE LENS SEARCH
        # ==================================================
        print("\nSTEP 3: GOOGLE LENS SEARCH")

        lens_results = search_product(image_url)

        # ==================================================
        # STEP 4: PRODUCT IDENTITY EXTRACTION
        # ==================================================
        print("\nSTEP 4: PRODUCT IDENTITY EXTRACTION")

        identity = extract_product_identity(lens_results)

        # ==================================================
        # STEP 5: AI + GOOGLE LENS QUERY BUILDER
        # ==================================================
        print("\nSTEP 5: BUILDING PRODUCT SEARCH QUERY")

        query_result = build_product_query()
        query = query_result["final_query"]

        print(f"\nFinal search query:\n{query}")

        # ==================================================
        # STEP 6: GOOGLE SHOPPING SEARCH
        # ==================================================
        print("\nSTEP 6: GOOGLE SHOPPING SEARCH")

        shopping_results = search_google_products(query)
        save_results(shopping_results)

        # ==================================================
        # STEP 7: FAST VISUAL FILTER
        # ==================================================
        print("\nSTEP 7: FAST VISUAL FILTER")

        fast_filter()

        # ==================================================
        # STEP 8: PRODUCT BRAIN
        # ==================================================
        print("\nSTEP 8: PRODUCT BRAIN")

        final_result = run_product_brain()

        # ==================================================
        # PIPELINE COMPLETE
        # ==================================================
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)

        if final_result:
            print(
                json.dumps(
                    final_result,
                    indent=4,
                    ensure_ascii=False,
                )
            )

    except Exception as error:
        print("\n" + "=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)

        print(
            f"\n{type(error).__name__}: "
            f"{error}"
        )


if __name__ == "__main__":
    main()