"""Vitals storage, simulation (until hardware is connected) and threshold alerts."""
import math
import random
from datetime import timedelta

from flask import current_app

from ..db import execute, get_db, get_setting, query
from ..i18n import translate
from ..utils import now
from . import alerts

STEP_MINUTES = 10


def _sim_point(ts, prev_hr=None, prev_temp=None, rng=random):
    """A plausible reading: daily rhythm + gentle random walk, normally inside range."""
    hours = ts.hour + ts.minute / 60
    base_hr = 74 + 9 * math.sin((hours - 9) / 24 * 2 * math.pi)
    hr = base_hr if prev_hr is None else prev_hr * 0.7 + base_hr * 0.3
    hr += rng.gauss(0, 2.5)
    base_t = 36.8 + 0.3 * math.sin((hours - 14) / 24 * 2 * math.pi)
    temp = base_t if prev_temp is None else prev_temp * 0.8 + base_t * 0.2
    temp += rng.gauss(0, 0.05)
    return int(round(max(56, min(108, hr)))), round(max(36.2, min(37.6, temp)), 1)


def seed_history(hours=24):
    rng = random.Random(7)
    end = now()
    ts = end - timedelta(hours=hours)
    rows, hr, temp = [], None, None
    while ts <= end:
        hr, temp = _sim_point(ts, hr, temp, rng)
        rows.append((ts.isoformat(), hr, temp, "simulated"))
        ts += timedelta(minutes=STEP_MINUTES)
    db = get_db()
    db.executemany("INSERT INTO vitals(ts, heart_rate, temperature, source) VALUES(?,?,?,?)", rows)
    db.commit()


def latest():
    hr = query("SELECT ts, heart_rate AS v, source FROM vitals WHERE heart_rate IS NOT NULL ORDER BY ts DESC LIMIT 1", one=True)
    tp = query("SELECT ts, temperature AS v, source FROM vitals WHERE temperature IS NOT NULL ORDER BY ts DESC LIMIT 1", one=True)
    return {
        "heart_rate": hr["v"] if hr else None,
        "temperature": tp["v"] if tp else None,
        "ts": max([x["ts"] for x in (hr, tp) if x], default=None),
        "simulated": bool((hr or tp or {}).get("source") == "simulated"),
    }


def history(metric="heart_rate", hours=24, max_points=150):
    column = {"heart_rate": "heart_rate", "temperature": "temperature"}.get(metric)
    if not column:
        raise ValueError("metric must be heart_rate or temperature")
    since = (now() - timedelta(hours=hours)).isoformat()
    rows = query(f"SELECT ts, {column} AS v FROM vitals WHERE ts >= ? AND {column} IS NOT NULL ORDER BY ts", (since,))
    if len(rows) > max_points:
        stride = math.ceil(len(rows) / max_points)
        rows = rows[::stride]
    return rows


def status_of(metric, value):
    if value is None:
        return "unknown"
    lo, hi = current_app.config["HR_RANGE" if metric == "heart_rate" else "TEMP_RANGE"]
    return "low" if value < lo else "high" if value > hi else "normal"


def check_thresholds(hr, temp):
    lang = get_setting("language", "en")
    checks = [
        ("heart_rate", hr, "alert_hr_high", "alert_hr_low", "heart"),
        ("temperature", temp, "alert_temp_high", "alert_temp_low", "temp"),
    ]
    for metric, value, key_high, key_low, kind in checks:
        state = status_of(metric, value)
        if state in ("high", "low"):
            key = key_high if state == "high" else key_low
            alerts.create_once(f"{kind}_{state}", "warning", translate(key, lang, v=value))


def add_reading(hr=None, temp=None, source="sensor"):
    if hr is None and temp is None:
        raise ValueError("Provide heart_rate and/or temperature.")
    execute(
        "INSERT INTO vitals(ts, heart_rate, temperature, source) VALUES(?,?,?,?)",
        (now().isoformat(), hr, temp, source),
    )
    check_thresholds(hr, temp)


def maybe_simulate():
    """When no hardware is attached, append a fresh fake reading about once a minute
    and backfill any gap so the 24h chart always looks continuous."""
    if not current_app.config["SIMULATE_SENSORS"]:
        return
    last = query("SELECT ts, heart_rate, temperature FROM vitals ORDER BY ts DESC LIMIT 1", one=True)
    current = now()
    if last:
        from datetime import datetime

        last_ts = datetime.fromisoformat(last["ts"])
        gap = (current - last_ts).total_seconds()
        if gap < 60:
            return
        hr, temp = last["heart_rate"], last["temperature"]
        ts = last_ts + timedelta(minutes=STEP_MINUTES)
        rows = []
        while gap > 15 * 60 and ts < current - timedelta(minutes=STEP_MINUTES) and len(rows) < 144:
            hr, temp = _sim_point(ts, hr, temp)
            rows.append((ts.isoformat(), hr, temp, "simulated"))
            ts += timedelta(minutes=STEP_MINUTES)
        if rows:
            db = get_db()
            db.executemany("INSERT INTO vitals(ts, heart_rate, temperature, source) VALUES(?,?,?,?)", rows)
            db.commit()
    else:
        hr = temp = None
    hr, temp = _sim_point(current, hr, temp)
    add_reading(hr, temp, source="simulated")
