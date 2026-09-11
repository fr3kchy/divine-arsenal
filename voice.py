#!/usr/bin/env python3
"""
Hermes Voice System — expressive TTS via Kokoro-82M on local CPU.
Uses upstream kokoro package with PyTorch CPU backend.
Plays through default audio output.
"""

import sys
import os
import time
import numpy as np

VOICES = {
    'af_sarah':    'American female — warm, Sarah',
    'af_nicole':   'American female — Nicole',
    'af_heart':    'American female — soft, warm',
    'af_alloy':    'American female — Alloy',
    'af_aoede':    'American female — Aoede',
    'af_bella':    'American/Aus female — Bella',
    'af_jessica':  'American female — Jessica',
    'af_kore':     'American female — Kore',
    'af_nova':     'American female — Nova',
    'af_river':    'American female — River',
    'af_sky':      'American female — Sky',
    'am_adam':     'American male — Adam',
    'am_echo':     'American male — Echo',
    'am_eric':     'American male — Eric',
    'am_fenrir':   'American male — Fenrir',
    'am_liam':     'American male — Liam',
    'am_michael':  'American male — Michael',
    'am_onyx':     'American male — Onyx',
    'am_puck':     'American male — Puck (deep)',
    'am_santa':    'American male — Santa',
    'bf_emma':     'British female — Emma',
    'bf_isabella': 'British female — Isabella',
    'bf_lily':     'British female — Lily',
    'bm_george':   'British male — George',
    'bm_lewis':    'British male — Lewis',
    'ff_siwis':    'French female — Siwis',
    'jf_alpha':    'Japanese female — Alpha',
    'zf_xiaobei':  'Chinese female — Xiaobei',
    'pf_dora':     'Portuguese (BR) female — Dora',
    'sf_dora':     'Spanish female — Dora',
}

EMOTION_PRESETS = {
    'neutral':   '<prosody rate="1.0" pitch="0Hz">%s</prosody>',
    'excited':   '<prosody rate="1.15" pitch="+30Hz">%s</prosody>',
    'whisper':   '<prosody rate="0.85" pitch="-10Hz" volume="soft">%s</prosody>',
    'sad':       '<prosody rate="0.8" pitch="-20Hz">%s</prosody>',
    'angry':     '<prosody rate="1.1" pitch="+20Hz">%s</prosody>',
    'question':  '<prosody rate="1.0" pitch="+15Hz">%s</prosody>',
    'emphatic':  '<prosody rate="0.95" pitch="+10Hz">%s</prosody>',
    'slow':      '<prosody rate="0.6" pitch="-5Hz">%s</prosody>',
    'fast':      '<prosody rate="1.4" pitch="+5Hz">%s</prosody>',
    'robotic':   '<prosody rate="0.9" pitch="0Hz">%s</prosody>',
}


def _make_pipeline(voice='af_sarah'):
    """Initialize the KPipeline (upstream kokoro package)."""
    from kokoro import KPipeline
    # Use 'a' for american english, 'b' for british, etc.
    lang_map = {'en-us': 'a', 'en-gb': 'b', 'en': 'a', 'ja': 'j', 'zh': 'z',
                'fr': 'f', 'pt-br': 'p', 'es': 'e', 'es-mx': 'e', 'ko': 'k'}
    lang_code = lang_map.get('en', 'a')
    return KPipeline(lang_code=lang_code)


_pipeline = None

def _get_pipeline(voice='af_sarah'):
    global _pipeline
    if _pipeline is None:
        _pipeline = _make_pipeline(voice)
    return _pipeline


def speak(text, voice='af_sarah', speed=1.33, lang='en', block=True):
    """Synthesize text and play through speakers."""
    pipe = _get_pipeline(voice)
    import sounddevice as sd
    import soundfile as sf
    import io

    all_audio = []
    for i, (gs, ps, audio) in enumerate(pipe(text, voice=voice, speed=speed)):
        all_audio.append(audio)

    if not all_audio:
        return {'error': 'No audio generated', 'text': text}

    audio = np.concatenate(all_audio) if len(all_audio) > 1 else all_audio[0]
    dur = len(audio) / 24000

    if block:
        sd.play(audio, samplerate=24000)
        sd.wait()
    else:
        sd.play(audio, samplerate=24000)

    return {'text': text, 'voice': voice, 'speed': speed, 'duration_sec': dur}


def speak_express(text, emotion='neutral', voice='af_sarah', speed=1.33, lang='en', block=True):
    """Speak with emotion preset (note: kokoro KPipeline doesn't support SSML prosody -
    this wraps text in simplistic markers. True SSML not supported by upstream kokoro.)"""
    preset = EMOTION_PRESETS.get(emotion, EMOTION_PRESETS['neutral'])
    # Remove XML tags - kokoro doesn't support SSML prosody
    # Instead we use speed to approximate emotion
    emotion_speed_map = {
        'neutral': speed,
        'excited': speed * 1.15,
        'whisper': speed * 0.85,
        'sad': speed * 0.8,
        'angry': speed * 1.1,
        'question': speed * 1.0,
        'emphatic': speed * 0.95,
        'slow': speed * 0.6,
        'fast': speed * 1.4,
        'robotic': speed * 0.9,
    }
    effective_speed = emotion_speed_map.get(emotion, speed)
    r = speak(text, voice=voice, speed=effective_speed, lang=lang, block=block)
    r['emotion'] = emotion
    return r


def list_voices():
    return dict(VOICES)


def list_emotions():
    return list(EMOTION_PRESETS.keys())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Hermes Voice — Kokoro TTS')
    parser.add_argument('text', nargs='*', help='Text to speak')
    parser.add_argument('--voice', '-v', default='af_bella')
    parser.add_argument('--speed', '-s', type=float, default=1.33)
    parser.add_argument('--emotion', '-e', default=None)
    parser.add_argument('--lang', '-l', default='en')
    parser.add_argument('--list-voices', action='store_true')
    parser.add_argument('--list-emotions', action='store_true')
    args = parser.parse_args()

    if args.list_voices:
        for k, d in sorted(VOICES.items()):
            print(f'{k:20s} {d}')
        sys.exit(0)
    if args.list_emotions:
        for e in EMOTION_PRESETS:
            print(e)
        sys.exit(0)

    text = ' '.join(args.text) if args.text else sys.stdin.read()
    if not text.strip():
        print('Provide text as args or pipe stdin.', file=sys.stderr)
        sys.exit(1)

    if args.emotion:
        r = speak_express(text, emotion=args.emotion, voice=args.voice,
                          speed=args.speed, lang=args.lang, block=True)
    else:
        r = speak(text, voice=args.voice, speed=args.speed, lang=args.lang, block=True)

    print(f'✓ {r["duration_sec"]:.1f}s  ({r["voice"]} @ {r["speed"]}x)')
