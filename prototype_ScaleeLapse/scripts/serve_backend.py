"""Local development entry point; uses project-local PostgreSQL when initialized."""

import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
password_file = ROOT / ".runtime/pgpass.txt"
if password_file.exists() and not os.getenv("SCALEELAPSE_SQLITE"):
    os.environ.setdefault("POSTGRES_HOST", "127.0.0.1")
    os.environ.setdefault("POSTGRES_PORT", "55432")
    os.environ.setdefault("POSTGRES_DB", "scaleelapse")
    os.environ.setdefault("POSTGRES_USER", "scaleelapse")
    os.environ.setdefault("POSTGRES_PASSWORD", password_file.read_text().strip())
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".runtime/matplotlib"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")
from django.core.management import execute_from_command_line

execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000", "--noreload"])
