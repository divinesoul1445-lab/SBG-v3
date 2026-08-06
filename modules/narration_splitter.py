"""
Narration Splitter V3
"""


class NarrationSplitter:

    def split(self, narration: str):

        sections = {}

        current = None

        for line in narration.splitlines():

            line = line.strip()

            if not line:
                continue

            if line == "===SCENE1===":
                current = "scene1"
                sections[current] = []
                continue

            if line == "===SCENE2===":
                current = "scene2"
                sections[current] = []
                continue

            if line == "===SCENE3===":
                current = "scene3"
                sections[current] = []
                continue

            if line == "===SCENE4===":
                current = "scene4"
                sections[current] = []
                continue

            if current:
                sections[current].append(line)

        return {

            "scene1": "\n".join(sections.get("scene1", [])),

            "scene2": "\n".join(sections.get("scene2", [])),

            "scene3": "\n".join(sections.get("scene3", [])),

            "scene4": "\n".join(sections.get("scene4", [])),

        }