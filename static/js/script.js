let video = document.getElementById('video');
let canvas = document.createElement('canvas');
let context = canvas.getContext('2d');
document.body.appendChild(canvas);

// Initialize ONNX model
async function loadModel() {
    const session = await onnxruntime.InferenceSession.create('best_model.onnx');
    console.log("ONNX model loaded!");
    return session;
}

// Start capturing video from the webcam
navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
    video.srcObject = stream;
    video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    };
});

// Process each frame captured from the webcam
async function processFrame(session) {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);

    // Convert image data to tensor
    const inputTensor = new onnxruntime.Tensor("float32", new Float32Array(imageData.data), [1, 3, 640, 480]);

    // Run model
    const results = await session.run({ input: inputTensor });

    // Process results
    processResults(results);
}

// Process the results from the model
function processResults(results) {
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    let detectedLabel = null;
    if (results.output) {
        const boxes = results.output.data;
        for (let i = 0; i < boxes.length; i += 6) {
            const [x, y, w, h, conf, classId] = boxes.slice(i, i + 6);
            if (conf > 0.5) {
                detectedLabel = `Currency ${classId}`;
                context.strokeStyle = "red";
                context.lineWidth = 2;
                context.strokeRect(x, y, w, h);
                context.fillStyle = "red";
                context.fillText(detectedLabel, x, y - 5);
            }
        }
    }

    // Speak detected label with a delay to avoid repeating
    if (detectedLabel && shouldSpeak(detectedLabel)) {
        speak(detectedLabel);
    }
}

// Control speaking frequency
let lastSpokenLabel = "";
let lastSpokenTime = 0;
const SPEAK_INTERVAL = 2000; // 2 seconds
function shouldSpeak(label) {
    const currentTime = Date.now();
    if (label !== lastSpokenLabel || currentTime - lastSpokenTime > SPEAK_INTERVAL) {
        lastSpokenLabel = label;
        lastSpokenTime = currentTime;
        return true;
    }
    return false;
}

// Function to speak detected label
function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utterance);
    console.log(`Spoken: ${text}`);
}

// Load the model and start processing the webcam feed
loadModel().then((session) => {
    setInterval(() => processFrame(session), 1000);
});
