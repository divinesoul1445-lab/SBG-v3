from pathlib import Path
import os
import urllib.request
import fal_client


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path("output/chapter_001/verse_001")

MODEL = "fal-ai/kling-video/v3/standard/image-to-video"


# ============================================================
# COMMON NEGATIVE PROMPT
# ============================================================

NEGATIVE_PROMPT = """
camera movement,
camera zoom,
camera pan,
camera rotation,
scene change,
new characters,
extra characters,
character duplication,
face distortion,
deformed face,
deformed hands,
extra fingers,
missing fingers,
extra limbs,
warped body,
changing clothes,
changing jewelry,
changing character identity,
changing environment,
large body movement,
fast movement,
walking,
fighting,
dramatic gestures,
exaggerated expression,
unnatural mouth movement,
lip distortion,
melting face,
flickering,
warping,
blurry face,
low quality
"""


# ============================================================
# SCENE PROMPTS
# ============================================================

SCENE_PROMPTS = {

    1: """
Animate the existing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
environment, composition, colors, lighting and overall
devotional visual style of the input image.

Krishna remains calm, peaceful and dignified.

Add very subtle natural facial movement and gentle blinking.

Krishna makes an extremely subtle natural movement,
as if peacefully preparing to share an important teaching.

Allow very slight natural movement in clothing and hair,
as if from a gentle breeze.

Maintain a serene divine atmosphere.

All movement must be slow, graceful, controlled and devotional.

The characters must remain in their original positions.

Do not change their appearance.

Do not add or remove characters.

Do not change the environment.

Do not change the camera angle.

Do not zoom.

Do not pan.

Do not rotate the camera.

Do not create dramatic action.

Do not distort faces, hands, fingers or bodies.

The result should look like the original still image
has gently come to life.

Cinematic, peaceful, realistic motion,
high visual consistency with the source image.
""",

    2: """
Animate the existing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
chariot, environment, composition, colors, lighting and
overall devotional visual style of the input image.

Krishna remains calm and dignified while gently moving
his right hand as if explaining an important teaching
to Arjuna.

Add very subtle natural facial movement and gentle blinking.

Krishna's lips move subtly as if he is speaking calmly.

Arjuna remains attentive and makes only a very small
natural head movement while listening.

Allow very slight natural movement in clothing and hair,
as if from a gentle breeze.

All character movements must be slow, graceful,
controlled and devotional.

The characters must remain in their original positions.

Do not change their appearance.

Do not add or remove characters.

Do not change the environment.

Do not change the camera angle.

Do not zoom.

Do not pan.

Do not rotate the camera.

Do not create dramatic action.

Do not distort faces, hands, fingers or bodies.

The result should look like the original still image
has come gently to life.

Cinematic, peaceful, realistic motion,
high visual consistency with the source image.
""",

    3: """
Animate the existing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
chariot, horses, battlefield, armies, environment,
composition, colors, lighting and overall devotional
visual style of the input image.

Krishna remains calm and composed as the charioteer.

Add extremely subtle natural facial movement and gentle blinking.

Krishna makes only a very small natural movement while
holding the reins.

Arjuna remains focused and attentive.

Allow very subtle movement in the horses, clothing,
hair and banners as if affected by a gentle battlefield breeze.

The distant armies remain essentially still.

Keep the atmosphere powerful but peaceful and controlled.

All movement must be slow, graceful and realistic.

The characters must remain in their original positions.

Do not change their appearance.

Do not add or remove characters.

Do not change the environment.

Do not change the camera angle.

Do not zoom.

Do not pan.

Do not rotate the camera.

Do not create fighting or dramatic battlefield action.

Do not distort faces, hands, fingers, horses or bodies.

The result should look like the original still image
has gently come to life.

Cinematic, realistic, devotional motion,
high visual consistency with the source image.
""",

    4: """
Animate the existing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
environment, composition, colors, lighting and overall
devotional visual style of the input image.

Create a peaceful closing feeling.

Krishna remains calm, compassionate and dignified.

Add very subtle natural facial movement and gentle blinking.

Krishna makes a very small graceful hand movement,
as if gently emphasizing the lesson being conveyed.

Allow subtle natural movement in clothing and hair,
as if from a gentle breeze.

Maintain a warm, peaceful and devotional atmosphere.

All movement must be slow, graceful, controlled and natural.

The characters must remain in their original positions.

Do not change their appearance.

Do not add or remove characters.

Do not change the environment.

Do not change the camera angle.

Do not zoom.

Do not pan.

Do not rotate the camera.

Do not create dramatic action.

Do not distort faces, hands, fingers or bodies.

The result should look like the original still image
has gently come to life.

Cinematic, peaceful, realistic motion,
high visual consistency with the source image.
"""
}


# ============================================================
# ANIMATE ONE SCENE
# ============================================================

def animate_scene(scene_number: int):

    scene_dir = BASE_DIR / f"scene{scene_number}"

    image_file = scene_dir / "composed_image.png"
    output_file = scene_dir / f"animated_scene{scene_number}.mp4"

    print()
    print("=" * 70)
    print(f"SCENE {scene_number}")
    print("=" * 70)

    if not image_file.exists():
        print(f"ERROR: Missing image:")
        print(image_file)
        return False

    if output_file.exists():
        print(f"Already exists:")
        print(output_file)
        print("Skipping generation.")
        return True

    print(f"Input : {image_file}")
    print(f"Output: {output_file}")
    print()
    print("Uploading image to Fal...")

    image_url = fal_client.upload_file(str(image_file))

    print("Image uploaded.")
    print()
    print("Starting Kling generation...")
    print("This may take some time.")
    print()

    result = fal_client.subscribe(
        MODEL,
        arguments={
            "prompt": SCENE_PROMPTS[scene_number],
            "negative_prompt": NEGATIVE_PROMPT,
            "start_image_url": image_url,
        "duration": "15",
        },
        with_logs=True,
    )

    video_url = result["video"]["url"]

    print()
    print("Video generated.")
    print("Downloading...")

    urllib.request.urlretrieve(
        video_url,
        output_file,
    )

    print()
    print(f"SUCCESS:")
    print(output_file)

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    if not os.environ.get("FAL_KEY"):
        raise RuntimeError(
            "FAL_KEY environment variable is not set."
        )

    print()
    print("=" * 70)
    print("BHAGAVAD GITA - ALL SCENE ANIMATION")
    print("=" * 70)

    for scene_number in range(1, 5):

        success = animate_scene(scene_number)

        if not success:
            print()
            print(f"Scene {scene_number} failed.")
            print("Stopping.")
            return

    print()
    print("=" * 70)
    print("ALL 4 SCENES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()