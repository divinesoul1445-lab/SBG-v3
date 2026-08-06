"""
Prompt Templates

SBG V3

Creates fixed cinematic prompts for every Bhagavad Gita verse.

Pipeline

Verse
    ↓
Narration
    ↓
Prompt Templates
    ↓
3 Image Prompts
"""

from typing import List


class PromptTemplates:
    def build(
        self,
        verse,
        narration: str,
    ) -> List[dict]:
        prompts = [
            self._scene_1(
                verse,
                narration,
            ),
            self._scene_2(
                verse,
                narration,
            ),
            self._scene_3(
                verse,
                narration,
            ),
        ]

        return prompts
        # ----------------------------------------------------
    # Scene 1
    # Krishna recites the verse
    # ----------------------------------------------------

    def _scene_1(
        self,
        verse,
        narration: str,
    ):

        prompt = f"""
Epic Mahabharata
Ancient India
Photorealistic
Hollywood cinematic
Feature film
Vertical composition
Ultra detailed
HDR
8K
Masterpiece

SCENE

Lord Krishna stands on the magnificent chariot of Arjuna
on the battlefield of Kurukshetra.

Krishna is reciting Bhagavad Gita Chapter {verse.chapter}
Verse {verse.verse}.

Arjuna listens with complete attention.

Morning sunlight.

Golden divine aura around Krishna.

Battlefield visible in background.

Ancient Indian armor.

Royal horses.

Epic cinematic atmosphere.

No modern objects.

Emotion:
Calm
Sacred
Divine Wisdom

Narration Context

{narration}

Professional cinematic photography.

Volumetric lighting.

Realistic Indian faces.

Authentic Mahabharata costumes.

No text.

No watermark.

No logo.
"""
        return {
            "scene": 1,
            "duration": 5,
            "prompt": prompt,
        }

        # ----------------------------------------------------
    # Scene 2
    # Krishna explains the meaning to Arjuna
    # ----------------------------------------------------

    def _scene_2(
        self,
        verse,
        narration: str,
    ):

        prompt = f"""
Epic Mahabharata
Ancient India
Photorealistic
Hollywood cinematic
Feature film
Vertical composition
Ultra detailed
HDR
8K
Masterpiece

SCENE

Lord Krishna is explaining the deeper meaning of the Bhagavad Gita
to Arjuna.

Krishna speaks with wisdom and compassion.

Arjuna sits respectfully on the chariot,
listening carefully,
deep in thought.

Close cinematic composition.

Krishna gently gestures with one hand while teaching.

Battlefield of Kurukshetra remains softly visible in the background.

Warm divine sunlight.

Golden aura around Krishna.

Authentic Mahabharata costumes.

Ancient Indian weapons and chariot.

Emotion

Wisdom

Compassion

Guidance

Teaching

Narration Context

{narration}

Natural human anatomy.

Realistic Indian faces.

Professional cinematic photography.

Volumetric lighting.

Film color grading.

Global illumination.

No text.

No logo.

No watermark.

No modern clothing.

No modern objects.
"""

        return {
            "scene": 2,
            "duration": 5,
            "prompt": prompt,

        }

        # ----------------------------------------------------
    # Scene 3
    # Krishna explains the life lesson to the audience
    # ----------------------------------------------------

    def _scene_3(
        self,
        verse,
        narration: str,
    ):

        prompt = f"""
Epic Mahabharata
Ancient India
Photorealistic
Hollywood blockbuster
Feature film quality
Vertical composition
Ultra detailed
HDR
8K
Masterpiece

SCENE

Lord Krishna is facing directly toward the viewer.

Krishna is speaking personally to the audience,
sharing the eternal wisdom of the Bhagavad Gita.

Krishna has a calm, compassionate smile.

One hand is raised in a teaching gesture.

Soft golden divine aura surrounds Krishna.

The battlefield of Kurukshetra is softly blurred in the background,
keeping full attention on Krishna.

Warm cinematic lighting.

Authentic Mahabharata clothing.

Natural human anatomy.

Realistic Indian face.

Emotion

Compassion

Wisdom

Inspiration

Hope

Narration Context

{narration}

Create a powerful spiritual connection between Krishna and the viewer.

Professional cinematic photography.

Film color grading.

Global illumination.

Volumetric lighting.

No text.

No watermark.

No logo.

No modern clothing.

No modern objects.

No anime.

No cartoon.
"""

        return {
            "scene": 3,
            "duration": 5,
            "prompt": prompt,

        }