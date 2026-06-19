"""Shared configuration loading helper."""

from pathlib import Path
import yaml


def load_config(config_path: str = "config/default.yaml") -> dict:
    """Load a YAML config file into a dict.

    Args:
        config_path: path to the YAML config file.

    Returns:
        Parsed config as a dictionary.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r") as f:
        return yaml.safe_load(f)
