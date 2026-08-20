from pathlib import Path
import json
from io import BytesIO
import requests
from PIL import Image, ImageDraw

from ai.manager import generate_ai
from ai.json_helper import extract_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_DIR = PROJECT_ROOT / "input" / "products"
RESULTS_DIR = PROJECT_ROOT / "output" / "search_results"
BRAIN_DIR = PROJECT_ROOT / "output" / "product_brain"

IMAGE_ANALYSIS_FILE = (
    PROJECT_ROOT
    / "output"
    / "product_research"
    / "image_analysis.json"
)

INPUT_FILE = RESULTS_DIR / "fast_filtered_candidates.json"
CONTACT_SHEET_FILE = BRAIN_DIR / "candidate_comparison.jpg"
FINAL_RESULT_FILE = BRAIN_DIR / "final_match.json"


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


def load_image_analysis():
    if not IMAGE_ANALYSIS_FILE.exists():
        print("\nWarning: image_analysis.json not found.")
        return {}

    with open(IMAGE_ANALYSIS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_candidate_information(candidates):
    information = []

    for index, candidate in enumerate(candidates, start=1):
        information.append({
            "candidate_number": index,
            "title": candidate.get("title", "Unknown"),
            "source": candidate.get("source", "Unknown"),
            "price": candidate.get("price", "Unknown"),
            "clip_similarity": candidate.get("visual_similarity", 0),
        })

    return information


def load_candidates():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fast filter results not found:\n{INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    candidates = data.get("candidates", [])

    if not candidates:
        raise ValueError("No candidates found.")

    return candidates


def download_image(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return Image.open(BytesIO(response.content)).convert("RGB")


def resize_image(image, size=(300, 300)):
    image.thumbnail(size, Image.LANCZOS)

    canvas = Image.new("RGB", size, "white")
    x = (size[0] - image.width) // 2
    y = (size[1] - image.height) // 2

    canvas.paste(image, (x, y))
    return canvas


def create_contact_sheet(reference_image, candidates):
    cell_width = 300
    cell_height = 360
    columns = 3

    total_items = len(candidates) + 1
    rows = (total_items + columns - 1) // columns

    sheet_width = columns * cell_width
    sheet_height = rows * cell_height

    sheet = Image.new("RGB", (sheet_width, sheet_height), "white")
    draw = ImageDraw.Draw(sheet)

    # Reference product
    reference = resize_image(reference_image.copy())
    sheet.paste(reference, (0, 0))
    draw.text((10, 310), "REFERENCE", fill="black")

    # Candidate products
    for index, candidate in enumerate(candidates, start=1):
        position = index
        row = position // columns
        column = position % columns

        x = column * cell_width
        y = row * cell_height

        try:
            image = download_image(candidate["thumbnail"])
            image = resize_image(image)

            sheet.paste(image, (x, y))

            label = f"CANDIDATE {index}"
            draw.text((x + 10, y + 310), label, fill="black")

            score = candidate.get("visual_similarity", 0)
            draw.text((x + 10, y + 330), f"CLIP: {score}%", fill="black")

        except Exception as error:
            print(f"Failed to load candidate {index}: {error}")

    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET_FILE)

    return CONTACT_SHEET_FILE


def select_top_candidates(comparison_image, reference_analysis, candidate_information):
    print("\nRunning Round 1 candidate selection...")

    prompt = f"""
You are an expert visual product verification AI.

Your task is ROUND 1 SCREENING:
Identify the TOP 3 most promising candidate products that could be the EXACT SAME product as the REFERENCE image.

REFERENCE PRODUCT METADATA:
{json.dumps(reference_analysis, indent=2)}

CANDIDATES METADATA:
{json.dumps(candidate_information, indent=2)}

RULES:
1. Compare overall shape, proportions, handles, straps, materials, hardware, closures, and structural details.
2. Filter out products that clearly have a different structure, geometry, handle setup, or product variant.
3. Select EXACTLY 3 candidate numbers that have the highest probability of being an exact match.

Return ONLY valid JSON in this format:
{{
    "top_candidates": [1, 2, 3],
    "reason": "Brief explanation of why these 3 candidates were selected."
}}

Do not return markdown or explanations outside the JSON.
"""

    result = generate_ai(
        contents=[
            prompt,
            comparison_image,
        ],
        task_type="vision",
    )

    if not result["success"]:
        raise RuntimeError(
            f"Round 1 AI request failed:\n{result['error']}"
        )

    print(f"\nProvider used: {result['provider']}")
    print(f"Model used: {result['model']}")
    print(f"Fallback used: {result['fallback_used']}")

    try:
        data = extract_json(result["text"])
        top_candidates = data.get("top_candidates", [])

        if not isinstance(top_candidates, list) or len(top_candidates) != 3:
            raise ValueError("AI did not return exactly 3 candidates.")

        top_candidates = list(dict.fromkeys(top_candidates))

        if len(top_candidates) != 3:
            raise ValueError("Duplicate candidate numbers returned.")

        for number in top_candidates:
            if (
                not isinstance(number, int)
                or number < 1
                or number > len(candidate_information)
            ):
                raise ValueError(f"Invalid candidate number: {number}")

        return {
            "success": True,
            "top_candidates": top_candidates,
            "reason": data.get("reason", ""),
        }

    except Exception as error:
        print("\nFailed to parse Round 1 response.")
        print(f"{type(error).__name__}: {error}")

        return {
            "success": False,
            "top_candidates": [],
            "reason": str(error),
        }


def get_selected_candidates(candidates, selected_numbers):
    selected_candidates = []

    for number in selected_numbers:
        candidate = candidates[number - 1]
        selected_candidates.append({
            "candidate_number": number,
            **candidate,
        })

    return selected_candidates


def download_selected_images(selected_candidates):
    selected_images = []

    print("\nDownloading selected candidate images...")

    for candidate in selected_candidates:
        number = candidate["candidate_number"]
        print(f"Downloading candidate {number}...")

        try:
            image = download_image(candidate["thumbnail"])
            selected_images.append({
                "candidate_number": number,
                "image": image,
                "candidate": candidate,
            })
        except Exception as error:
            print(f"Failed to download candidate {number}: {error}")

    return selected_images


def build_round_two_information(selected_candidates):
    information = []

    for candidate in selected_candidates:
        information.append({
            "candidate_number": candidate.get("candidate_number"),
            "title": candidate.get("title", "Unknown"),
            "source": candidate.get("source", "Unknown"),
            "price": candidate.get("price", "Unknown"),
            "clip_similarity": candidate.get("visual_similarity", 0),
        })

    return information


def make_final_decision(
    reference_image,
    selected_images,
    reference_analysis,
    candidate_information,
):
    print("\nSending high-resolution candidates to Product Brain for final decision...")

    prompt = f"""
You are an expert product identification and verification AI.

Your task is ROUND 2 FINAL VERIFICATION:
Carefully compare the REFERENCE PRODUCT against the top selected candidate products.
Determine if ONE of these candidates is the EXACT SAME physical product model.

REFERENCE PRODUCT METADATA:
{json.dumps(reference_analysis, indent=2)}

CANDIDATES METADATA:
{json.dumps(candidate_information, indent=2)}

VERIFICATION RULES:
1. Compare physical details: shape, proportions, silhouette, handle/strap configuration, material texture, hardware, stitching, closures, and logos.
2. If one candidate is the exact same product, select its candidate number and provide a confidence score (0-100).
3. If no candidate is an exact match (e.g., different size, variation, or entirely different product), return NO_MATCH.

Return ONLY valid JSON in one of these structures:

Exact Match Found:
{{
    "decision": "MATCH",
    "candidate_number": 1,
    "confidence": 95,
    "reason": "Detailed explanation of visual match confirmation."
}}

No Exact Match:
{{
    "decision": "NO_MATCH",
    "candidate_number": null,
    "confidence": 90,
    "reason": "Detailed explanation of differences found across all candidates."
}}

Do not return markdown or text outside the JSON.
"""

    contents = [
        prompt,
        "REFERENCE PRODUCT IMAGE:",
        reference_image,
    ]

    for item in selected_images:
        cand_num = item["candidate_number"]
        title = item["candidate"].get("title", "Unknown")
        contents.append(f"CANDIDATE {cand_num}: {title}")
        contents.append(item["image"])

    result = generate_ai(
        contents=contents,
        task_type="vision",
    )

    if not result["success"]:
        raise RuntimeError(
            f"Round 2 AI request failed:\n{result['error']}"
        )

    print(f"\nProvider used: {result['provider']}")
    print(f"Model used: {result['model']}")
    print(f"Fallback used: {result['fallback_used']}")

    try:
        data = extract_json(result["text"])
        decision = data.get("decision")
        candidate_number = data.get("candidate_number")
        confidence = data.get("confidence", 0)
        reason = data.get("reason", "")

        if decision not in ["MATCH", "NO_MATCH"]:
            raise ValueError("Invalid decision returned.")

        selected_numbers = [
            item["candidate_number"] for item in selected_images
        ]

        if decision == "MATCH":
            if candidate_number not in selected_numbers:
                raise ValueError(
                    "AI selected a candidate outside the Round 1 selection."
                )

        if decision == "NO_MATCH":
            candidate_number = None

        return {
            "success": True,
            "decision": decision,
            "candidate_number": candidate_number,
            "confidence": confidence,
            "reason": reason,
        }

    except Exception as error:
        print("\nFailed to parse final brain response.")
        return {
            "success": False,
            "decision": "ERROR",
            "candidate_number": None,
            "confidence": 0,
            "reason": str(error),
        }


def save_final_result(result, candidates):
    candidate_number = result.get("candidate_number")

    if (
        candidate_number
        and isinstance(candidate_number, int)
        and 1 <= candidate_number <= len(candidates)
    ):
        candidate = candidates[candidate_number - 1]
        result["matched_product"] = {
            "position": candidate.get("position"),
            "title": candidate.get("title"),
            "source": candidate.get("source"),
            "price": candidate.get("price"),
            "thumbnail": candidate.get("thumbnail"),
            "product_link": candidate.get("product_link"),
            "product_id": candidate.get("product_id"),
            "immersive_product_page_token": candidate.get(
                "immersive_product_page_token"
            ),
            "visual_similarity": candidate.get("visual_similarity"),
        }
    else:
        result["matched_product"] = None

    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    with open(FINAL_RESULT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    return FINAL_RESULT_FILE


def main():
    print("\n" + "=" * 60)
    print("PRODUCT BRAIN")
    print("=" * 60)

    # STEP 1: Reference image
    print("\nLoading reference product...")
    product_path = find_product_image()
    reference_image = Image.open(product_path).convert("RGB")
    print(f"Reference: {product_path.name}")

    # STEP 2: Candidates & Metadata
    print("\nLoading Top 10 candidates...")
    candidates = load_candidates()
    print(f"Candidates: {len(candidates)}")

    print("\nLoading AI reference analysis...")
    reference_analysis = load_image_analysis()
    candidate_information = build_candidate_information(candidates)

    # STEP 3: Create comparison sheet
    print("\nCreating comparison sheet...")
    output_path = create_contact_sheet(reference_image, candidates)
    comparison_image = Image.open(output_path).convert("RGB")

    # STEP 4: Product Brain Round 1
    print("\n" + "=" * 60)
    print("PRODUCT BRAIN ROUND 1")
    print("=" * 60)

    selection_result = select_top_candidates(
        comparison_image,
        reference_analysis,
        candidate_information,
    )

    if not selection_result["success"]:
        print("\nROUND 1 FAILED")
        print(selection_result["reason"])
        return None

    print("\n" + "=" * 60)
    print("ROUND 1 COMPLETE")
    print("=" * 60)

    print("\nSelected candidates:")
    for number in selection_result["top_candidates"]:
        candidate = candidates[number - 1]
        print(f"\nCandidate {number}")
        print(f"Title: {candidate.get('title')}")
        print(f"CLIP similarity: {candidate.get('visual_similarity')}%")

    print(f"\nReason:\n{selection_result['reason']}")

    # STEP 5: Prepare Round 2
    selected_numbers = selection_result["top_candidates"]
    selected_candidates = get_selected_candidates(candidates, selected_numbers)
    selected_images = download_selected_images(selected_candidates)

    if not selected_images:
        print("\nNo selected candidate images could be downloaded.")
        return None

    round_two_information = build_round_two_information(selected_candidates)

    # STEP 6: Product Brain Round 2
    print("\n" + "=" * 60)
    print("PRODUCT BRAIN ROUND 2")
    print("=" * 60)

    final_result = make_final_decision(
        reference_image=reference_image,
        selected_images=selected_images,
        reference_analysis=reference_analysis,
        candidate_information=round_two_information,
    )

    final_output_path = save_final_result(final_result, candidates)

    print("\n" + "=" * 60)
    print("FINAL DECISION")
    print("=" * 60)

    print(f"\nDecision: {final_result.get('decision')}")
    print(f"Candidate Number: {final_result.get('candidate_number')}")
    print(f"Confidence: {final_result.get('confidence')}%")
    print(f"Reason: {final_result.get('reason')}")
    print(f"\nSaved:\n{final_output_path}")

    return final_result


if __name__ == "__main__":
    main()