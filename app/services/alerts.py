from datetime import timedelta

from ..db import execute, get_setting, query
from ..utils import now, now_iso
from . import phone


def create(kind, level, message, notify=True):
    alert_id = execute(
        "INSERT INTO alerts(ts, kind, level, message) VALUES(?,?,?,?)",
        (now_iso(), kind, level, message),
    )
    result = {"id": alert_id, "sms": None, "call": None}
    if notify and level in ("warning", "critical"):
        number = get_setting("family_phone", "")
        result["sms"] = phone.send_sms(number, message)  # not implemented yet
        if level == "critical":
            result["call"] = phone.place_call(number)  # not implemented yet
    return result


def create_once(kind, level, message, cooldown_minutes=30):
    """Skip if the same kind of alert was raised recently (avoids alert storms)."""
    since = (now() - timedelta(minutes=cooldown_minutes)).isoformat()
    if query("SELECT id FROM alerts WHERE kind = ? AND ts >= ? LIMIT 1", (kind, since), one=True):
        return None
    return create(kind, level, message)


def recent(limit=50, days=None):
    sql, args = "SELECT * FROM alerts", []
    if days:
        sql += " WHERE ts >= ?"
        args.append((now() - timedelta(days=days)).isoformat())
    sql += " ORDER BY ts DESC, id DESC LIMIT ?"
    args.append(limit)
    return query(sql, args)


def count_days(days=7):
    since = (now() - timedelta(days=days)).isoformat()
    return query("SELECT COUNT(*) AS n FROM alerts WHERE ts >= ?", (since,), one=True)["n"]


def acknowledge(alert_id):
    execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
