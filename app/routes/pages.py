from flask import Blueprint, redirect, render_template, request, session, url_for

from ..db import set_setting
from ..i18n import CODES

bp = Blueprint("pages", __name__)


@bp.get("/")
def dashboard():
    return render_template("dashboard.html", page="dashboard")


@bp.get("/voice")
def voice():
    return render_template("voice.html", page="voice")


@bp.get("/medicine")
def medicine():
    return render_template("medicine.html", page="medicine")


@bp.get("/health")
def health():
    return render_template("health.html", page="health")


@bp.get("/alerts")
def alerts():
    return render_template("alerts.html", page="alerts")


@bp.get("/alarm")
def alarm():
    return render_template("alarm.html", page="alarm")


@bp.get("/settings")
def settings():
    return render_template("settings.html", page="settings")


@bp.get("/set-language/<code>")
def set_language(code):
    if code in CODES:
        session["lang"] = code
        set_setting("language", code)  # single-device appliance: remember it
    target = request.referrer or ""
    if not target.startswith(request.host_url):
        target = url_for("pages.dashboard")
    return redirect(target)
