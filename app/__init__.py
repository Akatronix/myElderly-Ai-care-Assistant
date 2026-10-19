import os

from flask import Flask

from config import Config

from . import db as database
from .i18n import LANGUAGES, js_bundle, translate


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    os.makedirs(app.config["GENERATED_DIR"], exist_ok=True)

    database.init_app(app)

    from .routes.api import bp as api_bp
    from .routes.pages import bp as pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    from . import seed

    seed.run(app)

    @app.context_processor
    def inject_globals():
        from .db import get_setting
        from .utils import current_lang

        lang = current_lang()
        html_lang = next((l["html"] for l in LANGUAGES if l["code"] == lang), "en")
        return {
            "lang": lang,
            "html_lang": html_lang,
            "languages": LANGUAGES,
            "elder_name": get_setting("elder_name", "Mama"),
            "t": lambda key, **kw: translate(key, lang, **kw),
            "i18n_bundle": js_bundle(lang),
            "hr_range": app.config["HR_RANGE"],
            "temp_range": app.config["TEMP_RANGE"],
        }

    return app
