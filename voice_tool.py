#!/usr/bin/env python3
"""
Hermes agent tool for TTS. Designed to be registered as agent-callable tools.
"""

import sys
import os

# Path so we can import from the voice directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voice import speak, speak_express, list_voices, list_emotions, VOICES, EMOTION_PRESETS


def tts_speak(text: str, voice: str = 'af_bella', speed: float = 1.33, lang: str = 'en', block: bool = True) -> dict:
    """Speak text aloud through system speakers using Kokoro TTS.

    Voice defaults to af_bella (warm female), speed to 1.33x.

    Args:
        text: The text to speak
        voice: Voice ID. See tts_list_voices() for options.
        speed: Speed multiplier (0.5-2.5). Default 1.33.
        lang: Language code. 'en' for English, 'ja' for Japanese, etc.
        block: If True (default), wait for speech to finish before returning.

    Returns:
        dict with keys: text, voice, speed, duration_sec
    """
    return speak(text, voice=voice, speed=speed, lang=lang, block=block)


def tts_express(text: str, emotion: str = 'neutral', voice: str = 'af_bella', speed: float = 1.33, lang: str = 'en', block: bool = True) -> dict:
    """Speak text with an emotional/expressive preset.

    Wraps text in SSML prosody tags to adjust pitch, speed, and volume.

    Available emotions: neutral, excited, whisper, sad, angry, question, emphatic, slow, fast, robotic

    Args:
        text: The text to speak
        emotion: Emotion preset
        voice: Voice ID. Default af_bella.
        speed: Speed multiplier. Default 1.33.
        lang: Language code
        block: Wait for speech before returning

    Returns:
        dict with keys: text, voice, speed, emotion, duration_sec
    """
    result = speak_express(text, emotion=emotion, voice=voice, speed=speed, lang=lang, block=block)
    return result


def tts_list_voices() -> dict:
    """List all available TTS voices with descriptions.

    Returns:
        dict mapping voice_id -> description
    """
    return dict(VOICES)


def tts_list_emotions() -> list:
    """List all emotion presets for expressive speech.

    Returns:
        list of emotion names
    """
    return list(EMOTION_PRESETS.keys())
