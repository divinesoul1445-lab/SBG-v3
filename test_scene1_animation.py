"""
SBG V4
Scene 1 Character Animation Test

Purpose:
    Take the existing Scene 1 composed image and generate
    a short AI image-to-video animation.

IMPORTANT:
    This is ONLY a test.
    It does NOT modify videos.py.
    It does NOT modify the production pipeline.
    It does NOT replace the existing scene renderer.

Input:
    output/chapter_001/verse_001/scene1/composed_image.png

Output:
    output/chapter_001/verse_001/scene1/animated_scene1.mp4
"""

from pathlib import Path
import os
import urllib.request

import fal_client


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

IMAGE_FILE = (
    PROJECT_ROOT
    / "output"
    / "chapter_001"
    / "verse_001"
    / "scene1"
    / "composed_image.png"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "output"
    / "chapter_001"
    / "verse_001"
    / "scene1"
    / "animated_scene1.mp4"
)


# ==========================================================
# MODEL
# ==========================================================

MODEL = (
    "fal-ai/kling-video/v3/standard/image-to-video"
)


# ==========================================================
# MOTION PROMPT
# ==========================================================

PROMPT = """
Animate the existing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
chariot, environment, composition, colors, lighting and
overall devotional visual style of the input image.

Krishna remains calm and dignified while gently moving his
right hand as if explaining an important teaching to Arjuna.

Add very subtle natural facial movement and gentle blinking.

Krishna's lips move subtly as if he is speaking calmly.

Arjuna remains attentive and makes only a very small natural
head movement while listening.

Allow a very slight natural movement in clothing and hair,
as if from a gentle breeze.

All character movements must be slow, graceful, controlled
and devotional.

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

The result should look like the original still image has
come gently to life.

Cinematic, peaceful, realistic motion,
high visual consistency with the source image.
"""


# ==========================================================
# NEGATIVE PROMPT
# ==========================================================

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


# ==========================================================
# VALIDATE
# ==========================================================

def validate():
    print()
    print("=" * 80)
    print("SBG V4 — SCENE 1 CHARACTER ANIMATION TEST")
    print("=" * 80)
    print()

    if not IMAGE_FILE.exists():
        raise FileNotFoundError(
            f"Scene 1 image not found:\n{IMAGE_FILE}"
        )

    if IMAGE_FILE.stat().st_size <= 0:
        raise ValueError(
            f"Scene 1 image is empty:\n{IMAGE_FILE}"
        )

    fal_key = os.environ.get(
        "FAL_KEY"
    )

    if not fal_key:
        raise RuntimeError(
            "FAL_KEY environment variable is not set.\n\n"
            "PowerShell example:\n"
            '$env:FAL_KEY="YOUR_FAL_API_KEY"'
        )

    print(
        f"Input image : {IMAGE_FILE}"
    )

    print(
        f"Output video: {OUTPUT_FILE}"
    )

    print(
        f"Model       : {MODEL}"
    )

    print()


# ==========================================================
# DOWNLOAD RESULT
# ==========================================================

def download_video(
    url,
    output_file,
):
    print()
    print(
        "Downloading generated animation..."
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    urllib.request.urlretrieve(
        url,
        output_file,
    )

    if not output_file.exists():
        raise RuntimeError(
            "Video download failed."
        )

    if output_file.stat().st_size <= 0:
        raise RuntimeError(
            "Downloaded video is empty."
        )


# ==========================================================
# MAIN
# ==========================================================

def main():

    validate()

    print(
        "Submitting Scene 1 to Kling..."
    )

    print()

    # ------------------------------------------------------
    # Upload local image to fal storage
    # ------------------------------------------------------

    print(
        "Uploading Scene 1 image..."
    )

    image_url = fal_client.upload_file(
        str(IMAGE_FILE)
    )

    print(
        f"Uploaded image:"
    )

    print(
        image_url
    )

    print()

    # ------------------------------------------------------
    # Submit image-to-video request
    # ------------------------------------------------------

    result = fal_client.subscribe(
        MODEL,
        arguments={
            "prompt": PROMPT,
            "negative_prompt": NEGATIVE_PROMPT,
            "start_image_url": image_url,
        },
        with_logs=True,
    )

    print()
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print()

    # ------------------------------------------------------
    # Extract result
    # ------------------------------------------------------

    if not result:
        raise RuntimeError(
            "fal.ai returned an empty result."
        )

    video = result.get(
        "video"
    )

    if not video:
        raise RuntimeError(
            "No video was returned by fal.ai.\n\n"
            f"Result:\n{result}"
        )

    video_url = video.get(
        "url"
    )

    if not video_url:
        raise RuntimeError(
            "Video URL was not returned.\n\n"
            f"Result:\n{result}"
        )

    print(
        f"Generated video URL:\n{video_url}"
    )

    # ------------------------------------------------------
    # Download
    # ------------------------------------------------------

    download_video(
        video_url,
        OUTPUT_FILE,
    )

    # ------------------------------------------------------
    # Success
    # ------------------------------------------------------

    print()
    print("=" * 80)
    print("SCENE 1 ANIMATION TEST SUCCESSFUL")
    print("=" * 80)
    print()

    print(
        f"Input : {IMAGE_FILE}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This video contains AI-generated character motion."
    )

    print(
        "It has NOT yet been integrated into the SBG renderer."
    )

    print()


if __name__ == "__main__":
    main()
