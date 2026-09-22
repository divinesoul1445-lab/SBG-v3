"""
SBG V4
Reusable Character Animation Generator

Purpose:
    Generate ONE reusable animated video for each of the
    four existing SBG scene images.

IMPORTANT:
    - Uses the existing selected images.
    - Does NOT modify videos.py.
    - Does NOT modify the production pipeline.
    - Does NOT regenerate images.
    - Animation is generated only once and can then be reused
      for every verse.

INPUT:
    assets/images/
        Scene1-Starting.jpeg
        Scene2-KrishnatoArjun.jpeg
        Scene3-ArjuntoKrishna.jpeg
        Scene4-closing.jpeg

OUTPUT:
    assets/animations/
        scene1_animation.mp4
        scene2_animation.mp4
        scene3_animation.mp4
        scene4_animation.mp4
"""

from pathlib import Path
import os
import mimetypes
import urllib.request

import requests
import fal_client


# ==========================================================
# PROJECT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent


# ==========================================================
# INPUT / OUTPUT DIRECTORIES
# ==========================================================

IMAGE_DIR = (
    PROJECT_ROOT
    / "assets"
    / "images"
)

ANIMATION_DIR = (
    PROJECT_ROOT
    / "assets"
    / "animations"
)

ANIMATION_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# FAL CONFIGURATION
# ==========================================================

FAL_KEY = os.environ.get("FAL_KEY")

REST_URL = "https://rest.fal.ai"

CDN_URL = "https://v3.fal.media"

CDN_TOKEN_URL = (
    REST_URL
    + "/storage/auth/token"
    + "?storage_type=fal-cdn-v3"
)


# ==========================================================
# KLING MODEL
# ==========================================================

MODEL = (
    "fal-ai/kling-video/v3/standard/image-to-video"
)


# ==========================================================
# SCENES
# ==========================================================

SCENES = [

    {
        "scene": 1,
        "image": "Scene1-Starting.jpeg",
        "output": "scene1_animation.mp4",
        "prompt": """
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
""",
    },

    {
        "scene": 2,
        "image": "Scene2-KrishnatoArjun.jpeg",
        "output": "scene2_animation.mp4",
        "prompt": """
Animate the existing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
chariot, environment, composition, colors, lighting and
overall devotional visual style of the input image.

Krishna remains calm, compassionate and dignified.

Krishna gently moves his hand as if explaining an important
spiritual teaching to Arjuna.

Add extremely subtle natural facial movement and gentle
blinking.

Krishna's lips move subtly as if speaking calmly.

Arjuna remains attentive and respectful.

Arjuna makes only a very small natural head movement while
listening to Krishna.

Allow subtle natural movement in clothing and hair from a
gentle breeze.

All movement must be slow, graceful, controlled and devotional.

The characters must remain in their original positions.

Do not change their appearance.

Do not add or remove characters.

Do not change the environment.

Do not change the composition.

Do not change the camera angle.

Do not zoom.

Do not pan.

Do not rotate the camera.

Do not create dramatic action.

Do not distort faces, hands, fingers or bodies.

The result should look like the original still image has
gently come to life.

Cinematic, peaceful, realistic motion,
high visual consistency with the source image.
""",
    },

    {
        "scene": 3,
        "image": "Scene3-ArjuntoKrishna.jpeg",
        "output": "scene3_animation.mp4",
        "prompt": """
Animate the existing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
chariot, environment, composition, colors, lighting and
overall devotional visual style of the input image.

Arjuna remains emotional but controlled and respectful.

Arjuna makes a very subtle natural facial movement and
gentle blinking.

Arjuna may make a small natural movement of his head while
speaking respectfully to Krishna.

Krishna remains completely calm, compassionate and dignified.

Krishna makes only a very subtle natural facial movement
and gentle blinking while listening.

Allow a slight natural movement in clothing and hair from
a gentle breeze.

All character movements must be slow, graceful, controlled
and devotional.

The characters must remain in their original positions.

Do not change their appearance.

Do not add or remove characters.

Do not change the environment.

Do not change the composition.

Do not change the camera angle.

Do not zoom.

Do not pan.

Do not rotate the camera.

Do not create dramatic action.

Do not distort faces, hands, fingers or bodies.

The result should look like the original still image has
gently come to life.

Cinematic, peaceful, realistic motion,
high visual consistency with the source image.
""",
    },

    {
        "scene": 4,
        "image": "Scene4-closing.jpeg",
        "output": "scene4_animation.mp4",
        "prompt": """
Animate the existing closing scene very subtly and naturally.

Preserve the exact characters, faces, clothing, jewelry,
environment, composition, colors, lighting and devotional
visual style of the input image.

Krishna remains peaceful, divine and dignified.

Add very subtle natural facial movement and gentle blinking.

Allow a very slight natural movement of Krishna's hand as if
giving a final blessing or concluding teaching.

Arjuna remains calm and respectful with only a tiny natural
head movement.

Allow very subtle movement in clothing and hair from a
gentle breeze.

All movement must be slow, graceful, peaceful and devotional.

The characters must remain in their original positions.

Do not change their appearance.

Do not add or remove characters.

Do not change the environment.

Do not change the composition.

Do not change the camera angle.

Do not zoom.

Do not pan.

Do not rotate the camera.

Do not create dramatic action.

Do not distort faces, hands, fingers or bodies.

The result should look like the original still image has
gently come to life.

Cinematic, peaceful, realistic motion,
high visual consistency with the source image.
""",
    },

]


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
# VALIDATION
# ==========================================================

def validate():
    print()
    print("=" * 80)
    print("SBG V4 — REUSABLE CHARACTER ANIMATION GENERATOR")
    print("=" * 80)
    print()

    if not FAL_KEY:
        raise RuntimeError(
            "FAL_KEY environment variable is not set.\n\n"
            "PowerShell:\n"
            '$env:FAL_KEY="YOUR_FAL_API_KEY"'
        )

    print(
        f"Image directory : {IMAGE_DIR}"
    )

    print(
        f"Output directory: {ANIMATION_DIR}"
    )

    print(
        f"Model           : {MODEL}"
    )

    print()

    missing = []

    for scene in SCENES:

        image_file = (
            IMAGE_DIR
            / scene["image"]
        )

        if not image_file.exists():
            missing.append(
                str(image_file)
            )

    if missing:

        print(
            "Missing images:"
        )

        for item in missing:
            print(
                f"  {item}"
            )

        raise FileNotFoundError(
            "One or more scene images are missing."
        )

    print(
        "All four scene images found."
    )

    print()


# ==========================================================
# GET CDN TOKEN
# ==========================================================

def get_cdn_token():

    print(
        "Requesting FAL CDN upload token..."
    )

    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(
        CDN_TOKEN_URL,
        headers=headers,
        json={},
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    token = data.get(
        "token"
    )

    token_type = data.get(
        "token_type"
    )

    base_url = data.get(
        "base_url"
    )

    if not token:
        raise RuntimeError(
            f"FAL CDN token was not returned.\n{data}"
        )

    if not base_url:
        raise RuntimeError(
            f"FAL CDN base URL was not returned.\n{data}"
        )

    print(
        f"CDN base URL: {base_url}"
    )

    print(
        f"Token type  : {token_type}"
    )

    print()

    return (
        token,
        token_type,
        base_url,
    )


# ==========================================================
# UPLOAD IMAGE DIRECTLY TO FAL CDN
# ==========================================================

def upload_image(
    image_file,
    token,
    token_type,
    base_url,
):

    print(
        f"Uploading image: {image_file.name}"
    )

    mime_type, _ = mimetypes.guess_type(
        str(image_file)
    )

    if not mime_type:
        mime_type = (
            "application/octet-stream"
        )

    with open(
        image_file,
        "rb",
    ) as f:

        data = f.read()

    headers = {
        "Authorization": (
            f"{token_type} {token}"
        ),
        "Content-Type": mime_type,
        "X-Fal-File-Name": image_file.name,
    }

    upload_url = (
        base_url.rstrip("/")
        + "/files/upload"
    )

    response = requests.post(
        upload_url,
        headers=headers,
        data=data,
        timeout=180,
    )

    response.raise_for_status()

    result = response.json()

    access_url = result.get(
        "access_url"
    )

    if not access_url:

        raise RuntimeError(
            "FAL CDN did not return access_url.\n\n"
            f"Response:\n{result}"
        )

    print(
        "Upload successful."
    )

    print(
        f"Image URL: {access_url}"
    )

    print()

    return access_url


# ==========================================================
# DOWNLOAD VIDEO
# ==========================================================

def download_video(
    video_url,
    output_file,
):

    print(
        "Downloading generated animation..."
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    urllib.request.urlretrieve(
        video_url,
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

    print(
        f"Downloaded: {output_file}"
    )

    print()


# ==========================================================
# GENERATE ONE SCENE
# ==========================================================

def generate_scene(
    scene,
    token,
    token_type,
    base_url,
):

    scene_number = scene["scene"]

    image_file = (
        IMAGE_DIR
        / scene["image"]
    )

    output_file = (
        ANIMATION_DIR
        / scene["output"]
    )

    print()
    print("=" * 80)
    print(
        f"SCENE {scene_number}"
    )
    print("=" * 80)
    print()

    print(
        f"Input : {image_file}"
    )

    print(
        f"Output: {output_file}"
    )

    print()

    # ------------------------------------------------------
    # Upload image
    # ------------------------------------------------------

    image_url = upload_image(
        image_file,
        token,
        token_type,
        base_url,
    )

    # ------------------------------------------------------
    # Submit Kling job
    # ------------------------------------------------------

    print(
        "Submitting image to Kling..."
    )

    print(
        f"Model: {MODEL}"
    )

    print()

    result = fal_client.subscribe(
        MODEL,
        arguments={
            "prompt": scene["prompt"],
            "negative_prompt": NEGATIVE_PROMPT,
            "start_image_url": image_url,
        },
        with_logs=True,
    )

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
            "Video URL was not returned by fal.ai.\n\n"
            f"Result:\n{result}"
        )

    print()
    print(
        "Kling generation complete."
    )

    print(
        f"Video URL:\n{video_url}"
    )

    print()

    # ------------------------------------------------------
    # Download
    # ------------------------------------------------------

    download_video(
        video_url,
        output_file,
    )

    # ------------------------------------------------------
    # Verify
    # ------------------------------------------------------

    print(
        f"Scene {scene_number} animation ready."
    )

    print(
        f"File size: "
        f"{output_file.stat().st_size:,} bytes"
    )

    print()

    return output_file


# ==========================================================
# MAIN
# ==========================================================

def main():

    validate()

    # ------------------------------------------------------
    # Get ONE CDN token.
    #
    # The same token can be reused for all four uploads.
    # ------------------------------------------------------

    (
        token,
        token_type,
        base_url,
    ) = get_cdn_token()

    successful = []
    failed = []

    # ------------------------------------------------------
    # Generate all four reusable animations
    # ------------------------------------------------------

    for scene in SCENES:

        try:

            output_file = generate_scene(
                scene,
                token,
                token_type,
                base_url,
            )

            successful.append(
                output_file
            )

        except Exception as exc:

            failed.append(
                (
                    scene["scene"],
                    str(exc),
                )
            )

            print()
            print(
                "!" * 80
            )

            print(
                f"SCENE {scene['scene']} FAILED"
            )

            print(
                str(exc)
            )

            print(
                "The remaining scenes will continue."
            )

            print(
                "!" * 80
            )

            print()

    # ------------------------------------------------------
    # Final report
    # ------------------------------------------------------

    print()
    print("=" * 80)
    print("SBG V4 — CHARACTER ANIMATION GENERATION COMPLETE")
    print("=" * 80)
    print()

    print(
        f"Successful scenes: {len(successful)} / 4"
    )

    print(
        f"Failed scenes    : {len(failed)} / 4"
    )

    print()

    if successful:

        print(
            "Generated animations:"
        )

        for file in successful:

            print(
                f"  {file}"
            )

        print()

    if failed:

        print(
            "Failed animations:"
        )

        for scene_number, error in failed:

            print(
                f"  Scene {scene_number}: {error}"
            )

        print()

    print(
        "IMPORTANT:"
    )

    print(
        "These animations are reusable assets."
    )

    print(
        "They have NOT been integrated into videos.py."
    )

    print(
        "They can be reused for every verse."
    )

    print()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()