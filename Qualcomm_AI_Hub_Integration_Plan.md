# Qualcomm AI Hub Integration Plan

## Goal
Move one or more AI-heavy perception components from the prototype to an optimized Snapdragon execution path.

## Candidate components
1. Text/vision understanding model for screen regions.
2. Face/object detection model.
3. Optional image-to-text model for OCR-like visual understanding.

## Workflow
1. Select a compatible model in Qualcomm AI Hub.
2. Target the actual Snapdragon HP device family where available.
3. Quantize/compile using Qualcomm AI Hub Workbench.
4. Export a deployable asset.
5. Integrate using ONNX Runtime or Qualcomm AI Runtime as appropriate.
6. Test on the physical laptop.
7. Record execution provider, latency, memory and accuracy.
8. Add only verified measurements to the final pitch.

## Evidence to capture for the competition
- Screenshot of the AI Hub model page/job.
- Device model and Windows version.
- Runtime and execution provider.
- Inference time.
- Peak memory.
- Before/after example.
- A short screen recording of the application.

## Why this is credible
Qualcomm documents AI Hub Workbench as a tool to optimize, validate and deploy models on Qualcomm devices, and its model catalog exposes Snapdragon X Elite, X Plus 8-Core and X2 Elite targets plus ONNX Runtime and Qualcomm AI Runtime options.
