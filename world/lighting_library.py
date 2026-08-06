"""
Lighting Library

Provides consistent cinematic lighting descriptions.

These descriptions are reused by every prompt.
"""

LIGHTING = {

    "golden sunrise": """
Golden sunrise,
warm orange sunlight,
soft cinematic shadows,
volumetric god rays,
golden rim lighting,
dust illuminated in the air,
global illumination,
HDR lighting,
morning atmosphere,
""",

    "warm cinematic sunlight": """
Warm cinematic afternoon sunlight,
soft directional light,
realistic shadow gradients,
subtle bloom,
global illumination,
warm color grading,
volumetric lighting,
""",

    "dramatic rim lighting": """
Strong cinematic rim lighting,
deep contrast,
warm highlights,
cool shadows,
dramatic atmosphere,
film-quality lighting,
volumetric rays,
""",

    "divine golden glow": """
Divine golden radiance,
heavenly light,
volumetric god rays,
ethereal bloom,
soft heavenly atmosphere,
warm cinematic grading,
global illumination,
high dynamic range,
""",

    "moonlight": """
Soft blue moonlight,
cold cinematic lighting,
mist,
volumetric moon rays,
high contrast,
night atmosphere,
""",

    "temple firelight": """
Warm firelight,
oil lamps,
golden reflections,
soft flickering shadows,
ancient Indian temple atmosphere,
cinematic lighting,
""",
}

DEFAULT_LIGHTING = """
Warm cinematic lighting,
soft shadows,
volumetric light,
global illumination,
HDR,
"""

def describe(name: str):

    if not name:
        return DEFAULT_LIGHTING

    return LIGHTING.get(
        name.lower(),
        DEFAULT_LIGHTING,
    )