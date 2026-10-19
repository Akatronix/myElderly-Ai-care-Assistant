"""First-run data: default settings, and (optionally) demo vitals + sample medicines."""
from .db import execute, get_setting, set_setting
from .utils import now_iso


def run(app):
    with app.app_context():
        if get_setting("seeded") == "1":
            return
        set_setting("elder_name", "Mama")
        set_setting("language", app.config["DEFAULT_LANGUAGE"])
        set_setting("family_phone", "")

        if app.config["SEED_DEMO_DATA"]:
            from .services import health

            health.seed_history()
            for name, dose, times, notes in [
                ("Amlodipine 5mg (sample)", "1 tablet", "08:00", "Sample entry. Replace with the real prescription."),
                ("Metformin 500mg (sample)", "1 tablet", "08:00,20:00", "Sample entry. Take with food."),
                ("Vitamin D (sample)", "1 capsule", "13:00", "Sample entry."),
            ]:
                execute(
                    "INSERT INTO medicines(name, dose, times, notes, created_at) VALUES(?,?,?,?,?)",
                    (name, dose, times, notes, now_iso()),
                )
        set_setting("seeded", "1")
