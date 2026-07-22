"""
config_loader.py
Owned by: Saarang Agarwal (System Software, Monitoring & Data Management)

Tiny wrapper so every module reads settings the same way instead of
hardcoding thresholds/paths (per CONTRIBUTING.md: "Config over hardcoding").
"""

import yaml


def load_config(path: str = "config/default.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)
