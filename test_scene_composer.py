from pathlib import Path

from modules.scene_composer import SceneComposer


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

IMAGE_FOLDER = (
    BASE_DIR
    / "assets"
    / "images"
)

OUTPUT_FOLDER = (
    BASE_DIR
    / "output"
    / "chapter_001"
    / "verse_001"
)

# =========================================================
# YOUR SHLOKA
# =========================================================

SHLOKA = (
    "धृतराष्ट्र उवाच । "
    "धर्मक्षेत्रे कुरुक्षेत्रे "
    "समवेता युयुत्सवः । "
    "मामकाः पाण्डवाश्चैव "
    "किमकुर्वत सञ्जय ॥"
)

# =========================================================
# FIXED SCENE IMAGES
# =========================================================

scene_images = [

    IMAGE_FOLDER
    / "Scene1-Starting.jpeg",

    IMAGE_FOLDER
    / "Scene2-KrishnatoArjun.jpeg",

    IMAGE_FOLDER
    / "Scene3-ArjuntoKrishna.jpeg",

    IMAGE_FOLDER
    / "Scene4-closing.jpeg",

]

# =========================================================
# CHECK IMAGES
# =========================================================

print()
print("=" * 70)
print("SCENE COMPOSER TEST")
print("=" * 70)

for index, image in enumerate(
    scene_images,
    start=1,
):

    print(
        f"Scene {index}: {image}"
    )

    if not image.exists():

        raise FileNotFoundError(
            f"Image not found:\n{image}"
        )

# =========================================================
# CREATE COMPOSER
# =========================================================

composer = SceneComposer()

# =========================================================
# COMPOSE
# =========================================================

results = composer.compose_scenes(

    scene_images=scene_images,

    output_folder=OUTPUT_FOLDER,

    shloka=SHLOKA,

    chapter=1,

    verse=1,

)

# =========================================================
# RESULTS
# =========================================================

print()
print("=" * 70)
print("COMPOSITION COMPLETE")
print("=" * 70)

for index, result in enumerate(
    results,
    start=1,
):

    print(
        f"Scene {index}:"
    )

    print(
        f"  {result}"
    )

print()
print("Open the generated PNG files and check the design.")
print()