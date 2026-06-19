# Contributing Guide

This is an internal team project with four module owners. This doc keeps everyone working in parallel without stepping on each other's code.

## Module Ownership (see README for details)

| Branch prefix | Owner | Module |
|---|---|---|
| `model/` | Mihir S. Joshi | AI Model Optimization & Edge Inference |
| `hardware/` | Dev Tiwari | Embedded Hardware & Device Integration |
| `system/` | Saarang Agarwal | System Software, Monitoring & Data Management |
| `dataset/` | Navya B. Kommuri | Dataset Engineering, AI Training & Validation |

## Branching

- Never commit directly to `main`.
- Create a feature branch using your module prefix:
  ```bash
  git checkout -b model/quantize-yolov8n
  git checkout -b hardware/gpio-buzzer-control
  git checkout -b system/sqlite-logging
  git checkout -b dataset/augmentation-pipeline
  ```
- Keep branches scoped to one feature/fix at a time.

## Commit Messages

Use a short prefix + clear summary:

```
[model] Add INT8 quantization script for YOLOv8-Nano
[hardware] Implement PWM buzzer trigger on GPIO 18
[system] Add SQLite schema for detection event logging
[dataset] Add brightness/rotation augmentation transforms
```

## Pull Requests

1. Push your branch and open a PR into `main`.
2. Fill in the PR template (what changed, how to test, screenshots/logs if relevant).
3. Tag at least one other module owner for review — cross-module review catches integration issues early (e.g. the inference output format the system module expects).
4. Squash-merge once approved.

## Code Style

- **Python:** follow PEP8. Run `black` and `flake8` before committing if installed (see `requirements.txt`).
- **Config over hardcoding:** thresholds, paths, and camera settings belong in `config/`, not hardcoded in scripts.
- **No large binary files in git:** trained models (`.pt`, `.onnx`, `.engine`) and datasets go in `models/` and `data/`, which are gitignored — share these via a shared drive or release artifact instead, and document the download link in the relevant module's README.

## Testing

- Add unit tests under `tests/` for any non-trivial logic (pre-processing, threshold logic, GPIO mocks).
- Hardware-dependent code (GPIO, camera) should be mockable so it can run in CI without a physical Jetson.

## Issues

Use the issue templates under `.github/ISSUE_TEMPLATE/` for bugs and feature requests. Label issues with the module they belong to (`model`, `hardware`, `system`, `dataset`).
