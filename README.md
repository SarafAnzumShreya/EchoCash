# <p align="center"><strong>EchoCash</strong></p>

<p align="center">
  <img src="static/logo.jpg" alt="EchoCash Logo" style="width: 100px; height: auto;"/>
</p>

EchoCash is a machine learning project designed to assist visually impaired people by detecting currency. It can recognize USD (United States Dollar), EURO (Euro), and BDT (Bangladeshi Taka). Trained using YOLO (You Only Look Once) along with convolutional neural networks, it achieves a precision of 98.61%.

## How to Use This Model

This project is designed to be used on a mobile phone with a laptop/computer acting as the local server.

### Steps to Set Up:

1. **Download the Project**  
   Download the EchoCash project to your laptop/computer.

2. **Run ngrok.exe**  
   - Launch `ngrok.exe` on your laptop/computer.
   - Run the following command in your terminal:  
     `ngrok http 5000`

3. **Get Your ngrok URL**  
   - After running the command, ngrok will provide a URL. It will look something like:  
     `https://xxxxxxxx.ngrok-free.app`
   - Copy this URL.

4. **Update WebSocket Address**  
   - Open `static/script.js` on your laptop/computer.
   - Replace the existing WebSocket connection line:  
     `var socket = io.connect("wss://xxxxxxxx.ngrok-free.app");`  
     with the URL you got from ngrok (e.g., `wss://xxxxxxxx.ngrok-free.app`).

5. **Run the Server**  
   - Run the `server.py` file on your laptop/computer. This will start the backend server that handles object detection.

6. **Visit the URL on Your Phone**  
   - On your phone, open a browser and navigate to the ngrok URL you copied:  
     `https://xxxxxxxx.ngrok-free.app`

7. **Start Detecting!**  
   - The app should now be ready to detect currency! Point your phone camera at the currency, and the app will provide feedback.

### Example Image

<p align="center">
  <img src="static/example.jpg" alt="Example" style="width: 300px; height: auto;"/>
</p>

Enjoy using EchoCash and help visually impaired people easily detect currency!

## How It Works

EchoCash combines a mobile phone’s camera with a local server to detect and count currency in real-time, providing audio feedback for visually impaired users. Here’s an overview of the process:

- **Camera Feed**: The mobile phone’s camera captures video at 4 frames per second (250ms intervals) and sends these frames to the server via a WebSocket connection.
- **Server Processing**: The laptop/computer runs `server.py`, which uses a pre-trained YOLO model (`best_model.pt`) to analyze each frame and identify currency.
- **Feedback Loop**: The server sends detection results back to the phone, which updates the UI and provides voice feedback using the browser’s speech synthesis API.

The system is designed to be lightweight and accessible, requiring only a browser on the phone and a local server with internet access (via ngrok).

## How Currency Is Detected

Currency detection is powered by a YOLO-based machine learning model, optimized for accuracy and speed:

- **Training**: The model was trained on a dataset of USD, EURO, and BDT notes, using convolutional layers to recognize patterns like text, colors, and symbols. It achieves 98.61% precision.
- **Detection Process**:
  1. **Frame Capture**: The phone sends 4 frames per second to the server.
  2. **YOLO Analysis**: The server processes each frame with the YOLO model, identifying objects and classifying them as specific currency denominations (e.g., "100taka", "5dollar") based on the `yaml.yaml` label mappings.
  3. **Consistency Check**: A currency must be detected consistently for 3 seconds (12 frames at 4fps) before it’s announced via voice feedback. This prevents false positives from brief glimpses.
  4. **No Currency Handling**: If no currency is detected, the system tracks it internally but doesn’t provide voice feedback, displaying "Detected: No currency detected" in the UI.
- **Voice Feedback**: Once a currency is confirmed (after 3 seconds), it’s spoken aloud (e.g., "100taka"), and the timer resets, requiring another 3 seconds for the next announcement—even if the same currency persists.

## How Currency Is Counted

EchoCash keeps a running total of detected currency, updated via user gestures:

- **Adding Currency**:
  - **For Currencies**: After a currency is detected and spoken (e.g., "100taka" after 3 seconds), a double tap on the phone screen adds its value to the total (e.g., 100 Taka). The system then speaks the updated total (e.g., "the total is 100 Taka").
  - **For No Currency**: If "No currency detected" is shown, a double tap adds zero (no change to totals) and speaks the current total (e.g., "the total is 100 Taka" if 100 Taka was previously added, or "the total is 0" if nothing was added yet).
  - **Validation**: Currency is only added if it matches the last spoken label, ensuring accuracy. Double taps before voice feedback are ignored for currencies.
- **Canceling Totals**: A triple tap resets all totals to zero and announces "canceled."
- **Total Tracking**: Totals are maintained separately for each currency type (Taka, USD, Euro, Eurocents) and displayed in the UI as "Totals: X Taka, Y USD, Z EUR, W Eurocents."

The counting process is intuitive for visually impaired users, relying on audio confirmation after each addition, with no pause in detection to allow continuous use.