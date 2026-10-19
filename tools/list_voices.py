"""Print the live YarnGPT voice catalogue so you can copy exact ids into .env.

Usage:  python tools/list_voices.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.services import voice  # noqa: E402

app = create_app()
with app.app_context():
    for v in voice.fetch_voices():
        print(v)
