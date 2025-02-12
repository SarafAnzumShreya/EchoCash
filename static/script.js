var socket = io.connect("wss://*****.ngrok-free.app");
var video = document.getElementById("videoElement");
var canvas = document.getElementById("videoCanvas");
var ctx = canvas.getContext("2d");

var capturing = true;
var videoStream = null;  // To store video stream

var isUserInteracted = false; // To track user interaction

// Play silent audio to unlock audio playback
function unlockAudio() {
    const silentAudio = document.getElementById("silentAudio");
    silentAudio.play().then(() => {
        console.log("Silent audio played successfully. Audio is unlocked.");
    }).catch((error) => {
        console.error("Failed to play silent audio:", error);
    });
}

// Call unlockAudio on page load
window.onload = function() {
    unlockAudio();
    startCamera(); // Start the camera as usual
};

// Trigger speech synthesis on any user interaction (e.g., touch/click)
document.body.addEventListener('click', function() {
    isUserInteracted = true;
});

async function requestMicrophonePermission() {
    try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("Microphone access granted.");
    } catch (err) {
        console.error("Microphone access denied:", err);
        alert("Microphone permission is required for speech feedback.");
    }
}

// Request microphone permission before starting the camera
requestMicrophonePermission();


// Adjusted to ensure camera permissions are requested properly
async function startCamera() {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" }
        });
        console.log("Camera access granted");
        video.srcObject = videoStream;
        video.play(); // Ensure video is playing
        captureFrame(); // Start sending frames to server
    } catch (error) {
        console.error("Error accessing camera: ", error);
        alert("Camera access is required. Please enable camera permissions in your browser.");
    }
}

// Capture video frames and send them to the server
function captureFrame() {
    if (video.readyState === 4 && capturing) {
        // Set canvas size to a smaller resolution
        canvas.width = 255;
        canvas.height = 255;

        // Draw the video frame onto the canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas frame to base64 for transmission
        let imageData = canvas.toDataURL("image/jpeg").split(",")[1];
        
        // Log the image data to the console to check if it's being generated correctly
        console.log("Sending frame to server: ", imageData);
        
        socket.emit("frame", imageData);
    }
    setTimeout(() => requestAnimationFrame(captureFrame), 250); // Throttle to 4 frame per second
}

// This function can be triggered by a user event to ensure speech synthesis works.
function speakDetectedCurrency(label) {
    var synth = window.speechSynthesis;
    var utterance = new SpeechSynthesisUtterance(label);
    
    // Check if the speech synthesis is supported
    if ('speechSynthesis' in window) {
        synth.speak(utterance);
    } else {
        console.error("Speech synthesis not supported on this device.");
    }
}

// Modify the existing result handler
socket.on("result", function(data) {
    console.log("Received result:", data);  // Debugging the received result

    document.getElementById("result").innerText = "Detected: " + data.label;

    // Speak the detected currency if it's been detected for 3 seconds
    if (data.speak) {
        console.log("Attempting to speak:", data.label);
        var synth = window.speechSynthesis;
        var utterance = new SpeechSynthesisUtterance(data.label);
        
        // Check if the speech synthesis is supported
        if ('speechSynthesis' in window) {
            synth.speak(utterance);
        } else {
            console.error("Speech synthesis not supported on this device.");
        }
    }
});


// Start camera automatically on page load
window.onload = startCamera;

// Stop capturing frames when page is unloaded or hidden
window.addEventListener("beforeunload", function() {
    capturing = false;
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());  // Stop video stream
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
});

document.addEventListener("visibilitychange", function() {
    if (document.hidden) {
        capturing = false; // Stop capturing when page is hidden
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());  // Stop video stream
        }
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    } else {
        capturing = true; // Start capturing again when page is visible
        startCamera(); // Re-start camera if needed
    }
});
