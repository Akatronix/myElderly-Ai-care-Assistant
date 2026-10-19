from datetime import datetime, timedelta

from ..db import execute, query
from ..utils import now, now_iso, parse_times

MISSED_AFTER_MINUTES = 90


def _row(m):
    m["times"] = [t for t in m["times"].split(",") if t]
    return m


def list_all():
    return [_row(m) for m in query("SELECT * FROM medicines ORDER BY name")]


def add(name, dose, times, notes=""):
    name = (name or "").strip()
    if not name:
        raise ValueError("Medicine name is required.")
    slots = parse_times(times)
    mid = execute(
        "INSERT INTO medicines(name, dose, times, notes, created_at) VALUES(?,?,?,?,?)",
        (name, (dose or "").strip(), ",".join(slots), (notes or "").strip(), now_iso()),
    )
    return mid


def delete(medicine_id):
    execute("DELETE FROM medicine_log WHERE medicine_id = ?", (medicine_id,))
    execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))


def mark_taken(medicine_id, slot, undo=False):
    day = now().date().isoformat()
    if undo:
        execute("DELETE FROM medicine_log WHERE medicine_id = ? AND day = ? AND slot = ?", (medicine_id, day, slot))
        return
    execute(
        "INSERT OR IGNORE INTO medicine_log(medicine_id, day, slot, taken_at) VALUES(?,?,?,?)",
        (medicine_id, day, slot, now_iso()),
    )


def today_schedule():
    current = now()
    day = current.date().isoformat()
    logs = {(r["medicine_id"], r["slot"]): r["taken_at"] for r in query("SELECT * FROM medicine_log WHERE day = ?", (day,))}
    items = []
    for m in list_all():
        for slot in m["times"]:
            h, mi = map(int, slot.split(":"))
            due_at = current.replace(hour=h, minute=mi, second=0)
            taken_at = logs.get((m["id"], slot))
            if taken_at:
                status = "taken"
            elif current >= due_at + timedelta(minutes=MISSED_AFTER_MINUTES):
                status = "missed"
            elif current >= due_at:
                status = "due"
            else:
                status = "upcoming"
            items.append(
                {
                    "medicine_id": m["id"],
                    "name": m["name"],
                    "dose": m["dose"],
                    "notes": m["notes"],
                    "slot": slot,
                    "status": status,
                    "taken_at": taken_at[11:16] if taken_at else None,
                }
            )
    return sorted(items, key=lambda i: (i["slot"], i["name"]))


def adherence(days=7):
    """% of doses taken over the last `days` days (only counting doses already due,
    and only from the day each medicine was added). None if nothing was due yet."""
    current = now()
    logs = {(r["medicine_id"], r["day"], r["slot"]) for r in query("SELECT * FROM medicine_log")}
    due = taken = 0
    for m in list_all():
        added = datetime.fromisoformat(m["created_at"])
        for offset in range(days):
            d = current.date() - timedelta(days=offset)
            if d < added.date():
                continue
            for slot in m["times"]:
                h, mi = map(int, slot.split(":"))
                slot_dt = datetime(d.year, d.month, d.day, h, mi)
                if slot_dt > current:
                    continue
                if d == added.date() and slot_dt < added:
                    continue  # dose time passed before the medicine was added
                due += 1
                taken += (m["id"], d.isoformat(), slot) in logs
    return round(100 * taken / due) if due else None


def find_by_name(name):
    name = (name or "").lower().strip()
    if not name:
        return None
    best = None
    for m in list_all():
        mn = m["name"].lower()
        if name in mn or mn.split(" ")[0] in name:
            best = m
            break
    return best
