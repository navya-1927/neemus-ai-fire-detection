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
        cfg = yaml.safe_load(f) or {}

    # Backwards compatibility: some configs place confidence_threshold under
    # `detection:` while tests and code expect it under `model:`. Ensure the
    # value is available at config['model']['confidence_threshold'] without
    # overwriting an explicit model setting.
    if "model" not in cfg or cfg["model"] is None:
        cfg["model"] = {}

    if "confidence_threshold" not in cfg["model"]:
        # Prefer detection.confidence_threshold if present
        detection_conf = None
        if isinstance(cfg.get("detection"), dict):
            detection_conf = cfg["detection"].get("confidence_threshold")

        if detection_conf is not None:
            cfg["model"]["confidence_threshold"] = detection_conf
        else:
            # Fallback default used by tests and as a sensible default
            cfg["model"]["confidence_threshold"] = 0.6

    return cfg
