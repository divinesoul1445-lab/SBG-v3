"""
Scene Generator (V3)

Uses 4 predefined images from assets/images.
"""

from pathlib import Path
from modules.models import Verse


ASSETS = Path("assets/images")


class SceneGenerator:

    def generate(
        self,
        verse: Verse,
        narration: str,
    ):

        return [

            {
                "scene": 1,
                "title": "Krishna Recites",
                "image": ASSETS / "Scene1-Starting.jpeg",
            },

            {
                "scene": 2,
                "title": "Krishna Explains",
                "image": ASSETS / "Scene2-KrishnatoArjun.jpeg",
            },

            {
                "scene": 3,
                "title": "Meaning",
                "image": ASSETS / "Scene3-ArjuntoKrishna.jpeg",
            },

            {
                "scene": 4,
                "title": "Life Lesson",
                "image": ASSETS / "Scene4-closing.jpeg",
            },

        ]