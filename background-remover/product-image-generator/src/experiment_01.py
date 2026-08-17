from pathlib import Path
from PIL import Image


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCT_DIR = BASE_DIR / "input" / "products"
TEMPLATE_DIR = BASE_DIR / "input" / "templates"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==================================================
# FIND FILES
# ==================================================

product_files = list(PRODUCT_DIR.glob("*.png"))
template_files = (
    list(TEMPLATE_DIR.glob("*.jpg"))
    + list(TEMPLATE_DIR.glob("*.jpeg"))
    + list(TEMPLATE_DIR.glob("*.png"))
)

if not product_files:
    raise FileNotFoundError("No PNG product found in input/products")

if not template_files:
    raise FileNotFoundError("No template image found in input/templates")


product_path = product_files[0]
template_path = template_files[0]


# ==================================================
# LOAD IMAGES
# ==================================================

print("\nLOADING IMAGES...\n")

product = Image.open(product_path).convert("RGBA")
template = Image.open(template_path).convert("RGBA")

print(f"Product:  {product_path.name}")
print(f"Size:     {product.size}")

print()

print(f"Template: {template_path.name}")
print(f"Size:     {template.size}")


# ==================================================
# PRODUCT SIZE
# ==================================================

# Change this later after checking the output
PRODUCT_WIDTH = 380

original_width, original_height = product.size

scale = PRODUCT_WIDTH / original_width

product_height = int(original_height * scale)

product = product.resize(
    (PRODUCT_WIDTH, product_height),
    Image.Resampling.LANCZOS
)


# ==================================================
# PRODUCT POSITION
# ==================================================

# Change these values to move the bag
X = 356
Y = 526


# ==================================================
# COMPOSITE
# ==================================================

result = template.copy()

result.alpha_composite(product, (X, Y))


# ==================================================
# SAVE
# ==================================================

output_path = OUTPUT_DIR / "experiment_01.png"

result.save(output_path)

print("\nCOMPOSITE COMPLETE\n")

print(f"Product size: {product.size}")
print(f"Position:     {X}, {Y}")
print(f"Output:       {output_path}")
