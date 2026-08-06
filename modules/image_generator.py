"""
Image Generator (V3)

Simple FLUX Dev image generation.

Input:
    prompt

Output:
    jpg
"""

from pathlib import Path

import requests
import fal_client

from config import FAL_KEY


class ImageGenerator:

    def __init__(self):

        import os

        os.environ["FAL_KEY"] = FAL_KEY

    # --------------------------------------------------
    # Generate one image
    # --------------------------------------------------

    def generate_image(
        self,
        prompt: str,
        output_file: Path,
        ) -> Path:

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result = fal_client.subscribe(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "image_size": {

                    "width": 1080,
                    "height": 1920,

                },
                "num_images": 1,
            },
        )

        image_url = result["images"][0]["url"]

        response = requests.get(
            image_url,
            timeout=120,
        )

        response.raise_for_status()

        output_file.write_bytes(
            response.content
        )

        print(f"Saved -> {output_file}")

        return output_file

    # --------------------------------------------------
    # Generate all scenes
    # --------------------------------------------------

    def generate_scene_images(
        self,
        prompts: list,
        output_folder,

    ):

        output_folder = Path(output_folder)
        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        images = []
        total = len(prompts)
        for index, scene in enumerate(
            prompts,
            start=1,
        ):

            print()
            print(f"Scene {index}/{total}")
            output_file = (
                output_folder
                / f"scene_{index:02d}.jpg"
            )

            self.generate_image(
                prompt=scene["prompt"],
                output_file=output_file,
            )

            images.append(output_file)

        return images