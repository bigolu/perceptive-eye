let preview = document.getElementById("preview");
let recording = document.getElementById("recording");
let startButton = document.getElementById("startButton");
let stopButton = document.getElementById("stopButton");
let downloadButton = document.getElementById("downloadButton");
let logElement = document.getElementById("log");

function log(msg) {
    logElement.innerHTML += msg + "\n";
}

function processVideo(video) {
    log('Sending video to server');
    console.log(video);
    const fd = new FormData();
    fd.append('video', video, 'video.webm');
    fetch('/process', {
        method: 'post',
        body: fd
    })
        .then(response => {
            response.json().then((data) => {
                console.log(data);
                log(`SERVER RESPONSE: ${data}`);
            });
        });
}

let recordingTimeMS = 1000;
function wait(delayInMS) {
    return new Promise(resolve => setTimeout(resolve, delayInMS));
}
function startRecording(stream, lengthInMS) {
    let recorder = new MediaRecorder(stream);
    let data = [];

    recorder.ondataavailable = event => data.push(event.data);
    recorder.start();
    log(recorder.state + " for " + (lengthInMS/1000) + " seconds...");

    let stopped = new Promise((resolve, reject) => {
        recorder.onstop = resolve;
        recorder.onerror = event => reject(event.name);
    });

    let recorded = wait(lengthInMS).then(
        () => recorder.state == "recording" && recorder.stop()
    );

    return Promise.all([
        stopped,
        recorded
    ])
        .then(() => data);
}
function stop(stream) {
    stream.getTracks().forEach(track => track.stop());
}
startButton.addEventListener("click", function() {
    navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
    }).then(stream => {
        preview.srcObject = stream;
        // downloadButton.href = stream;
        preview.captureStream = preview.captureStream || preview.mozCaptureStream;
        return new Promise(resolve => preview.onplaying = resolve);
    }).then(() => startRecording(preview.captureStream(), recordingTimeMS))
        .then (recordedChunks => {
            const recordedBlob = new Blob(recordedChunks, { type: "video/webm" });
            recording.src = URL.createObjectURL(recordedBlob);
            // downloadButton.href = recording.src;
            // downloadButton.download = "RecordedVideo.webm";
            
            downloadButton.addEventListener("click", function() {
                processVideo(recordedBlob);
            });

            renderModel();

            log("Successfully recorded " + recordedBlob.size + " bytes of " +
                recordedBlob.type + " media.");
        })
        .catch(log);
}, false);stopButton.addEventListener("click", function() {
    stop(preview.srcObject);
}, false);
