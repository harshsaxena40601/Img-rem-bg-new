from upload_image import find_product_image, upload_product_image
from search_product import search_product
from extract_results import extract_product_identity
from google_products import search_google_products, save_results


def main():

    print("\n" + "=" * 60)
    print("FULL PRODUCT RESEARCH PIPELINE")
    print("=" * 60)

    # STEP 1
    print("\nSTEP 1: Finding product image...")

    image_path = find_product_image()

    print(f"Product found: {image_path.name}")

    # STEP 2
    print("\nSTEP 2: Uploading to Cloudinary...")

    upload_result = upload_product_image(image_path)

    image_url = upload_result["secure_url"]

    print("\nCloudinary upload successful.")
    print(f"Image URL: {image_url}")

    # STEP 3
    print("\nSTEP 3: Searching Google Lens...")

    lens_results = search_product(image_url)

    visual_matches = lens_results.get(
        "visual_matches",
        []
    )

    print(
        f"\nVisual matches found: "
        f"{len(visual_matches)}"
    )

    # STEP 4
    print("\nSTEP 4: Identifying product...")

    identity = extract_product_identity(
        lens_results
    )

    query = identity["suggested_query"]

    print(f"\nIdentified query: {query}")
    print(
        f"Confidence: "
        f"{identity['confidence']}"
    )

    # STEP 5
    print("\nSTEP 5: Searching Google Shopping...")

    shopping_results = search_google_products(
        query
    )

    save_results(shopping_results)

    products = shopping_results.get(
        "shopping_results",
        []
    )

    # FINAL SUMMARY
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    print(f"\nProduct image: {image_path.name}")
    print(f"Cloudinary URL: {image_url}")

    print(
        f"Visual matches: "
        f"{len(visual_matches)}"
    )

    print(f"Product query: {query}")

    print(
        f"Identification confidence: "
        f"{identity['confidence']}"
    )

    print(
        f"Shopping products found: "
        f"{len(products)}"
    )

    print("\nTop 5 shopping results:")

    for index, product in enumerate(
        products[:5],
        start=1
    ):
        print(f"\n{index}. {product.get('title')}")
        print(f"   Source: {product.get('source')}")
        print(f"   Price: {product.get('price')}")


if __name__ == "__main__":
    main()