from flask import Flask, render_template, Response, request, redirect, jsonify
import cv2
import pyttsx3
import yaml
import time
import threading
import os
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO("best_model.pt")

with open("yaml.yaml") as file:
    label_mapping = yaml.load(file, Loader=yaml.FullLoader)["labels"]

label_timers = {}
speak_lock = threading.Lock()

def speak(text):
    """Speak detected currency using text-to-speech."""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        print(f"Spoken: {text}")
    except Exception as e:
        print(f"Error in speak function: {e}")

def detect_currency(image):
    """Run YOLO on the frame and draw bounding boxes."""
    global label_timers
    results = model(image)
    label = "No currency detected"

    if results[0].boxes:
        detected_classes = []
        boxes = []

        for result in results[0].boxes.data:
            xmin, ymin, xmax, ymax, conf, class_id = result.tolist()
            detected_classes.append(int(class_id))
            boxes.append([xmin, ymin, xmax, ymax])

        if detected_classes:
            label_index = detected_classes[0]
            label = label_mapping.get(label_index, "Unknown currency")

        for i, box in enumerate(boxes):
            xmin, ymin, xmax, ymax = map(int, box)
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    current_time = time.time()

    if label != "No currency detected":
        if label not in label_timers:
            label_timers[label] = current_time
        elif current_time - label_timers[label] >= 2:
            threading.Thread(target=speak, args=(label,), daemon=True).start()
            label_timers[label] = current_time
    elif label in label_timers:
        del label_timers[label]

    return label, image

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@app.route("/video_feed", methods=["POST"])
def video_feed():
    """Receive video frames from frontend, process them, and return processed images."""
    try:
        file = request.files["frame"]
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        _, processed_frame = detect_currency(frame)

        _, buffer = cv2.imencode(".jpg", processed_frame)
        return Response(buffer.tobytes(), mimetype="image/jpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.before_request
def enforce_https():
    """Redirect HTTP requests to HTTPS (only when deployed)."""
    if "RENDER" in os.environ:  # Only enforce HTTPS on Render
        if request.headers.get("X-Forwarded-Proto", "http") != "https":
            return redirect(request.url.replace("http://", "https://"), code=301)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Allow Render to assign port dynamically
    app.run(host="0.0.0.0", port=port, debug=True)
