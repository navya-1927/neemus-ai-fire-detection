# 🔥 AI Fire Detection — Embedded Real-Time Flame & Smoke Detection

An embedded AI system that detects flame and smoke signatures in real time using a lightweight deep learning model (YOLOv8-Nano / MobileNet) running on an NVIDIA Jetson Nano, with automated buzzer/LED/relay alarm integration.

> Built to replace traditional smoke/heat detectors — which have high false-alarm rates and no visual intelligence — with on-device, low-power, low-latency computer vision.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Hardware Requirements](#hardware-requirements)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Project Roadmap](#project-roadmap)
- [Team](#team--module-ownership)
- [Documentation](#documentation)
- [Status](#status)

---

## Overview

Traditional fire/smoke detectors are reactive, slow in large or outdoor spaces, and can't visually distinguish flame from steam or dust. This project builds an **edge AI** solution: a camera-equipped embedded device that runs a quantized object detection model directly on-device (no cloud dependency) to identify flame and smoke signatures and trigger an alarm in real time.

**Target performance:**
- ≥ 90% detection accuracy
- ≥ 15 FPS real-time inference
- Runs entirely on-device (Jetson Nano 4GB)
- Low power draw (battery/solar-deployable)

## Key Features

- 🎯 **Real-time detection** of flame and smoke from live camera feed
- ⚡ **Edge inference** — no server/cloud round-trip, fully on-device
- 🔔 **Automated alarm response** — buzzer, LED, and relay trigger on detection
- 📉 **Optimized model** — INT8 quantized, pruned, exported to TensorRT/ONNX for fast inference on constrained hardware
- 📊 **Logging & monitoring** — local SQLite logging with optional web dashboard
- 🔌 **Modular hardware integration** — supports CSI camera, IR sensor, GPIO peripherals, optional ESP32 extension

## System Architecture

```
INPUT LAYER          PROCESSING LAYER         DECISION LAYER           OUTPUT LAYER
─────────────        ──────────────────       ──────────────────       ──────────────────
Camera / IR    ──►    Pre-processing      ──►  Confidence Threshold ──► Buzzer / LED Alarm
Video Capture         AI Inference Engine      Alert Classification     Display / Log Output
Frame Buffer          Flame/Smoke Model        Trigger Logic            Serial / MQTT Alert
```

**Inference pipeline:** Frame capture (GStreamer) → Pre-processing (resize 416×416, normalize) → YOLOv8-Nano TensorRT inference → Non-Maximum Suppression → Confidence check (>0.6) → Alarm trigger or loop to next frame.

See [`docs/proposal/`](docs/proposal/) for full architecture diagrams and the original technical proposal.

## Tech Stack

| Layer | Tool / Library | Version |
|---|---|---|
| OS / Runtime | NVIDIA JetPack SDK | 4.6.x |
| AI Framework | YOLOv8 + TensorRT | YOLOv8.2 / TRT 8.x |
| Camera Pipeline | GStreamer + nvarguscamerasrc | Built-in |
| Computer Vision | OpenCV (CUDA-enabled) | 4.5.x |
| GPIO Control | Jetson.GPIO | Latest |
| Communication | MQTT | 1.6.x |
| Logging | SQLite3 + Python | Built-in |
| Model Training | Ultralytics + Google Colab | YOLOv8.2 |
| Model Export | ONNX → TensorRT (.engine) | On-device |
| Language | Python | 3.8 (JetPack default) |

## Hardware Requirements

- **Processing Unit:** NVIDIA Jetson Nano Developer Kit (4GB), GPU-accelerated
- **Camera:** IMX219-160 CSI camera (Jetson-compatible) — optional IR sensor for thermal input
- **Alarm/Output:** Piezo buzzer (PWM), RGB LED strip, 5V relay module
- **Power:** 5V/4A power supply
- **Storage:** MicroSD 64GB or SSD

Full part list and wiring diagram: [`docs/proposal/`](docs/proposal/) and [`hardware/wiring_diagrams/`](hardware/wiring_diagrams/).

## Repository Structure

```
ai-fire-detection/
├── src/
│   ├── inference/        # Real-time inference pipeline (camera → model → alarm)
│   ├── training/         # Dataset prep, training, evaluation scripts
│   └── utils/            # Shared helpers (logging, config loading, GPIO control)
├── models/               # Trained weights / exported .onnx, .engine files (gitignored)
├── data/                 # Dataset used: DFire
│   ├── train/            # Number of images: 15068 (70%)
│   ├── val/              # Number of images: 2153 (10%)
│   └── test/             # Number of images: 4306 (20%)
├── hardware/
│   ├── firmware/          # ESP32 / GPIO firmware code (if used)
│   └── wiring_diagrams/   # Circuit & block diagrams
├── config/                 # YAML/JSON config files (thresholds, camera settings)
├── scripts/                 # One-off setup / deployment scripts
├── tests/                   # Unit tests
├── docs/
│   └── proposal/           # Original technical proposal & supporting docs
├── .github/                 # Issue templates, CI workflows
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- NVIDIA Jetson Nano (4GB) flashed with JetPack 4.6.x, **or** a development machine with Python 3.8+ and a webcam for early prototyping
- Python 3.8+
- (On Jetson) CUDA-enabled OpenCV and TensorRT pre-installed via JetPack

### Setup

```bash
# Clone the repo
git clone https://github.com/<your-username>/ai-fire-detection.git
cd ai-fire-detection

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running inference (once a model is trained/placed in `models/`)

```bash
python src/inference/run_inference.py --config config/default.yaml
```

See [`src/inference/run_inference.py`](src/inference/run_inference.py) for the current stub — this will be filled in as Phase 3 (Embedded Deployment) progresses.

## Dataset Details

Source: https://github.com/gaia-solutions-on-demand/DFireDataset/tree/master <br>
Number of images:
- only fire: 1164
- only smoke: 5867
- both fire and smoke: 4658
- nothing: 9838 <br>
total: 21527

<p> the train, val and test folders contain two folders: images and labels. labels contains the normalised bounding box coordinates for each image. 0 stands for smoke and 1 stands for fire. </p>

<p> YOLO augments images before training by default. </p>

## Project Roadmap

| Phase | Weeks | Milestone |
|---|---|---|
| 1 | 1–2 | Literature review, dataset collection & labeling, hardware setup |
| 2 | 3–6 | Train baseline CNN/YOLO model, evaluate, optimize (quantization & pruning) |
| 3 | 7–8 | Port model to edge runtime, integrate camera pipeline, hit ≥15 FPS |
| 4 | 9–11 | Wire GPIO alarms (buzzer, LED, relay), test end-to-end flow |
| 5 | 12–14 | Real-world fire/smoke testing, false-positive tuning, latency optimization |
| 6 | 15–16 | Final prototype, demo, and documentation |

Track active work in [Issues](../../issues) and [Projects](../../projects).

## Team & Module Ownership

| Member | Module |
|---|---|
| **Mihir S. Joshi** | AI Model Optimization & Edge Inference — model selection, quantization/pruning, TensorRT/ONNX conversion, FPS/latency benchmarking |
| **Dev Tiwari** | Embedded Hardware & Device Integration — Jetson setup, camera/GPIO, buzzer/LED/relay control, firmware |
| **Saarang Agarwal** | System Software, Monitoring & Data Management — real-time workflow integration, alerting, logging, dashboard, deployment |
| **Navya B. Kommuri** | Dataset Engineering, AI Training & Validation — data collection/annotation, augmentation, training, accuracy analysis, threshold tuning |

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branch/workflow conventions per module.

## Documentation

- 📄 [Technical Proposal (original PDF, converted)](docs/proposal/) — full problem statement, objectives, architecture, and team experience
- 📄 [Work Assignment](docs/proposal/) — module breakdown per team member

## Status

🚧 **Early development — Phase 1.** Repository scaffolding in progress; no trained model yet.

---

*Internal project — no license applied yet. Do not distribute outside the team until a license is added.*
