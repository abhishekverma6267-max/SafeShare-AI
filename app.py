import re
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter

st.set_page_config(page_title="SafeShare AI", page_icon="🔐", layout="wide")

st.title("🔐 SafeShare AI")
st.caption("On-device privacy guardian for screen sharing")

st.markdown("""
SafeShare AI analyzes a screenshot locally and identifies potentially sensitive
content before you share your screen. The prototype is designed with an
on-device-first architecture and an optional Qualcomm AI Hub/ONNX deployment path.
""")

PII_PATTERNS = {
    "Email address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "Phone number": r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",
    "API key / secret-like token": r"\b(?:sk-[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{20,})\b",
    "Long numeric identifier": r"\b\d{10,16}\b",
}

@st.cache_resource
def load_face_detector():
    path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    return cv2.CascadeClassifier(path)

def detect_qr(image_bgr):
    detector = cv2.QRCodeDetector()
    try:
        value, points, _ = detector.detectAndDecode(image_bgr)
        if points is not None:
            pts = points[0].astype(int)
            x, y, w, h = cv2.boundingRect(pts)
            return [{"type": "QR code", "text": value or "QR code detected",
                     "bbox": (x, y, w, h), "severity": "high"}]
    except Exception:
        pass
    return []

def detect_faces(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    faces = load_face_detector().detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return [{"type": "Face", "text": "Face detected", "bbox": tuple(map(int, f)),
             "severity": "medium"} for f in faces]

def ocr_text(image):
    # Optional OCR. The app still works without Tesseract.
    try:
        import pytesseract
        return pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    except Exception:
        return None

def detect_pii(image):
    data = ocr_text(image)
    findings = []
    if data is None:
        return findings, "OCR is not installed. Install Tesseract + pytesseract for text PII detection."
    for i, text in enumerate(data.get("text", [])):
        text = (text or "").strip()
        if not text:
            continue
        x, y, w, h = [int(data[k][i]) for k in ("left", "top", "width", "height")]
        for kind, pattern in PII_PATTERNS.items():
            if re.search(pattern, text, re.I):
                findings.append({
                    "type": kind, "text": text, "bbox": (x, y, w, h),
                    "severity": "high" if "API" in kind or "identifier" in kind else "medium"
                })
    return findings, "OCR scan completed."

def redact(image, findings, mode="Blur"):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    for f in findings:
        x, y, w, h = f["bbox"]
        box = (max(0,x), max(0,y), min(out.width,x+w), min(out.height,y+h))
        if mode == "Blackout":
            draw.rectangle(box, fill=(0,0,0))
        elif mode == "Pixelate":
            crop = out.crop(box)
            small = crop.resize((max(1,crop.width//12), max(1,crop.height//12)))
            pix = small.resize(crop.size, Image.Resampling.NEAREST)
            out.paste(pix, box)
        else:
            crop = out.crop(box).filter(ImageFilter.GaussianBlur(radius=14))
            out.paste(crop, box)
    return out

def annotate(image, findings):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    for f in findings:
        x,y,w,h = f["bbox"]
        draw.rectangle((x,y,x+w,y+h), outline=(255,60,60), width=4)
        draw.text((x, max(0,y-18)), f["type"], fill=(255,60,60))
    return out

uploaded = st.file_uploader("Upload a screenshot to scan", type=["png","jpg","jpeg","webp"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(image, use_container_width=True)

    with st.spinner("Running local privacy scan..."):
        pii, ocr_status = detect_pii(image)
        faces = detect_faces(bgr)
        qrs = detect_qr(bgr)
        findings = pii + faces + qrs

    with col2:
        st.subheader("Detected")
        st.image(annotate(image, findings), use_container_width=True)

    high = sum(f["severity"] == "high" for f in findings)
    medium = sum(f["severity"] == "medium" for f in findings)
    score = min(100, high*25 + medium*12)
    level = "HIGH" if score >= 60 else "MEDIUM" if score >= 25 else "LOW"

    st.metric("Privacy Risk", f"{level} ({score}/100)")
    st.caption(ocr_status)

    if findings:
        df = pd.DataFrame([{
            "Type": f["type"], "Detected value": f["text"],
            "Severity": f["severity"], "X": f["bbox"][0], "Y": f["bbox"][1],
            "Width": f["bbox"][2], "Height": f["bbox"][3]
        } for f in findings])
        st.dataframe(df, use_container_width=True)

        mode = st.selectbox("Protection mode", ["Blur", "Blackout", "Pixelate"])
        protected = redact(image, findings, mode)
        st.subheader("Protected Screenshot")
        st.image(protected, use_container_width=True)

        buf = BytesIO()
        protected.save(buf, format="PNG")
        st.download_button("Download protected screenshot", buf.getvalue(),
                           "safeshare_protected.png", "image/png")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download privacy report (CSV)", csv,
                           "safeshare_report.csv", "text/csv")
    else:
        st.success("No supported sensitive patterns were detected in this scan.")

st.divider()
st.caption("Prototype note: core scanning runs locally. For the competition submission, Snapdragon/NPU execution must be validated on the actual target HP Snapdragon PC before claiming measured NPU performance.")
