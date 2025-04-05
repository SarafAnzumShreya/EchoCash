# <p align="center"><strong>EchoCash</strong></p>

<p align="center">
  <img src="static/logo.jpg" alt="EchoCash Logo" style="width: 100px; height: auto;"/>
</p>

EchoCash is a tool to help visually impaired people detect and count USD, EURO, and BDT currency using a phone and a computer.

## How to Set Up and Use

Follow these steps to get EchoCash running:

1. **Download the Project**  
   - Download or clone this project to your laptop/computer.

2. **Install Requirements**  
   - Ensure Python is installed on your computer.
   - Open a terminal in the project folder and run:  
     `pip install -r requirements.txt`  
     (This installs Flask, SocketIO, OpenCV, and Ultralytics YOLO.)

3. **Run ngrok**  
   - Download `ngrok.exe` from [ngrok.com](https://ngrok.com/) if you don’t have it.
   - Open a terminal and run:  
     `ngrok http 5000`
   - Copy the URL it gives you (e.g., `https://xxxxxxxx.ngrok-free.app`).

4. **Update the WebSocket Address**  
   - Open `static/script.js` in a text editor.
   - Find this line:  
     `var socket = io.connect("wss://xxxxxxxx.ngrok-free.app");`  
   - Replace the URL with the one from ngrok (e.g., `wss://xxxxxxxx.ngrok-free.app`).
   - Save the file.

5. **Start the Server**  
   - In a terminal, go to the project folder and run:  
     `python server.py`  
   - This starts the server on your computer.

6. **Open on Your Phone**  
   - On your phone, open a browser and go to the ngrok URL (e.g., `https://xxxxxxxx.ngrok-free.app`).
   - Allow camera access when prompted.

7. **Detect Currency**  
   - Point your phone camera at a USD, EURO, or BDT note.
   - Wait 3 seconds; if it’s a currency, you’ll hear it spoken (e.g., "100taka").
   - Double tap the screen to add it to the total, then hear the total (e.g., "the total is 100 Taka").
   - If no currency is detected, double tap to hear the current total (e.g., "the total is 0").
   - Triple tap to reset the total to zero (you’ll hear "canceled").

### Example Image

<p align="center">
  <img src="static/example.jpg" alt="Example" style="width: 300px; height: auto;"/>
</p>

That’s it! Use EchoCash to detect and count currency easily.