var socket = io.connect("wss://59f8-123-136-25-129.ngrok-free.app");
var video = document.getElementById("videoElement");
var canvas = document.getElementById("videoCanvas");
var ctx = canvas.getContext("2d");

var capturing = true;
var videoStream = null;
var tapCount = 0;
var lastTapTime = 0;
var TAP_TIMEOUT = 1000; // 500ms window for multi-tap detection
var LONG_PRESS_TIMEOUT = 1500; // 1.5 seconds for long press detection
var longPressTimer = null;
var isLongPress = false;

function unlockAudio() {
    const silentAudio = document.getElementById("silentAudio");
    silentAudio.play().then(() => {
        console.log("Silent audio played successfully. Audio is unlocked.");
    }).catch((error) => {
        console.error("Failed to play silent audio:", error);
    });
}

window.onload = function() {
    socket.emit("command", { command: "start", label: null });
    unlockAudio();
    startCamera();
};

async function startCamera() {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" }
        });
        console.log("Camera access granted");
        video.srcObject = videoStream;
        video.play();
        captureFrame();
    } catch (error) {
        console.error("Error accessing camera: ", error);
        alert("Camera access is required. Please enable camera permissions.");
    }
}

function captureFrame() {
    if (video.readyState === 4 && capturing) {
        canvas.width = 370;
        canvas.height = 370;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        let imageData = canvas.toDataURL("image/jpeg").split(",")[1];
        console.log("Sending frame to server");
        socket.emit("frame", imageData);
    }
    setTimeout(() => requestAnimationFrame(captureFrame), 250); // 4 frames per second 
}

function speakDetectedCurrency(label) {
    var synth = window.speechSynthesis;
    if (!synth) {
        console.error("Speech synthesis not supported on this device.");
        return;
    }
    var utterance = new SpeechSynthesisUtterance(label);
    const voices = synth.getVoices();
    if (voices.length === 0) {
        console.warn("No voices available yet, waiting for voiceschanged event");
        synth.onvoiceschanged = () => {
            const loadedVoices = synth.getVoices();
            const femaleVoice = loadedVoices.find(voice => 
                voice.lang.includes("en") && voice.name.toLowerCase().includes("female")) || 
                loadedVoices.find(voice => voice.lang.includes("en"));
            if (femaleVoice) {
                utterance.voice = femaleVoice;
            }
            console.log("Speaking with voice:", utterance.voice ? utterance.voice.name : "default");
            synth.speak(utterance);
        };
    } else {
        const femaleVoice = voices.find(voice => 
            voice.lang.includes("en") && voice.name.toLowerCase().includes("female")) || 
            voices.find(voice => voice.lang.includes("en"));
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        }
        console.log("Speaking with voice:", utterance.voice ? utterance.voice.name : "default");
        synth.speak(utterance);
    }
}

// Tap/Click gesture handling
document.body.addEventListener("click", function(event) {
    const currentTime = Date.now();
    if (currentTime - lastTapTime > TAP_TIMEOUT) {
        tapCount = 0; // Reset if too much time has passed
    }
    tapCount++;
    lastTapTime = currentTime;

    setTimeout(() => {
        if (tapCount === 2) {
            const currentLabel = document.getElementById("result").innerText.split("Detected: ")[1];
            console.log("Double tap detected, sending 'add' command with label:", currentLabel);
            socket.emit("command", { command: "add", label: currentLabel });
        } else if (tapCount === 3) {
            console.log("Triple tap detected, sending 'cancel' command");
            socket.emit("command", { command: "cancel", label: null });
        }
        tapCount = 0; // Reset after processing
    }, TAP_TIMEOUT);
});

// Long press gesture handling
document.body.addEventListener("mousedown", function(event) {
    longPressTimer = setTimeout(() => {
        isLongPress = true;
        console.log("Long press detected, sending 'reset' command");
        socket.emit("command", { command: "reset", label: null });
    }, LONG_PRESS_TIMEOUT);
});

document.body.addEventListener("mouseup", function(event) {
    if (!isLongPress) {
        clearTimeout(longPressTimer);
    }
    isLongPress = false;
});

document.body.addEventListener("touchstart", function(event) {
    longPressTimer = setTimeout(() => {
        isLongPress = true;
        console.log("Long press detected, sending 'reset' command");
        socket.emit("command", { command: "reset", label: null });
    }, LONG_PRESS_TIMEOUT);
});

document.body.addEventListener("touchend", function(event) {
    if (!isLongPress) {
        clearTimeout(longPressTimer);
    }
    isLongPress = false;
});

socket.on("connect", function() {
    console.log("Connected to server");
});

socket.on("disconnect", function() {
    console.log("Disconnected from server");
});

socket.on("result", function(data) {
    console.log("Received result:", data);
    document.getElementById("result").innerText = "Detected: " + data.label;
    updateTotals(data.totals);
    if (data.speak) {
        console.log("Attempting to speak:", data.label);
        speakDetectedCurrency(data.label);
    }
});

socket.on("total_update", function(data) {
    console.log("Received total update:", data);
    updateTotals(data.totals);
});

socket.on("command_feedback", function(data) {
    console.log("Received command feedback:", data);
    speakDetectedCurrency(data.message); 
});

function updateTotals(totals) {
    document.getElementById("total").innerText = 
        `Totals: ${totals.taka} Taka, ${totals.dollar} USD, ${totals.euro} EUR, ${totals.eurocent} Eurocents`;
}

window.addEventListener("beforeunload", function() {
    capturing = false;
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});

document.addEventListener("visibilitychange", function() {
    if (document.hidden) {
        capturing = false;
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
        }
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    } else {
        capturing = true;
        startCamera();
    }
});