"""'What do you see?' -- runs the project's own MobileNetSSD detector on a
single camera frame. Same offline model used by webcam_object_detect.py at
the repo root, no cloud vision API involved.

On a phone (inside Termux) the frame is captured with `termux-camera-photo`
(part of Termux:API). On a desktop, it falls back to OpenCV's
`cv2.VideoCapture(0)` so the skill can also be exercised during development.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor",
]

_PROTOTXT = Path(__file__).resolve().parent.parent.parent / "MobileNetSSD_deploy.prototxt"
_MODEL = Path(__file__).resolve().parent.parent.parent / "MobileNetSSD_deploy.caffemodel"

_net = None
_net_load_failed = False


def _load_net():
    global _net, _net_load_failed
    if _net is not None or _net_load_failed:
        return _net
    if not (_PROTOTXT.exists() and _MODEL.exists()):
        _net_load_failed = True
        return None
    try:
        import cv2

        _net = cv2.dnn.readNetFromCaffe(str(_PROTOTXT), str(_MODEL))
    except Exception:
        _net_load_failed = True
        _net = None
    return _net


def _capture_frame():
    """Return a BGR numpy frame, or None if no camera is available."""
    import cv2

    if shutil.which("termux-camera-photo"):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "jarvis_capture.jpg"
            result = subprocess.run(
                ["termux-camera-photo", "-c", "0", str(out_path)],
                capture_output=True, timeout=15, check=False,
            )
            if result.returncode == 0 and out_path.exists():
                return cv2.imread(str(out_path))

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    ok, frame = cap.read()
    cap.release()
    return frame if ok else None


def _detect_labels(frame, confidence_threshold: float = 0.5) -> list[str]:
    import cv2
    import numpy as np

    net = _load_net()
    if net is None:
        return []

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    labels = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            idx = int(detections[0, 0, i, 1])
            if 0 <= idx < len(CLASSES) and CLASSES[idx] != "background":
                labels.append(CLASSES[idx])
    return labels


def _what_do_you_see(match, ctx) -> str:
    if not (_PROTOTXT.exists() and _MODEL.exists()):
        return (
            "I don't have my object-detection model files yet. Download "
            "MobileNetSSD_deploy.prototxt and MobileNetSSD_deploy.caffemodel "
            "into the project folder, as described in the main README."
        )
    try:
        frame = _capture_frame()
    except Exception as exc:
        return f"I couldn't access the camera: {exc}"
    if frame is None:
        return "I couldn't get a picture from the camera."

    labels = _detect_labels(frame)
    if not labels:
        return "I don't recognize anything in front of the camera right now."

    unique = sorted(set(labels), key=labels.index)
    if len(unique) == 1:
        return f"I can see a {unique[0]}."
    return "I can see: " + ", ".join(unique[:-1]) + f", and {unique[-1]}."


def register(engine) -> None:
    engine.register(
        "vision",
        r"\bwhat (do you see|can you see|('?s| is) in front of the camera)\b|\bdetect objects\b|\blook around\b",
        _what_do_you_see,
        "'what do you see' - run the camera object detector.",
    )
