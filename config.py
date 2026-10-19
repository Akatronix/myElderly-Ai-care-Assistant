"""Central configuration for myElderly. Values come from environment variables
(or a .env file next to this file)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:  # python-dotenv is optional
    pass


def _bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    DATABASE = str(BASE_DIR / "instance" / "myelderly.db")
    GENERATED_DIR = str(BASE_DIR / "app" / "static" / "generated")
    MAX_CONTENT_LENGTH = 12 * 1024 * 1024  # audio uploads

    # --- AI / voice providers -------------------------------------------
    YARN_API_KEY = os.environ.get("YARN_API_KEY", "")
    YARN_BASE_URL = os.environ.get("YARN_BASE_URL", "https://api.yarngpt.ai/api/v1")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    TTS_OUTPUT_FORMAT = os.environ.get("TTS_OUTPUT_FORMAT", "wav")
    POLL_START = 1.0
    POLL_MAX = 4.0
    POLL_TIMEOUT = 90  # seconds to wait for STT / TTS jobs

    # Optional exact (case-sensitive) YarnGPT voice id per language.
    # Leave blank to auto-pick from the live voice catalogue.
    VOICE_OVERRIDES = {
        "en": os.environ.get("YARN_VOICE_EN", ""),
        "yo": os.environ.get("YARN_VOICE_YO", ""),
        "ig": os.environ.get("YARN_VOICE_IG", ""),
        "ha": os.environ.get("YARN_VOICE_HA", ""),
        "pcm": os.environ.get("YARN_VOICE_PCM", ""),
    }

    # --- Sensors / hardware ---------------------------------------------
    SIMULATE_SENSORS = _bool("SIMULATE_SENSORS", True)  # fake vitals until hardware is wired
    DEVICE_API_KEY = os.environ.get("DEVICE_API_KEY", "")  # sent by hardware as X-Device-Key
    HR_RANGE = (50, 120)  # BPM
    TEMP_RANGE = (35.5, 38.0)  # degrees C
    SEED_DEMO_DATA = _bool("SEED_DEMO_DATA", True)  # sample vitals + sample medicines on first run

    DEFAULT_LANGUAGE = "en"
