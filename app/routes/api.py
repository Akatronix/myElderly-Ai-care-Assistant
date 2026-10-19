import time

import requests
from flask import Blueprint, current_app, jsonify, request

from ..db import get_setting, set_setting
from ..i18n import translate
from ..services import alarms, alerts, assistant, health, medicine, phone, voice
from ..utils import current_lang, now_iso

bp = Blueprint("api", __name__)

_internet = {"at": 0.0, "online": False}


def err(message, status=400):
    return jsonify(error=message), status


# ------------------------------------------------------------------ system
@bp.get("/ping")
def ping():
    return jsonify(ok=True, time=now_iso())


@bp.get("/internet")
def internet():
    """Is the *device* connected to the internet? (cached for 20 s)"""
    if time.time() - _internet["at"] > 20:
        try:
            r = requests.get("https://www.gstatic.com/generate_204", timeout=3)
            _internet["online"] = r.status_code in (200, 204)
        except requests.RequestException:
            _internet["online"] = False
        _internet["at"] = time.time()
    return jsonify(online=_internet["online"])


@bp.get("/settings")
def get_settings():
    return jsonify(
        elder_name=get_setting("elder_name", "Mama"),
        family_phone=get_setting("family_phone", ""),
        language=current_lang(),
        voice_ready=voice.configured(),
        assistant_ready=bool(current_app.config["GROQ_API_KEY"]),
        simulate_sensors=current_app.config["SIMULATE_SENSORS"],
    )


@bp.post("/settings")
def save_settings():
    data = request.get_json(silent=True) or {}
    if "elder_name" in data:
        set_setting("elder_name", (data["elder_name"] or "Mama").strip()[:40])
    if "family_phone" in data:
        set_setting("family_phone", (data["family_phone"] or "").strip()[:25])
    return jsonify(ok=True)


# ------------------------------------------------------------------ dashboard / vitals
@bp.get("/dashboard")
def dashboard():
    health.maybe_simulate()
    latest = health.latest()
    schedule = medicine.today_schedule()
    return jsonify(
        name=get_setting("elder_name", "Mama"),
        vitals={
            **latest,
            "hr_status": health.status_of("heart_rate", latest["heart_rate"]),
            "temp_status": health.status_of("temperature", latest["temperature"]),
        },
        medicine={
            "taken": sum(1 for s in schedule if s["status"] == "taken"),
            "total": len(schedule),
            "adherence_7d": medicine.adherence(7),
            "schedule": schedule,
        },
        alerts={"count_7d": alerts.count_days(7), "recent": alerts.recent(limit=5)},
        history={
            "heart_rate": health.history("heart_rate", 24),
            "temperature": health.history("temperature", 24),
        },
    )


@bp.get("/vitals/history")
def vitals_history():
    metric = request.args.get("metric", "heart_rate")
    hours = min(max(request.args.get("hours", 24, type=int), 1), 24 * 14)
    try:
        return jsonify(metric=metric, points=health.history(metric, hours))
    except ValueError as exc:
        return err(str(exc))


@bp.get("/vitals/latest")
def vitals_latest():
    health.maybe_simulate()
    latest = health.latest()
    return jsonify(
        **latest,
        hr_status=health.status_of("heart_rate", latest["heart_rate"]),
        temp_status=health.status_of("temperature", latest["temperature"]),
    )


@bp.post("/vitals")
def post_vitals():
    """Endpoint for the sensor hardware. Body: {"heart_rate": 72, "temperature": 36.8}"""
    key = current_app.config["DEVICE_API_KEY"]
    if key and request.headers.get("X-Device-Key") != key:
        return err("Invalid or missing X-Device-Key.", 401)
    data = request.get_json(silent=True) or {}
    try:
        hr = int(data["heart_rate"]) if data.get("heart_rate") is not None else None
        temp = float(data["temperature"]) if data.get("temperature") is not None else None
        health.add_reading(hr, temp, source="sensor")
    except (ValueError, TypeError) as exc:
        return err(str(exc))
    return jsonify(ok=True), 201


# ------------------------------------------------------------------ medicine
@bp.get("/medicines")
def medicines_list():
    return jsonify(medicines=medicine.list_all())


@bp.post("/medicines")
def medicines_add():
    d = request.get_json(silent=True) or {}
    try:
        mid = medicine.add(d.get("name"), d.get("dose"), d.get("times"), d.get("notes"))
    except ValueError as exc:
        return err(str(exc))
    return jsonify(id=mid), 201


@bp.delete("/medicines/<int:mid>")
def medicines_delete(mid):
    medicine.delete(mid)
    return jsonify(ok=True)


@bp.get("/medicines/today")
def medicines_today():
    schedule = medicine.today_schedule()
    return jsonify(
        schedule=schedule,
        taken=sum(1 for s in schedule if s["status"] == "taken"),
        total=len(schedule),
        adherence_7d=medicine.adherence(7),
    )


@bp.post("/medicines/take")
def medicines_take():
    d = request.get_json(silent=True) or {}
    try:
        medicine.mark_taken(int(d["medicine_id"]), d["slot"], undo=bool(d.get("undo")))
    except (KeyError, ValueError, TypeError):
        return err("medicine_id and slot are required.")
    return jsonify(ok=True)


# ------------------------------------------------------------------ alarms
@bp.get("/alarms")
def alarms_list():
    return jsonify(alarms=alarms.list_all())


@bp.post("/alarms")
def alarms_add():
    d = request.get_json(silent=True) or {}
    try:
        aid = alarms.add(d.get("time", ""), d.get("label", ""), d.get("days"))
    except (ValueError, TypeError) as exc:
        return err(str(exc))
    return jsonify(id=aid), 201


@bp.patch("/alarms/<int:aid>")
def alarms_toggle(aid):
    d = request.get_json(silent=True) or {}
    alarms.set_enabled(aid, bool(d.get("enabled")))
    return jsonify(ok=True)


@bp.delete("/alarms/<int:aid>")
def alarms_delete(aid):
    alarms.delete(aid)
    return jsonify(ok=True)


# ------------------------------------------------------------------ alerts / emergency / phone
@bp.get("/alerts")
def alerts_list():
    return jsonify(alerts=alerts.recent(limit=100), count_7d=alerts.count_days(7))


@bp.post("/alerts/<int:alert_id>/ack")
def alerts_ack(alert_id):
    alerts.acknowledge(alert_id)
    return jsonify(ok=True)


@bp.post("/alerts/test")
def alerts_test():
    result = alerts.create("test", "info", translate("alert_test", current_lang()), notify=False)
    return jsonify(result), 201


@bp.post("/emergency")
def emergency():
    result = alerts.create("emergency", "critical", translate("alert_emergency", current_lang()))
    return jsonify(alert=result, phone=phone.place_call(get_setting("family_phone", ""))), 201


@bp.post("/phone/call")
def phone_call():
    return jsonify(phone.place_call(get_setting("family_phone", ""))), 501


# ------------------------------------------------------------------ voice assistant
def _converse(transcript, lang, wants_audio=True):
    """Shared by /voice and /chat: LLM reply (+ optional speech)."""
    try:
        result = assistant.respond(transcript, lang)
    except RuntimeError as exc:
        return err(str(exc), 503)
    except Exception as exc:  # network / provider errors
        current_app.logger.exception("assistant failed")
        return err(f"The assistant could not answer: {exc}", 502)

    audio_url, tts_error = None, None
    if wants_audio:
        try:
            audio_url = voice.synthesize(result["reply"], lang)
        except Exception as exc:
            current_app.logger.warning("TTS failed: %s", exc)
            tts_error = str(exc)
    return jsonify(
        transcript=transcript,
        reply=result["reply"],
        actions=result["actions"],
        audio_url=audio_url,
        tts_error=tts_error,
    )


@bp.post("/voice")
def voice_endpoint():
    lang = request.form.get("lang") or current_lang()
    upload = request.files.get("audio")
    if not upload:
        return err("No audio uploaded.")
    data = upload.read()
    if len(data) < 3000:
        return jsonify(transcript="", reply=translate("no_speech", lang), actions=[], audio_url=None)
    try:
        transcript = voice.transcribe(data)
    except voice.VoiceError as exc:
        return err(str(exc), 502)
    except requests.RequestException as exc:
        return err(f"Could not reach the speech service: {exc}", 502)
    if not transcript:
        return jsonify(transcript="", reply=translate("no_speech", lang), actions=[], audio_url=None)
    return _converse(transcript, lang)


@bp.post("/chat")
def chat_endpoint():
    d = request.get_json(silent=True) or {}
    text = (d.get("text") or "").strip()
    if not text:
        return err("Empty message.")
    return _converse(text[:1000], d.get("lang") or current_lang(), wants_audio=bool(d.get("speak", True)))
