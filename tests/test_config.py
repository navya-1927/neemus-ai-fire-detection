"""Tests for config loading utility."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.utils.config import load_config


def test_load_default_config():
    config = load_config("config/default.yaml")
    assert "model" in config
    assert "camera" in config
    assert "alarm" in config
    assert config["model"]["confidence_threshold"] == 0.6
