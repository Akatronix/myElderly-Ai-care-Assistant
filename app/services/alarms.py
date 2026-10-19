from ..db import execute, query
from ..utils import normalize_time


def _row(a):
    a["days"] = [int(d) for d in a["days"].split(",") if d != ""]
    a["enabled"] = bool(a["enabled"])
    return a


def list_all():
    return [_row(a) for a in query("SELECT * FROM alarms ORDER BY time")]


def add(time, label="", days=None):
    time = normalize_time(time)
    days = sorted({int(d) for d in (days or []) if 0 <= int(d) <= 6})
    return execute(
        "INSERT INTO alarms(label, time, days, enabled) VALUES(?,?,?,1)",
        ((label or "").strip(), time, ",".join(map(str, days))),
    )


def set_enabled(alarm_id, enabled):
    execute("UPDATE alarms SET enabled = ? WHERE id = ?", (1 if enabled else 0, alarm_id))


def delete(alarm_id):
    execute("DELETE FROM alarms WHERE id = ?", (alarm_id,))
