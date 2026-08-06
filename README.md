# 🔥 AI Fire Detection — Embedded Real-Time Flame & Smoke Detection

An embedded AI system that detects flame and smoke signatures in real time using a lightweight deep learning model (YOLOv8-Nano / MobileNet) running on an NVIDIA Jetson Nano, with automated buzzer/LED/relay alarm integration.

Built to replace traditional smoke/heat detectors — which have high false-alarm rates and no visual intelligence — with on-device, low-power, low-latency computer vision.

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

- **Real-time detection** of flame and smoke from live camera feed
- **Edge inference** — no server/cloud round-trip, fully on-device
- **Automated alarm response** — buzzer, LED, and relay trigger on detection
- **Optimized model** — INT8 quantized, pruned, exported to TensorRT/ONNX for fast inference on constrained hardware
- **Logging & monitoring** — local SQLite logging with optional web dashboard
- **Modular hardware integration** — supports CSI camera, IR sensor, GPIO peripherals, optional ESP32 extension

## System Architecture

```
INPUT LAYER          PROCESSING LAYER         DECISION LAYER           OUTPUT LAYER
─────────────        ──────────────────       ──────────────────       ──────────────────
Camera / IR    ──►    Pre-processing      ──►  Confidence Threshold ──► Buzzer / LED Alarm
Video Capture         AI Inference Engine      Alert Classification     Display / Log Output
Frame Buffer          Flame/Smoke Model        Trigger Logic            Serial / MQTT Alert
```

**Inference pipeline:** Frame capture (GStreamer) → Pre-processing (resize 416×416, normalize) → YOLOv8-Nano TensorRT inference → Non-Maximum Suppression → Confidence check (>0.6) → Alarm trigger or loop to next frame.

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

Wiring diagram: [`hardware/wiring_diagrams/`](hardware/wiring_diagrams/).

## Repository Structure

```
ai-fire-detection/
├── src/
│   ├── dashboard         # Contains code for a real-time dashboard.
│   ├── inference/        # Real-time inference pipeline (camera → model → alarm)
│   ├── training/         # Dataset prep, training, evaluation scripts
│   └── utils/            # Shared helpers (logging, config loading, GPIO control)
├── models/               # Trained weights / exported .onnx, .engine files (gitignored)
├── hardware/
│   ├── firmware/          # ESP32 / GPIO firmware code (if used)
│   └── wiring_diagrams/   # Circuit & block diagrams
├── config/                # YAML/JSON config files (thresholds, camera settings)
├── scripts/               # One-off setup / deployment scripts
├── tests/                 # Unit tests
├── sample_data/           # Contains sample data and output the model was tested on.
├── .github/               # Issue templates, CI workflows
├── seed_data.py           # Database logger code
├── start_neemus.bat       # Code to activate dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- NVIDIA Jetson Nano (4GB) flashed with JetPack 4.6.x, **or** a development machine with Python 3.8+ and a webcam for early prototyping
- Python 3.8+
- (On Jetson) CUDA-enabled OpenCV and TensorRT pre-installed via JetPack

### Setup & Installation

Follow these steps to configure your local environment and run the hardware simulation and inference pipeline.

First, download the project to your local machine and enter the directory:
```bash
# Clone the Repository
git clone https://github.com/navya-1927/neemus-ai-fire-detection.git
cd neemus-ai-fire-detection

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Download and unzip the fire detection and classification datasets from HuggingFace: https://huggingface.co/datasets/navya-1927/neemus-ai-fire-detection-dataset

### Running inference (once a model is trained/placed in `models/`)

```bash
python src/inference/run_inference.py --config config/default.yaml
```

## Dataset Details

Two datasets have been used: one for fire detection and one for fire classification.

### Fire Detection Dataset Details:
Source: https://github.com/gaia-solutions-on-demand/DFireDataset/tree/master <br>
Number of images:
- only fire: 1164
- only smoke: 5867
- both fire and smoke: 4658
- nothing: 9838 <br>
total: 21527 <br>

train/test/val split:
- train: 15068 (70%)
- val: 2153 (10%)
- test: 4306 (20%) <br>

<p> the train, val and test folders contain two folders: images and labels. labels contains the normalised bounding box coordinates for each image. 0 stands for smoke and 1 stands for fire. </p>

### Fire Classification Dataset Details
Source: https://universe.roboflow.com/rutuja-t3xz4/fire-classification-up72t <br>
Number of images:
- Chemical: 29 images
- Electrical: 159 images
- Explosive: 45 images
- Cooking Oils/Fats: 230
- Flammable Liquids: 223
- Solid Combustibles: 519
- Flashover: 24 images
- Hydrocarbon Pool: 80
- Warehouse: 82 images
- Wild/Bush Fires: 604 <br>
total: 1995 <br>

train/test/val split:
- train: 1396 (70%)
- val: 200 (10%)
- test: 399 (20%) <br>

<p> YOLO augments images before training by default. </p>

## Team & Module Ownership

| Member | Module |
|---|---|
| **Mihir S. Joshi** | AI Model Optimization & Edge Inference — model selection, quantization/pruning, TensorRT/ONNX conversion, FPS/latency benchmarking |
| **Dev Tiwari** | Embedded Hardware & Device Integration — Jetson setup, camera/GPIO, buzzer/LED/relay control, firmware |
| **Saarang Agarwal** | System Software, Monitoring & Data Management — real-time workflow integration, alerting, logging, dashboard, deployment |
| **Navya B. Kommuri** | Dataset Engineering, AI Training & Validation — data collection/annotation, augmentation, training, accuracy analysis, threshold tuning |

---
