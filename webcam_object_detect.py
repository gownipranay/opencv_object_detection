import cv2
import numpy as np
import time

# Load class labels MobileNetSSD was trained on
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Random colors for each class
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# Load the serialized model from disk
print("[INFO] Loading MobileNetSSD model...")
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt",
                               "MobileNetSSD_deploy.caffemodel")
print("[INFO] Model loaded successfully!")

# Initialize webcam (0 = default camera)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Cannot access webcam!")
    exit()

print("[INFO] Starting camera... Press 'q' to quit, 's' to save snapshot.")

saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to grab frame.")
        break

    # Get frame dimensions
    (h, w) = frame.shape[:2]

    # Prepare the frame as a blob for the DNN
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)

    # Set blob as input and get detections
    net.setInput(blob)
    detections = net.forward()

    # Loop over detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            idx = int(detections[0, 0, i, 1])
            label = CLASSES[idx] if idx < len(CLASSES) else "Unknown"

            # Compute bounding box coordinates
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Draw the prediction
            color = COLORS[idx]
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            text = f"{label}: {confidence * 100:.2f}%"
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, text, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Show output frame
    cv2.imshow("Object Detection (press 'q' to quit, 's' to save)", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print("[INFO] Quitting...")
        break
    elif key == ord("s"):
        saved_count += 1
        filename = f"snapshot_{saved_count}.jpg"
        cv2.imwrite(filename, frame)
        print(f"[INFO] Saved {filename}")

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("[INFO] Detection finished.")
