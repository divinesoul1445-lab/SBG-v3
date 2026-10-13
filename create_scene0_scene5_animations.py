"""
SBG-v4: Generate only Scene 0 and Scene 5 animations.
Reuses the upload, Kling submission, download, and verification helpers
from create_character_animations.py. Does not regenerate Scenes 1-4.
"""

import create_character_animations as base


SCENES = [
    {
        "scene": 0,
        "image": "Scene0-Opening.png",
        "output": "scene0_animation.mp4",
        "prompt": """
Create a graceful, cinematic book-opening animation from this exact
starting image. The sacred Bhagavad Gita book slowly opens naturally:
the front cover lifts from its closed position and rotates upward,
then the pages gently separate and fan open a little, as if the book
is being respectfully opened for a spiritual reading. Keep the book
centered and in its original position. Preserve its exact design,
cover artwork, colors, ornaments, proportions, lighting, background,
and devotional atmosphere. Motion should be slow, smooth, realistic,
and reverent. Keep the camera completely fixed: no zoom, no pan,
no rotation, no cuts, and no scene change. Do not add hands or people
unless they already exist in the source image. Do not invent text,
symbols, or extra objects. Avoid bending, melting, duplicating, or
warping the book or its pages. End with the book gently open and stable.
""",
    },
    {
        "scene": 5,
        "image": "Scene5-likeIncentive.png",
        "output": "scene5_animation.mp4",
        "prompt": """
Animate this existing Bhagavad Gita YouTube Shorts closing image into
a warm, polished call-to-action ending. Preserve the exact characters,
faces, hands, clothing, objects, text, icons, layout, colors, lighting,
and devotional style in the source image. Add only subtle, tasteful
motion that supports the existing like-and-subscribe message: a gentle
glow or soft pulse around the existing like/subscribe elements, with
very small natural movement in any existing character. Keep every
word and icon readable, stable, and spelled exactly as in the source.
Do not generate new text, letters, logos, buttons, or icons. Do not
replace, distort, duplicate, or move the main elements. Keep the camera
fixed with no zoom, pan, rotation, cuts, or scene change. The result
should feel inviting, calm, devotional, and suitable for the final
seconds of a vertical YouTube Short.
""",
    },
]


def main():
    # Keep the existing generator's paths, model, and helper functions.
    if not base.FAL_KEY:
        raise RuntimeError(
            "FAL_KEY environment variable is not set. In PowerShell run:\n"
            '$env:FAL_KEY="YOUR_FAL_API_KEY"'
        )

    print("=" * 72)
    print("SBG-v4 — SCENE 0 AND SCENE 5 ANIMATION GENERATOR")
    print("=" * 72)
    print(f"Image directory : {base.IMAGE_DIR}")
    print(f"Output directory: {base.ANIMATION_DIR}")
    print(f"Model           : {base.MODEL}")

    for scene in SCENES:
        image_file = base.IMAGE_DIR / scene["image"]
        if not image_file.exists():
            raise FileNotFoundError(f"Missing input image: {image_file}")
    print("Both input images found.")

    token, token_type, base_url = base.get_cdn_token()
    successful = []
    failed = []

    for scene in SCENES:
        try:
            successful.append(
                base.generate_scene(scene, token, token_type, base_url)
            )
        except Exception as exc:
            failed.append((scene["scene"], str(exc)))
            print(f"\nSCENE {scene['scene']} FAILED: {exc}")

    print("\n" + "=" * 72)
    print(f"Successful animations: {len(successful)} / {len(SCENES)}")
    print(f"Failed animations    : {len(failed)} / {len(SCENES)}")
    if successful:
        print("\nGenerated files:")
        for file in successful:
            print(f"  {file}")
    if failed:
        print("\nFailures:")
        for scene_number, error in failed:
            print(f"  Scene {scene_number}: {error}")
    print("\nScenes 1-4 were not regenerated or modified.")


if __name__ == "__main__":
    main()
