"""Smoke test: every page renders in all 5 languages and the JSON API behaves.

Run from the project root:   python tests/smoke_test.py
Uses a throw-away database and never calls YarnGPT/Groq.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config  # noqa: E402


class TestConfig(Config):
    TESTING = True
    _tmp = tempfile.mkdtemp()
    DATABASE = os.path.join(_tmp, "test.db")
    GENERATED_DIR = os.path.join(_tmp, "generated")
    YARN_API_KEY = ""
    GROQ_API_KEY = ""
    SIMULATE_SENSORS = True
    SEED_DEMO_DATA = True
    DEVICE_API_KEY = "secret"


from app import create_app  # noqa: E402

app = create_app(TestConfig)
c = app.test_client()
failures = []


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  {extra}" if extra and not cond else ""))
    if not cond:
        failures.append(name)


# pages in every language
for lang in ("en", "yo", "ig", "ha", "pcm"):
    c.get(f"/set-language/{lang}")
    for path in ("/", "/voice", "/medicine", "/health", "/alerts", "/alarm", "/settings"):
        r = c.get(path)
        check(f"GET {path} [{lang}]", r.status_code == 200 and b"myElderly" in r.data, r.status_code)
c.get("/set-language/pcm")
check("pidgin dashboard subtitle", b"care overview be dis for today" in c.get("/").data)
c.get("/set-language/en")

# dashboard payload
d = c.get("/api/dashboard").get_json()
check("dashboard has 24h history", len(d["history"]["heart_rate"]) > 100, len(d["history"]["heart_rate"]))
check("dashboard medicine totals", d["medicine"]["total"] == 4, d["medicine"]["total"])
check("heart rate within range", 50 <= d["vitals"]["heart_rate"] <= 120)

# medicine
r = c.post("/api/medicines", json={"name": "Test med", "dose": "1", "times": "6:30, 21:00"})
check("add medicine", r.status_code == 201)
check("bad time rejected", c.post("/api/medicines", json={"name": "x", "times": "25:99"}).status_code == 400)
mid = r.get_json()["id"]
check("take dose", c.post("/api/medicines/take", json={"medicine_id": mid, "slot": "06:30"}).status_code == 200)
today = c.get("/api/medicines/today").get_json()
check("dose recorded as taken", any(s["medicine_id"] == mid and s["slot"] == "06:30" and s["status"] == "taken" for s in today["schedule"]))
check("delete medicine", c.delete(f"/api/medicines/{mid}").status_code == 200)

# alarms
r = c.post("/api/alarms", json={"time": "7:05", "label": "Wake up", "days": [0, 2]})
check("add alarm", r.status_code == 201)
aid = r.get_json()["id"]
al = c.get("/api/alarms").get_json()["alarms"][0]
check("alarm normalised", al["time"] == "07:05" and al["days"] == [0, 2])
check("toggle alarm", c.patch(f"/api/alarms/{aid}", json={"enabled": False}).status_code == 200)
check("delete alarm", c.delete(f"/api/alarms/{aid}").status_code == 200)

# hardware vitals + threshold alert
check("device key enforced", c.post("/api/vitals", json={"heart_rate": 80}).status_code == 401)
h = {"X-Device-Key": "secret"}
check("device reading ok", c.post("/api/vitals", json={"heart_rate": 150, "temperature": 36.9}, headers=h).status_code == 201)
alerts = c.get("/api/alerts").get_json()["alerts"]
check("high heart-rate alert raised", any(a["kind"] == "heart_high" for a in alerts))
c.post("/api/vitals", json={"heart_rate": 151}, headers=h)
check("alert cooldown (no duplicates)", sum(a["kind"] == "heart_high" for a in c.get("/api/alerts").get_json()["alerts"]) == 1)

# emergency + phone stub
r = c.post("/api/emergency")
check("emergency recorded", r.status_code == 201 and r.get_json()["phone"]["implemented"] is False)
check("phone call is 'coming soon'", c.post("/api/phone/call").status_code == 501)
first = c.get("/api/alerts").get_json()["alerts"][0]
check("ack alert", c.post(f"/api/alerts/{first['id']}/ack").status_code == 200)

# assistant without keys fails politely
check("chat without GROQ key -> 503", c.post("/api/chat", json={"text": "hello"}).status_code == 503)
check("voice without audio -> 400", c.post("/api/voice", data={}).status_code == 400)

# settings
c.post("/api/settings", json={"elder_name": "Papa", "family_phone": "+2348000000000"})
check("settings saved", c.get("/api/settings").get_json()["elder_name"] == "Papa")
check("header shows new name", b"Papa" in c.get("/").data)

print("\n%d failure(s)" % len(failures))
sys.exit(1 if failures else 0)
