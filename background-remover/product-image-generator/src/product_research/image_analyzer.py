from pathlib import Path
import json
from PIL import Image

from ai.manager import generate_ai


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_DIR = PROJECT_ROOT / "input" / "products"
OUTPUT_DIR = PROJECT_ROOT / "output" / "product_research"
OUTPUT_FILE = OUTPUT_DIR / "image_analysis.json"


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


def analyze_image(image_path):
    print("\nLoading product image...")

    image = Image.open(image_path).convert("RGB")

    prompt = """
You are a product visual analysis system.

Analyze ONLY what is visually visible
in the product image.

Do NOT guess details that cannot be seen.

Return ONLY valid JSON.

Use this structure:

{
    "product_type": "",
    "possible_brand": "",
    "brand_confidence": 0.0,
    "material": "",
    "primary_color": "",
    "secondary_colors": [],
    "pattern_or_texture": "",
    "shape": "",
    "size_clues": "",
    "handle_or_strap": "",
    "hardware": "",
    "visible_logo_or_text": "",
    "distinctive_features": [],
    "search_keywords": []
}

Rules:

1. Describe visible facts.
2. If something is uncertain, say "unknown".
3. Do not identify an exact product model.
4. Do not invent measurements.
5. Focus strongly on features useful
   for distinguishing this product
   from similar products.
6. search_keywords should contain
   useful product search terms.
7. brand_confidence must be a number between 0.0 and 1.0.

Examples:
0.0 = no confidence
0.5 = moderate confidence
0.9 = high confidence
1.0 = certain

Never return percentages, integers from 1 to 10, strings, or any other scale.
"""

    # ==================================================
    # SEND IMAGE TO CENTRAL AI MANAGER
    # ==================================================
    print("\nSending image to AI...")

    result = generate_ai(
        contents=[
            prompt,
            image,
        ],
        task_type="vision",
    )

    if not result["success"]:
        raise RuntimeError(result["error"])

    response_text = result["text"]

    print("\nAI analysis received.")
    print(f"Provider used: {result['provider']}")
    print(f"Model used: {result['model']}")
    print(f"Fallback used: {result['fallback_used']}")

    return response_text


def clean_json(text):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text[:-3]
    elif text.startswith("```"):
        text = text.replace("```", "", 1)
        if text.endswith("```"):
            text = text[:-3]

    return text.strip()


def validate_and_normalize_analysis(analysis):
    """
    Validates and normalizes brand_confidence to ensure it is always
    a float strictly between 0.0 and 1.0.
    """
    confidence = analysis.get("brand_confidence", 0.0)

    try:
        confidence = float(confidence)

        # Normalize if the model accidentally returned 0-100 scale
        if 1.0 < confidence <= 100.0:
            confidence = confidence / 100.0

        # Clamp between 0.0 and 1.0
        confidence = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        confidence = 0.0

    analysis["brand_confidence"] = round(confidence, 2)
    return analysis


def parse_response(raw_response):
    """
    Cleans, parses, and validates the model response into structured data.
    """
    if raw_response is None:
        return None

    print("\nRAW RESPONSE:")
    print(raw_response)

    cleaned_response = clean_json(raw_response)

    try:
        analysis = json.loads(cleaned_response)
    except json.JSONDecodeError:
        raise ValueError("AI did not return valid JSON.")

    return validate_and_normalize_analysis(analysis)


def save_analysis(analysis):
    if analysis is None:
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(analysis, file, indent=4, ensure_ascii=False)

    print(f"\nAnalysis saved:\n{OUTPUT_FILE}")


def analyze_product_image():
    """
    Analyze the product image and return structured AI data.
    """
    print("\n" + "=" * 60)
    print("AI PRODUCT IMAGE ANALYZER")
    print("=" * 60)

    image_path = find_product_image()
    print(f"\nProduct image:\n{image_path.name}")

    try:
        raw_response = analyze_image(image_path)
    except Exception as error:
        print(f"\nAI image analysis failed: {error}")
        print("The main pipeline can continue using Google Lens.")
        return None

    analysis = parse_response(raw_response)
    save_analysis(analysis)

    return analysis


if __name__ == "__main__":
    analysis = analyze_product_image()

    if analysis:
        print("\n" + "=" * 60)
        print("IMAGE ANALYSIS COMPLETE")
        print("=" * 60)

        print(
            json.dumps(
                analysis,
                indent=4,
                ensure_ascii=False,
            )
        )