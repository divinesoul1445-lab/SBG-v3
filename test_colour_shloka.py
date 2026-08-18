from modules.videos import VideoRenderer
from pathlib import Path

renderer = VideoRenderer()

path = "C://SBG//SBG-v3//output//chapter_001//verse_001//scene2//"

BASE_DIR = Path(__file__).resolve().parent


renderer.render_scene(
    image_file= r"C:\SBG\SBG-v3\output\chapter_001\verse_001\scene2/composed_image.png",
    audio_file= path + "narration.mp3",
    subtitle_file= path + "subtitles.srt",
    shloka_overlay= path + "chapter1_verse1.webm",
    output_file= path + "chapter1_verse1_test.mp4",
)