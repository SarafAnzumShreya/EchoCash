from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import base64
import numpy as np
import yaml
import time
import threading
from ultralytics import YOLO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', compression_threshold=1024)

# Load the YOLO model
model = YOLO("best_model.pt")

# Load label mappings
with open("yaml.yaml") as file:
    label_mapping = yaml.safe_load(file)["labels"]

label_timers = {}  # Store the last detected timestamp for each label

def detect_currency(image):
    global label_timers
    results = model(image)
    detected_label = "No currency detected"
    speak = False  # Default: Don't trigger voice feedback

    if results[0].boxes:
        detected_classes = [int(box[-1]) for box in results[0].boxes.data]
        if detected_classes:
            detected_label = label_mapping.get(detected_classes[0], "Unknown currency")

            # Check if this label was detected for 3+ seconds
            current_time = time.time()
            if detected_label in label_timers:
                elapsed_time = current_time - label_timers[detected_label]
                if elapsed_time >= 3:
                    speak = True  # Trigger voice feedback
                    label_timers.clear()  # Reset timer after speaking

            else:
                label_timers[detected_label] = current_time
        else:
            detected_label = "No currency detected"
    else:
        detected_label = "No currency detected"

    print(f"Detected: {detected_label}, Speak: {speak}")  # Debugging line

    return {"label": detected_label, "speak": speak}


# A function to process frames in a separate thread
def process_frame(image_data):
    try:
        image_data = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Check if the frame is valid
        if frame is None or frame.size == 0:
            print("Invalid frame received. Skipping processing.")
            return

        # Call detect_currency and send result
        result = detect_currency(frame)
        print("Emitting result:", result)  # Debugging line
        socketio.emit("result", result)  # Send result back to frontend
    except Exception as e:
        print(f"Error processing frame: {e}")


@socketio.on("frame")
def handle_frame(data):
    print("Received frame from client:", data[:10])  # Print part of the image data for debugging
    threading.Thread(target=process_frame, args=(data,)).start()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


