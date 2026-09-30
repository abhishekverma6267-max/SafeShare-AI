# SafeShare AI

**On-Device AI Privacy Guardian for Screen Sharing**

SafeShare AI is a prototype that scans screenshots locally for potentially sensitive information before screen sharing. It detects text-based PII patterns, faces and QR codes, calculates a privacy-risk score, draws findings, and produces a protected screenshot.

## Why this fits the Snapdragon AI challenge

The application is designed around local inference and a Snapdragon optimization path. Qualcomm AI Hub supports computer-vision and multimodal models and lists Snapdragon X Elite, Snapdragon X Plus 8-Core and Snapdragon X2 Elite targets, with runtimes including ONNX Runtime and Qualcomm AI Runtime.

The repository intentionally separates the application/privacy logic from the model-runtime layer so an AI Hub-optimized ONNX model can be substituted and profiled on a compatible Snapdragon HP PC.

## Important claim policy

This repository does **not** claim that NPU execution has been completed unless the final build is tested on the participant's actual Snapdragon-powered HP laptop. Add real device name, runtime/execution provider and measured latency only after testing.

## Run

1. Install Python.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR separately if text PII detection is required.
5. Start:

```bash
streamlit run app.py
```

## Features

- Screenshot upload
- Local OCR-based PII pattern detection
- Face detection
- QR detection
- Privacy risk score
- Bounding-box annotation
- Blur / blackout / pixelate protection
- CSV privacy report
- AI Hub/ONNX deployment-ready architecture

## Suggested Snapdragon integration

Use Qualcomm AI Hub Workbench to select and optimize a supported model for the target Snapdragon device/runtime, then integrate the exported deployable asset through a supported runtime such as ONNX Runtime or Qualcomm AI Runtime. Profile on-device execution and document the actual execution provider and measurements.

## Project structure

```text
SafeShare-AI/
├── app.py
├── requirements.txt
├── README.md
├── src/
├── docs/
├── presentation/
├── assets/
└── tests/
```
