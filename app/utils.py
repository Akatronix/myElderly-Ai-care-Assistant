import re
from datetime import datetime

from flask import current_app, session

from .db import get_setting
from .i18n import CODES

TIME_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")


def now():
    """Local (server) time, second precision. Set the device timezone correctly."""
    return datetime.now().replace(microsecond=0)


def now_iso():
    return now().isoformat()


def normalize_time(value):
    m = TIME_RE.match(str(value))
    if not m:
        raise ValueError(f"Invalid time: {value!r} (use HH:MM, 24-hour)")
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 23 or mi > 59:
        raise ValueError(f"Invalid time: {value!r}")
    return f"{h:02d}:{mi:02d}"


def parse_times(value):
    """Accepts 'HH:MM, HH:MM' or a list. Returns a sorted, de-duplicated list."""
    items = value if isinstance(value, (list, tuple)) else str(value or "").replace(";", ",").split(",")
    times = sorted({normalize_time(v) for v in items if str(v).strip()})
    if not times:
        raise ValueError("At least one time is required (HH:MM).")
    return times


def current_lang():
    lang = session.get("lang") or get_setting("language") or current_app.config["DEFAULT_LANGUAGE"]
    return lang if lang in CODES else current_app.config["DEFAULT_LANGUAGE"]
