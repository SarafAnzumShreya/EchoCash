let video = document.getElementById('video');
let canvas = document.createElement('canvas');
let context = canvas.getContext('2d');
document.body.appendChild(canvas);

// Initialize NCNN model
async function loadModel() {
    // Initialize the WebAssembly version of NCNN
    await ncnn.initWasm();  // Initialize WebAssembly
    
    // Load the model with .param and .bin files
    const model = await ncnn.loadModel('best_model.param', 'best_model.bin');

    console.log("NCNN model loaded!");
    return model;
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
async function processFrame(model) {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);

    // Convert image data to tensor and perform inference
    const detections = await model.detect(imageData.data);  // Assuming detect method for ncnn

    // Draw bounding boxes and labels on the canvas
    detections.forEach((det) => {
        context.beginPath();
        context.rect(det.x, det.y, det.width, det.height);
        context.strokeStyle = "#00FF00";
        context.lineWidth = 3;
        context.stroke();
        context.fillText(det.class, det.x, det.y - 10);
    });

    requestAnimationFrame(() => processFrame(model)); // Keep processing frames
}

// Load the model and start processing the webcam feed
loadModel().then((model) => {
    processFrame(model);
});
