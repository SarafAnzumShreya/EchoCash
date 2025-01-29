from flask import Flask, render_template, Response
import cv2
import pyttsx3
import yaml
import time
import threading
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO("best_model.pt")

with open("yaml.yaml") as file:
    label_mapping = yaml.load(file, Loader=yaml.FullLoader)["labels"]

label_timers = {}
speak_lock = threading.Lock()

def speak(text):
    try:
        engine = pyttsx3.init()  # Initialize a new engine instance for each call
        engine.say(text)
        engine.runAndWait()
        engine.stop()  # Clean up the engine after use
        print(f"Spoken: {text}")
    except Exception as e:
        print(f"Error in speak function: {e}")

def detect_currency(image):
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
            label = label_mapping[label_index] if label_index < len(label_mapping) else "Unknown currency"

        for i, box in enumerate(boxes):
            xmin, ymin, xmax, ymax = map(int, box)
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(image, str(label), (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    current_time = time.time()

    if label != "No currency detected":
        if label not in label_timers:
            label_timers[label] = current_time
            print(f"Timer started for {label}")
        elif current_time - label_timers[label] >= 2:
            threading.Thread(target=speak, args=(label,), daemon=True).start()
            label_timers[label] = current_time # Correct: Reset AFTER speaking thread starts
            print(f"Triggered speak for {label} and reset timer")
    elif label in label_timers:
        del label_timers[label]
        print(f"Removed timer for {label}")
    return label

def generate_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break
        detect_currency(frame)
        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    cap.release()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
