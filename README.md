# opencv_object_detection
Model Information

This project uses the MobileNetSSD (Single Shot MultiBox Detector) model trained on the COCO dataset.
You need two model files (place them in the same folder as your Python script):

MobileNetSSD_deploy.prototxt

MobileNetSSD_deploy.caffemodel

You can download them from trusted sources such as:

Hugging Face Model File

Kaggle Dataset

Run the Project

Run the following command in your terminal:

python webcam_object_detect.py


If everything is set up correctly:

Your webcam will open.

Objects in front of the camera will be detected and labeled in real-time.

Controls
Key	Action
q	Quit webcam
s	Save current frame as snapshot_X.jpg
How It Works

The webcam feed is read using OpenCV.

Each frame is passed through MobileNetSSD using OpenCV’s DNN module.

Detected objects are labeled with confidence scores.

The frame is displayed in real-time with bounding boxes drawn.

Future Enhancements

Integrate YOLOv8 or DETR for higher accuracy

Deploy on a web dashboard using Streamlit

Add text-to-speech alerts for specific objects

## Jarvis: a rule-based phone assistant

This repo also includes `jarvis/`, an offline, rule-based "Jarvis"-style
assistant you can run on your phone (via Termux) or on a PC. It understands
commands like time/date, calculator, notes, reminders/timers, device
control (battery, flashlight, calls, SMS), opening apps/websites, and "what
do you see" (which reuses the MobileNetSSD detector above through your
camera). No API keys, no cloud services, no ML for its command
understanding — just regular expressions and Python. See
[`jarvis/README.md`](jarvis/README.md) for setup and the full command list.

GOWNI PRANAY-BTech(CSE-AIML)
