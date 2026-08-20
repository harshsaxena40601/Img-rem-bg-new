from pathlib import Path
import json
from io import BytesIO
import requests

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_DIR = PROJECT_ROOT / "input" / "products"
RESULTS_DIR = PROJECT_ROOT / "output" / "search_results"

PRODUCTS_FILE = RESULTS_DIR / "google_products.json"
OUTPUT_FILE = RESULTS_DIR / "fast_filtered_candidates.json"

MODEL_NAME = "openai/clip-vit-base-patch32"


def find_product_image():
    extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    images = [
        file
        for file in PRODUCT_DIR.iterdir()
        if file.suffix.lower() in extensions
    ]

    if not images:
        raise FileNotFoundError("No product image found.")

    return images[0]


def load_products():
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def download_image(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    return Image.open(BytesIO(response.content)).convert("RGB")


def load_clip():
    print("\nLoading CLIP model...")

    model = CLIPModel.from_pretrained(MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model.eval()

    print("CLIP model loaded.")
    return model, processor


def get_embedding(image, model, processor):
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model.vision_model(pixel_values=inputs["pixel_values"])
        features = outputs.pooler_output
        features = model.visual_projection(features)

    features = features / features.norm(p=2, dim=-1, keepdim=True)
    return features


def calculate_similarity(reference_embedding, candidate_embedding):
    similarity = torch.matmul(reference_embedding, candidate_embedding.T)
    return float(similarity.item())


def fast_filter():
    print("\n" + "=" * 60)
    print("FAST CANDIDATE FILTERING")
    print("=" * 60)

    product_path = find_product_image()

    print(f"\nOriginal product:\n{product_path.name}")

    original_image = Image.open(product_path).convert("RGB")
    products_data = load_products()
    products = products_data.get("shopping_results", [])

    print(f"\nCandidate products: {len(products)}")

    model, processor = load_clip()

    print("\nCreating reference embedding...")
    reference_embedding = get_embedding(original_image, model, processor)

    results = []

    print("\nComparing candidate images...")
    for index, product in enumerate(products, start=1):
        title = product.get("title", "Unknown")
        thumbnail_url = product.get("thumbnail")

        print(f"\n[{index}/{len(products)}] {title}")

        if not thumbnail_url:
            print("No thumbnail. Skipping.")
            continue

        try:
            candidate_image = download_image(thumbnail_url)
            candidate_embedding = get_embedding(candidate_image, model, processor)

            similarity = calculate_similarity(
                reference_embedding, candidate_embedding
            )

            score = round(similarity * 100, 2)
            print(f"Visual similarity: {score}%")

            results.append({
                "position": product.get("position", index),
                "title": title,
                "source": product.get("source"),
                "price": product.get("price"),
                "thumbnail": thumbnail_url,
                "product_link": (
                    product.get("product_link")
                    or product.get("link")
                ),
                "product_id": product.get("product_id"),
                "immersive_product_page_token": product.get(
                    "immersive_product_page_token"
                ),
                "serpapi_immersive_product_api": product.get(
                    "serpapi_immersive_product_api"
                ),
                "visual_similarity": score,
            })

        except Exception as error:
            print(f"Failed: {error}")

    results.sort(key=lambda item: item["visual_similarity"], reverse=True)
    top_candidates = results[:10]

    output = {
        "reference_image": product_path.name,
        "total_candidates": len(products),
        "filtered_count": len(top_candidates),
        "candidates": top_candidates,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("FILTERING COMPLETE")
    print("=" * 60)

    print(f"\nTOP {len(top_candidates)} VISUAL MATCHES:")
    for index, item in enumerate(top_candidates, start=1):
        print(f"\n{index}. {item['title']}")
        print(f"   Similarity: {item['visual_similarity']}%")
        print(f"   Source: {item['source']}")

    print(f"\nSaved:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    fast_filter()