"""
Camera Library

Provides cinematic camera language used by PromptBuilder.

Every camera type returns a consistent visual description,
lens selection, composition and movement.

This keeps every generated scene looking like a professional film.
"""

CAMERAS = {

    "wide shot": {

        "description": """
Epic cinematic establishing shot showing the full environment,
vast scale, immersive perspective.
""",

        "lens": "24mm Cinema Lens",

        "composition": "Rule of Thirds",

        "movement": "slow_push",

    },

    "medium shot": {

        "description": """
Balanced cinematic framing showing the character from the waist up,
ideal for dialogue and storytelling.
""",

        "lens": "50mm Cinema Lens",

        "composition": "Balanced Composition",

        "movement": "slow_push",

    },

    "close up": {

        "description": """
Emotional cinematic portrait emphasizing facial expression and eyes.
""",

        "lens": "85mm Portrait Lens",

        "composition": "Portrait Composition",

        "movement": "hero_zoom",

    },

    "extreme close up": {

        "description": """
Extreme emotional detail emphasizing the eyes, hands or sacred objects.
""",

        "lens": "135mm Macro Lens",

        "composition": "Extreme Portrait",

        "movement": "slow_push",

    },

    "low angle": {

        "description": """
Heroic low-angle cinematic shot emphasizing strength, divinity and power.
""",

        "lens": "35mm Cinema Lens",

        "composition": "Hero Composition",

        "movement": "tilt_up",

    },

    "high angle": {

        "description": """
High-angle cinematic perspective emphasizing vulnerability or scale.
""",

        "lens": "35mm Cinema Lens",

        "composition": "Top Composition",

        "movement": "tilt_down",

    },

    "over shoulder": {

        "description": """
Over-the-shoulder cinematic dialogue framing between characters.
""",

        "lens": "50mm Cinema Lens",

        "composition": "Dialogue Composition",

        "movement": "slow_push",

    },

    "aerial shot": {

        "description": """
Majestic aerial establishing shot revealing the entire landscape.
""",

        "lens": "16mm Ultra Wide Lens",

        "composition": "Panoramic Composition",

        "movement": "slow_pull",

    },

    "tracking shot": {

        "description": """
Dynamic tracking camera following the character through the environment.
""",

        "lens": "35mm Cinema Lens",

        "composition": "Dynamic Tracking",

        "movement": "pan_right",

    },

    "orbit shot": {

        "description": """
Slow cinematic orbit around the main subject creating dramatic depth.
""",

        "lens": "35mm Cinema Lens",

        "composition": "Circular Composition",

        "movement": "orbit",

    },

}

DEFAULT_CAMERA = {

    "description": "Professional cinematic shot.",

    "lens": "50mm Cinema Lens",

    "composition": "Rule of Thirds",

    "movement": "slow_push",

}


def describe(camera: str):

    if not camera:

        return DEFAULT_CAMERA

    for key, value in CAMERAS.items():

        if key.lower() == camera.lower():

            return value

    return DEFAULT_CAMERA