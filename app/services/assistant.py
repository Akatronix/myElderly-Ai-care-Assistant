"""The Alexa-style brain: Groq LLM with tools (alarms, medicine, emergency, internet lookup).

The model always replies in the user's selected language and gets live context
(vitals, today's medicine, alarms) so it can talk about the person's health.
"""
import json
import re

import requests
from flask import current_app

from ..db import execute, get_setting, query
from ..i18n import LLM_LANGUAGE_NAMES, translate
from ..utils import normalize_time, now, now_iso
from . import alarms, alerts, health, medicine, phone

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_alarm",
            "description": "Create an alarm/reminder at a time of day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {"type": "string", "description": "24-hour HH:MM, e.g. 07:30"},
                    "label": {"type": "string", "description": "Short label, e.g. 'Wake up'"},
                },
                "required": ["time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_medicine_taken",
            "description": "Record that the person has taken a medicine dose that is due now or was due earlier today.",
            "parameters": {
                "type": "object",
                "properties": {"medicine_name": {"type": "string"}},
                "required": ["medicine_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "emergency_alert",
            "description": "Raise an emergency alert to the family. Use when the person says they are in danger, have severe pain, "
            "chest pain, difficulty breathing, fell down, cannot get up, or asks for urgent help.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_family",
            "description": "Phone the family member when the person asks to call someone.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_internet",
            "description": "Look up a general-knowledge fact on the internet (people, places, history, science). Not for medical advice.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Short search phrase in English"}},
                "required": ["query"],
            },
        },
    },
]


def _context_block():
    name = get_setting("elder_name", "Mama")
    current = now()
    vit = health.latest()
    sched = medicine.today_schedule()
    med_lines = "\n".join(
        f"- {s['slot']} {s['name']} {s['dose']} [{s['status']}]" for s in sched
    ) or "- none scheduled"
    alarm_lines = "\n".join(
        f"- {a['time']} {a['label']} ({'on' if a['enabled'] else 'off'})" for a in alarms.list_all()
    ) or "- none"
    cfg = current_app.config
    return (
        f"Person you are caring for: {name}\n"
        f"Current local time: {current.strftime('%A %d %B %Y, %H:%M')}\n"
        f"Latest heart rate: {vit['heart_rate']} BPM (normal {cfg['HR_RANGE'][0]}-{cfg['HR_RANGE'][1]})\n"
        f"Latest body temperature: {vit['temperature']} C (normal {cfg['TEMP_RANGE'][0]}-{cfg['TEMP_RANGE'][1]})\n"
        f"Today's medicine schedule (status: taken / due / upcoming / missed):\n{med_lines}\n"
        f"Alarms:\n{alarm_lines}"
    )


def build_system_prompt(lang):
    return (
        "You are the voice assistant of myElderly, a caring companion and health helper for an elderly person in Nigeria. "
        f"ALWAYS reply in {LLM_LANGUAGE_NAMES[lang]}, whatever language the person uses. "
        "Speak warmly and respectfully, like a kind grandchild or nurse. Use short, simple sentences: 1 to 3 sentences. "
        "Your reply will be read aloud, so never use markdown, bullet points, emojis, or symbols. Write times in words the person can say.\n\n"
        "HEALTH RULES: Use the context below to answer questions about heartbeat, temperature and medicine. "
        "Remind about medicine that is due or missed. Never diagnose, never change or invent doses, never tell the person to skip a medicine. "
        "For dose questions, state what is in the schedule and suggest asking the doctor or pharmacist for changes. "
        "If readings are outside the normal range, say so gently and suggest resting, drinking water and telling the family or a doctor. "
        "If the person describes an emergency (chest pain, trouble breathing, a fall, severe pain, confusion, feeling like dying), "
        "call the emergency_alert tool immediately and calmly tell them help is being alerted.\n\n"
        "Use tools for actions: set_alarm, mark_medicine_taken, call_family, lookup_internet. "
        "Phone calling is not available yet; if call_family says it is not implemented, tell the person kindly that calling is coming soon "
        "and offer to send an alert instead. After using a tool, confirm briefly what was done.\n\n"
        "CONTEXT\n" + _context_block()
    )


# ---------------------------------------------------------------- tools
def _lookup_internet(q):
    try:
        s = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": q, "format": "json", "srlimit": 1},
            timeout=8,
        ).json()
        hits = s.get("query", {}).get("search", [])
        if not hits:
            return {"found": False}
        title = hits[0]["title"]
        r = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(title.replace(" ", "_")),
            timeout=8,
        ).json()
        return {"found": True, "title": title, "summary": (r.get("extract") or "")[:700]}
    except requests.RequestException:
        return {"found": False, "error": "No internet connection right now."}


def run_tool(name, args, lang, actions):
    try:
        if name == "set_alarm":
            t = normalize_time(args.get("time", ""))
            alarms.add(t, args.get("label", ""))
            actions.append({"type": "set_alarm", "time": t})
            return {"ok": True, "time": t}
        if name == "mark_medicine_taken":
            med = medicine.find_by_name(args.get("medicine_name", ""))
            if not med:
                return {"ok": False, "error": "Medicine not found", "known": [m["name"] for m in medicine.list_all()]}
            pending = [s for s in medicine.today_schedule() if s["medicine_id"] == med["id"] and s["status"] in ("due", "missed", "upcoming")]
            if not pending:
                return {"ok": False, "error": "All of today's doses are already recorded as taken."}
            pending.sort(key=lambda s: s["slot"])
            medicine.mark_taken(med["id"], pending[0]["slot"])
            actions.append({"type": "medicine_taken", "name": med["name"]})
            return {"ok": True, "medicine": med["name"], "slot": pending[0]["slot"]}
        if name == "emergency_alert":
            alerts.create("emergency", "critical", translate("alert_assistant", get_setting("language", lang)))
            actions.append({"type": "emergency"})
            return {"ok": True, "note": "Alert recorded. SMS/phone to family is coming soon."}
        if name == "call_family":
            result = phone.place_call(get_setting("family_phone", ""))
            actions.append({"type": "call_family"})
            return result
        if name == "lookup_internet":
            return _lookup_internet(args.get("query", ""))
    except Exception as exc:  # tools must never crash the conversation
        return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": f"Unknown tool {name}"}


def _plain_for_speech(text):
    text = re.sub(r"[*_#`>]+", "", text or "")
    text = re.sub(r"([.!?:;,])\s*\n+\s*", r"\1 ", text)  # line break after punctuation -> space
    text = re.sub(r"\s*\n+\s*", ". ", text)               # other line breaks -> a pause
    return re.sub(r"\s{2,}", " ", text).strip()


def _history(limit=8):
    rows = query("SELECT role, text FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
    return [{"role": r["role"], "content": r["text"]} for r in reversed(rows)]


def _log(role, lang, text):
    execute("INSERT INTO conversations(ts, lang, role, text) VALUES(?,?,?,?)", (now_iso(), lang, role, text))


def respond(user_text, lang):
    """Returns {"reply": str, "actions": [...]}. Raises RuntimeError if Groq is not configured."""
    cfg = current_app.config
    if not cfg["GROQ_API_KEY"]:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")
    from groq import Groq

    client = Groq(api_key=cfg["GROQ_API_KEY"])
    messages = [{"role": "system", "content": build_system_prompt(lang)}, *_history(), {"role": "user", "content": user_text}]
    actions, reply = [], ""
    extra = {"reasoning_effort": "low"}

    for _ in range(4):  # allow a few tool round-trips
        resp = client.chat.completions.create(
            model=cfg["GROQ_MODEL"],
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
            max_completion_tokens=900,
            extra_body=extra,
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            reply = msg.content or ""
            break
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments or "{}"}}
                    for tc in msg.tool_calls
                ],
            }
        )
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = run_tool(tc.function.name, args, lang, actions)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})

    reply = _plain_for_speech(reply) or translate("assistant_error", lang)
    _log("user", lang, user_text)
    _log("assistant", lang, reply)
    return {"reply": reply, "actions": actions}
