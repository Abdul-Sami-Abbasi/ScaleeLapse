from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def isolated_media(settings):
    settings.MEDIA_ROOT = Path(__file__).resolve().parents[1] / "artifacts/test-media"
