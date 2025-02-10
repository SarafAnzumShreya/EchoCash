let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');
let stream = null;
let model = null;

async function loadModel() {
    await ncnn.initWasm();  // Initialize WebAssembly
    // Load the model with .param and .bin files
    model = await ncnn.loadModel('assets/best_model.param', 'assets/best_model.bin');
    console.log("NCNN model loaded!");
}

async function startCamera() {
    try {
        // Request webcam access
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;

        video.onloadedmetadata = () => {
            // Set canvas size to match the video size
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        };
    } catch (err) {
        console.error('Error accessing camera: ', err);
    }
}

async function processFrame() {
    if (model && stream) {
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
            context.fillStyle = "#00FF00";
            context.fillText(det.class, det.x, det.y - 10);
        });
    }

    requestAnimationFrame(processFrame); // Keep processing frames
}

// Initialize and start the process
loadModel().then(() => {
    startCamera().then(() => {
        processFrame();  // Start frame processing once everything is ready
    });
});
