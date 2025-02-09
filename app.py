from flask import Flask, render_template, Response
import cv2
import pyttsx3
import yaml
import time
import threading
import onnx
import onnxruntime as ort
import numpy as np

app = Flask(__name__)

# Load the label mapping from the YAML file
with open("yaml.yaml") as file:
    label_mapping = yaml.load(file, Loader=yaml.FullLoader)["labels"]

# Initialize ONNX model with ONNX Runtime
onnx_model_path = "best_model.onnx"
ort_session = ort.InferenceSession(onnx_model_path)

# Dictionary to manage timers for each detected currency
label_timers = {}

# Lock for threading to avoid concurrent access issues with text-to-speech
speak_lock = threading.Lock()

# Function for text-to-speech
def speak(text):
    try:
        engine = pyttsx3.init()  # Initialize a new engine instance for each call
        engine.say(text)
        engine.runAndWait()
        engine.stop()  # Clean up the engine after use
        print(f"Spoken: {text}")
    except Exception as e:
        print(f"Error in speak function: {e}")

# Function to preprocess the image before passing it to the ONNX model
def preprocess_image(image):
    # Resize the image to match input size of the model (example: 640x640)
    image_resized = cv2.resize(image, (640, 640))
    # Normalize the image (if required)
    image_normalized = image_resized.astype(np.float32) / 255.0
    # Convert to the model's expected input shape (batch, height, width, channels)
    image_transposed = np.transpose(image_normalized, (2, 0, 1))  # Convert to CHW format
    image_input = np.expand_dims(image_transposed, axis=0)  # Add batch dimension
    return image_input

# Function to detect currency from an image using ONNX model
def detect_currency(image):
    global label_timers

    # Preprocess the image for the ONNX model
    image_input = preprocess_image(image)

    # Run the ONNX model
    ort_inputs = {ort_session.get_inputs()[0].name: image_input}
    ort_outputs = ort_session.run(None, ort_inputs)

    # Process the output (assuming the model returns bounding boxes and class IDs)
    output = ort_outputs[0]  # Assuming the output is in a format like [num_detections, 6] (bbox, class_id, confidence)

    label = "No currency detected"
    boxes = []
    detected_classes = []

    # Process the detection results (you may need to adapt this based on your model's output format)
    for detection in output[0]:
        if detection[4] > 0.5:  # Confidence threshold (you can adjust this)
            xmin, ymin, xmax, ymax = detection[0:4]
            class_id = int(detection[5])
            boxes.append([xmin, ymin, xmax, ymax])
            detected_classes.append(class_id)

    if detected_classes:
        label_index = detected_classes[0]
        label = label_mapping[label_index] if label_index < len(label_mapping) else "Unknown currency"

    # Draw bounding boxes on the frame
    for box in boxes:
        xmin, ymin, xmax, ymax = map(int, box)
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        cv2.putText(image, str(label), (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Manage timing for speaking detected currency labels
    current_time = time.time()
    if label != "No currency detected":
        if label not in label_timers:
            label_timers[label] = current_time
            print(f"Timer started for {label}")
        elif current_time - label_timers[label] >= 2:
            threading.Thread(target=speak, args=(label,), daemon=True).start()
            label_timers[label] = current_time  # Reset timer after speaking
            print(f"Triggered speak for {label} and reset timer")
    elif label in label_timers:
        del label_timers[label]  # Remove timer if no currency is detected
        print(f"Removed timer for {label}")
    return label

# Function to capture video frames and process them for currency detection
def generate_frames():
    cap = cv2.VideoCapture(0)  # Open the webcam
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break
        detect_currency(frame)  # Detect currency in each frame
        _, buffer = cv2.imencode(".jpg", frame)  # Convert frame to JPEG format
        frame = buffer.tobytes()  # Convert frame to bytes
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")  # Yield the frame to the frontend

    cap.release()

# Route to render the main page
@app.route("/")
def index():
    return render_template("index.html")

# Route to stream the video feed to the browser
@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
