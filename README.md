# OpenCV Object Detection

A real-time object detection application built with Python and OpenCV. It uses a
pre-trained MobileNet-SSD deep learning model to detect and label everyday objects
(people, vehicles, animals, furniture, etc.) live from your webcam feed, drawing
bounding boxes and confidence scores directly on the video.

## Features

- Real-time object detection from a live webcam feed
- Detects 20 common object classes (see below)
- Draws bounding boxes, labels, and confidence scores on screen
- Save any frame as a snapshot with a single keypress
- Lightweight — runs on CPU using OpenCV's DNN module (no GPU required)

## Model Information

This project uses **MobileNet-SSD** (Single Shot MultiBox Detector), a lightweight
deep learning model trained on the COCO dataset for fast object detection.

The model can detect the following 20 object classes:

`aeroplane, bicycle, bird, boat, bottle, bus, car, cat, chair, cow, diningtable,
dog, horse, motorbike, person, pottedplant, sheep, sofa, train, tvmonitor`

You need two model files, placed in the same folder as `webcam_object_detect.py`:

- `MobileNetSSD_deploy.prototxt` — the model architecture definition
- `MobileNetSSD_deploy.caffemodel` — the pre-trained model weights

These files are not included in this repository. Download them from a trusted
source such as Hugging Face or Kaggle and place them in the project root.

## Project Structure

```
opencv_object_detection/
├── webcam_object_detect.py   # Main script: captures webcam feed and runs detection
├── reuirements.txt           # Python dependencies
└── README.md
```

## Requirements

- Python 3.x
- A webcam

Dependencies (listed in `reuirements.txt`):

- `opencv-python`
- `numpy`
- `imutils`

Optional (for experimentation/analysis):

- `matplotlib`
- `jupyter`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/gownipranay/opencv_object_detection.git
   cd opencv_object_detection
   ```
2. Install the dependencies:
   ```
   pip install opencv-python numpy imutils
   ```
3. Download `MobileNetSSD_deploy.prototxt` and `MobileNetSSD_deploy.caffemodel`
   and place them in the project root.

## Usage

Run the script from the project root:

```
python webcam_object_detect.py
```

If everything is set up correctly, your webcam will open and detected objects
will be labeled in real-time with bounding boxes.

### Controls

| Key | Action                              |
|-----|--------------------------------------|
| `q` | Quit the webcam window               |
| `s` | Save the current frame as `snapshot_X.jpg` |

## How It Works

1. The webcam feed is read frame-by-frame using OpenCV.
2. Each frame is resized and converted into a blob, then passed through the
   MobileNet-SSD network via OpenCV's DNN module.
3. Detections above a confidence threshold (50%) are kept.
4. Bounding boxes and class labels with confidence scores are drawn on the frame.
5. The annotated frame is displayed in a live window until the user quits.

## Future Enhancements

- Integrate YOLOv8 or DETR for higher detection accuracy
- Deploy as a web dashboard using Streamlit
- Add text-to-speech alerts for specific detected objects

## Author

GOWNI PRANAY — B.Tech (CSE-AIML)
