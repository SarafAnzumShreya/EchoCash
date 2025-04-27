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

model = YOLO("best_model.pt")

with open("yaml.yaml") as file:
    label_mapping = yaml.safe_load(file)["labels"]

label_timers = {}  
last_spoken_label = None  
total_amounts = {
    "taka": 0,
    "dollar": 0,
    "euro": 0,
    "eurocent": 0
}
addition_history = []  # Tracks additions for cancel functionality

currency_values = {
    "1000taka": {"value": 1000, "type": "taka"},
    "100dollar": {"value": 100, "type": "dollar"},
    "100euro": {"value": 100, "type": "euro"},
    "100taka": {"value": 100, "type": "taka"},
    "10dollar": {"value": 10, "type": "dollar"},
    "10euro": {"value": 10, "type": "euro"},
    "10eurocent": {"value": 10, "type": "eurocent"},
    "10taka": {"value": 10, "type": "taka"},
    "1dollar": {"value": 1, "type": "dollar"},
    "1euro": {"value": 1, "type": "euro"},
    "1eurocent": {"value": 1, "type": "eurocent"},
    "1taka": {"value": 1, "type": "taka"},
    "200taka": {"value": 200, "type": "taka"},
    "20dollar": {"value": 20, "type": "dollar"},
    "20euro": {"value": 20, "type": "euro"},
    "20eurocent": {"value": 20, "type": "eurocent"},
    "20taka": {"value": 20, "type": "taka"},
    "2dollar": {"value": 2, "type": "dollar"},
    "2euro": {"value": 2, "type": "euro"},
    "2eurocent": {"value": 2, "type": "eurocent"},
    "2taka": {"value": 2, "type": "taka"},
    "500taka": {"value": 500, "type": "taka"},
    "50dollar": {"value": 50, "type": "dollar"},
    "50euro": {"value": 50, "type": "euro"},
    "50eurocent": {"value": 50, "type": "eurocent"},
    "50taka": {"value": 50, "type": "taka"},
    "5dollar": {"value": 5, "type": "dollar"},
    "5euro": {"value": 5, "type": "euro"},
    "5eurocent": {"value": 5, "type": "eurocent"},
    "5taka": {"value": 5, "type": "taka"}
}

def detect_currency(image):
    global label_timers, last_spoken_label
    
    if not model:
        print("No model loaded, skipping detection")
        return {"label": "Model not loaded", "speak": False, "totals": total_amounts}

    try:
        print("Running YOLO detection...")
        results = model(image)
        detected_label = "No currency detected"
        speak = False

        if results and results[0].boxes:
            detected_classes = [int(box[-1]) for box in results[0].boxes.data]
            print(f"Detected classes: {detected_classes}")
            if detected_classes:
                detected_label = label_mapping.get(detected_classes[0], "Unknown currency")

        current_time = time.time()

        if detected_label not in label_timers:
            label_timers.clear() 
            label_timers[detected_label] = current_time
            print(f"Timer started for {detected_label}")
        else:
            elapsed_time = current_time - label_timers[detected_label]
            if elapsed_time >= 3 and detected_label in currency_values:
                speak = True
                last_spoken_label = detected_label  
                label_timers[detected_label] = current_time  
                print(f"Speak triggered for {detected_label} after {elapsed_time:.2f}s")
            elif detected_label in currency_values:
                print(f"Waiting for {detected_label}, elapsed: {elapsed_time:.2f}s")
            else:
                print(f"Tracking {detected_label}, elapsed: {elapsed_time:.2f}s (no voice feedback)")
                
        if speak:
            label_timers.clear()
            label_timers[detected_label] = current_time

        print(f"Detection result - Label: {detected_label}, Speak: {speak}")
        return {"label": detected_label, "speak": speak, "totals": total_amounts}
    
    except Exception as e:
        print(f"Error in detect_currency: {e}")
        return {"label": "Detection error", "speak": False, "totals": total_amounts}

def process_frame(image_data):
    try:
        print("Decoding frame...")
        image_data = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None or frame.size == 0:
            print("Invalid frame received")
            socketio.emit("result", {"label": "Invalid frame", "speak": False, "totals": total_amounts})
            return

        print("Frame decoded successfully, processing with YOLO...")
        result = detect_currency(frame)
        socketio.emit("result", result)
    except Exception as e:
        print(f"Error processing frame: {e}")
        socketio.emit("result", {"label": "Processing error", "speak": False, "totals": total_amounts})

@socketio.on("frame")
def handle_frame(data):
    print("Received frame from client")
    threading.Thread(target=process_frame, args=(data,)).start()

@socketio.on("command")
def handle_command(data):
    global total_amounts, last_spoken_label, addition_history
    command = data.get("command")
    detected_label = data.get("label")
    print(f"Received command: {command}, label: {detected_label}")

    if command == "add":
        if detected_label == "No currency detected":
            print("No currency detected, adding zero")
        elif last_spoken_label and last_spoken_label in currency_values and detected_label == last_spoken_label:
            currency_info = currency_values[last_spoken_label]
            total_amounts[currency_info["type"]] += currency_info["value"]
            addition_history.append({"label": last_spoken_label, "type": currency_info["type"], "value": currency_info["value"]})
            print(f"Added {last_spoken_label}. New totals: {total_amounts}")
        else:
            print(f"Invalid or not yet spoken label: {detected_label}, skipping add (last spoken: {last_spoken_label})")
            return

        feedback = "the total is "
        if total_amounts["taka"] > 0:
            feedback += f"{total_amounts['taka']} Taka, "
        if total_amounts["dollar"] > 0:
            feedback += f"{total_amounts['dollar']} USD, "
        if total_amounts["euro"] > 0:
            feedback += f"{total_amounts['euro']} Euro, "
        if total_amounts["eurocent"] > 0:
            feedback += f"{total_amounts['eurocent']} Eurocents, "
        feedback = feedback.rstrip(", ")  
        if feedback == "the total is":  
            feedback = "the total is 0"
        
        socketio.emit("command_feedback", {"message": feedback})
        print("Command processed, detection continues, speaking total")
        label_timers.clear()
        socketio.emit("total_update", {"totals": total_amounts})
        
    elif command == "cancel":
        if addition_history:
            last_addition = addition_history.pop()
            total_amounts[last_addition["type"]] -= last_addition["value"]
            print(f"Canceled last addition: {last_addition['label']}. New totals: {total_amounts}")
            feedback = f"{last_addition['value']} {last_addition['type']} removed and the total is "
            if total_amounts["taka"] > 0:
                feedback += f"{total_amounts['taka']} Taka, "
            if total_amounts["dollar"] > 0:
                feedback += f"{total_amounts['dollar']} USD, "
            if total_amounts["euro"] > 0:
                feedback += f"{total_amounts['euro']} Euro, "
            if total_amounts["eurocent"] > 0:
                feedback += f"{total_amounts['eurocent']} Eurocents, "
            if (total_amounts["taka"] == 0 and 
                total_amounts["dollar"] == 0 and 
                total_amounts["euro"] == 0 and 
                total_amounts["eurocent"] == 0):
                feedback += " 0"
            feedback = feedback.rstrip(", ")
            if feedback == f"{last_addition['value']} {last_addition['type']} removed and The total is":
                feedback += " 0"
            
            socketio.emit("command_feedback", {"message": feedback})
            label_timers.clear()
        else:
            print("No additions to cancel")
            
            socketio.emit("command_feedback", {"message": "Nothing to cancel"})
            label_timers.clear()
            
        socketio.emit("total_update", {"totals": total_amounts})
        
    elif command == "reset":
        total_amounts = {"taka": 0, "dollar": 0, "euro": 0, "eurocent": 0}
        last_spoken_label = None  
        addition_history.clear()
        print("Totals reset to zero")
        socketio.emit("command_feedback", {"message": "canceled"})
        label_timers.clear()
        
    elif command == "start":
        total_amounts = {"taka": 0, "dollar": 0, "euro": 0, "eurocent": 0}
        last_spoken_label = None
        addition_history.clear()
        print("App started: Totals reset silently on client open")
        socketio.emit("total_update", {"totals": total_amounts})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    import os
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))