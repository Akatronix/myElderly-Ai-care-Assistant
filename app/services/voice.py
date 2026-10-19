"""YarnGPT speech-to-text and text-to-speech (ported from the original CLI script).

Flow: browser WAV -> transcribe() -> assistant -> synthesize() -> /static/generated/*.wav
"""
import json
import os
import time
import uuid

import requests
from flask import current_app

_voice_cache = {"at": 0, "voices": []}

# Words that identify a voice for each language inside the catalogue JSON.
LANG_TOKENS = {
    "en": ['"english"', '"en"', "english"],
    "yo": ["yoruba", '"yo"'],
    "ig": ["igbo", '"ig"'],
    "ha": ["hausa", '"ha"'],
    "pcm": ["pidgin", '"pcm"'],
}


class VoiceError(RuntimeError):
    pass


def configured():
    return bool(current_app.config["YARN_API_KEY"])


def _cfg(name):
    return current_app.config[name]


def _headers(extra=None):
    key = _cfg("YARN_API_KEY")
    if not key:
        raise VoiceError("YARN_API_KEY is not set. Add it to your .env file.")
    return {"Authorization": f"Bearer {key}", **(extra or {})}


def _raise_for_api_error(response, context):
    """Readable error from YarnGPT's standard error envelope."""
    if response.ok:
        return
    try:
        err = response.json().get("error", {})
    except ValueError:
        err = {}
    code = err.get("code", f"HTTP {response.status_code}")
    message = err.get("user_message") or err.get("message") or response.text[:200]
    trace = err.get("trace_id") or response.headers.get("X-Request-Id")
    raise VoiceError(f"{context} failed: {code} - {message} (trace_id={trace})")


def _poll(url, context):
    delay, deadline = _cfg("POLL_START"), time.time() + _cfg("POLL_TIMEOUT")
    while time.time() < deadline:
        time.sleep(delay)
        delay = min(delay * 1.5, _cfg("POLL_MAX"))
        r = requests.get(url, headers=_headers(), timeout=30)
        _raise_for_api_error(r, f"{context} poll")
        data = r.json()
        status = data.get("status")
        if status == "completed":
            return data
        if status == "failed":
            raise VoiceError(f"{context} failed: {data.get('error_code') or ''} {data.get('error_message') or data.get('user_message') or ''}".strip())
    raise VoiceError(f"Timed out waiting for {context}.")


# ---------------------------------------------------------------- speech-to-text
def transcribe(wav_bytes, filename="speech.wav"):
    """Returns the transcript in the spoken language (no translation requested)."""
    base = _cfg("YARN_BASE_URL")
    headers = _headers({"Idempotency-Key": str(uuid.uuid4())})
    r = requests.post(f"{base}/asr", headers=headers, files={"file": (filename, wav_bytes, "audio/wav")}, timeout=45)
    _raise_for_api_error(r, "Speech recognition upload")
    job_id = r.json().get("job_id")
    if not job_id:
        raise VoiceError("Speech recognition returned no job_id.")
    data = _poll(f"{base}/asr/{job_id}", "Speech recognition")
    return (data.get("transcript") or "").strip()


# ---------------------------------------------------------------- voices
def fetch_voices():
    now = time.time()
    if _voice_cache["voices"] and now - _voice_cache["at"] < 3600:
        return _voice_cache["voices"]
    r = requests.get(f"{_cfg('YARN_BASE_URL')}/voices", headers=_headers(), timeout=30)
    _raise_for_api_error(r, "Voice list")
    body = r.json()
    voices = []
    if isinstance(body, dict):
        for key in ("voices", "data", "items", "results"):
            if isinstance(body.get(key), list):
                voices = body[key]
                break
    elif isinstance(body, list):
        voices = body
    _voice_cache.update(at=now, voices=voices)
    return voices


def voice_id_of(voice):
    if isinstance(voice, str):
        return voice
    for key in ("id", "name", "voice", "voice_id"):
        if voice.get(key):
            return voice[key]
    return None


def choose_voice(lang):
    """Override from .env -> catalogue voice matching the language -> default voice."""
    override = _cfg("VOICE_OVERRIDES").get(lang)
    if override:
        return override
    voices = fetch_voices()
    if not voices:
        raise VoiceError("The voice catalogue is empty. Set YARN_VOICE_<LANG> in .env.")

    def matches(v, code):
        text = json.dumps(v).lower()
        return any(tok in text for tok in LANG_TOKENS[code])

    dict_voices = [v for v in voices if isinstance(v, dict)]
    for code in (lang, "en") if lang == "pcm" else (lang,):
        found = [v for v in dict_voices if matches(v, code)]
        if found:
            return voice_id_of(found[0])
    defaults = [v for v in dict_voices if v.get("default")]
    chosen = (defaults or voices)[0]
    voice = voice_id_of(chosen)
    if not voice:
        raise VoiceError(f"Could not read a voice id from: {chosen}")
    return voice


# ---------------------------------------------------------------- text-to-speech
def _cleanup_old_files(folder, max_age=3600):
    cutoff = time.time() - max_age
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if name.startswith("reply_") and os.path.isfile(path) and os.path.getmtime(path) < cutoff:
            try:
                os.remove(path)
            except OSError:
                pass


def synthesize(text, lang):
    """Returns a URL path like /static/generated/reply_xxx.wav"""
    base = _cfg("YARN_BASE_URL")
    headers = _headers({"Idempotency-Key": str(uuid.uuid4()), "Content-Type": "application/json"})
    # The text is already in the target language, so no target_language (it would translate + bill).
    payload = {"text": text, "voice": choose_voice(lang), "output_format": _cfg("TTS_OUTPUT_FORMAT")}
    r = requests.post(f"{base}/tts", headers=headers, json=payload, timeout=45)
    _raise_for_api_error(r, "Text-to-speech submit")
    job_id = r.json().get("job_id")
    if not job_id:
        raise VoiceError("Text-to-speech returned no job_id.")
    data = _poll(f"{base}/status/{job_id}", "Text-to-speech")
    audio_url = data.get("audio_url")
    if not audio_url:
        raise VoiceError(f"Text-to-speech completed without audio_url: {data}")

    audio = requests.get(audio_url, timeout=60)
    audio.raise_for_status()
    if len(audio.content) < 1000:
        raise VoiceError(f"Downloaded audio looks empty ({len(audio.content)} bytes).")

    folder = _cfg("GENERATED_DIR")
    _cleanup_old_files(folder)
    ext = "mp3" if _cfg("TTS_OUTPUT_FORMAT") == "mp3" else "wav"
    filename = f"reply_{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(folder, filename), "wb") as fh:
        fh.write(audio.content)
    return f"/static/generated/{filename}"
