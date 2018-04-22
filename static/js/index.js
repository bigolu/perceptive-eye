// try ply format
var camera, scene, renderer;
var windowScale;
var ambientLight, light;
var controls;
var myObjs = {};

function drawCube(rgb=0xff0000ff, pos=[0, 0, 0]) {
    var scale = 0.2;
    var geo = new THREE.CubeGeometry(scale, scale, scale); // change the resolution here
    var mat = new THREE.MeshLambertMaterial({
        color: rgb,
        side: THREE.FrontSide,
        transparent: true
    });
    var mesh = new THREE.Mesh(geo, mat);
    mesh.position.x = pos[0] * scale;
    mesh.position.y = pos[1] * scale;
    mesh.position.z = pos[2] * scale;
    scene.add(mesh);
    return mesh;
}

function setup() { // Using three.js library (webgl) (math)
    var height = 720;
    var width = 1280;
    var ratio = width / height;

    scene = new THREE.Scene();
    windowScale = 12;
    var windowWidth = windowScale * ratio;
    var windowHeight = windowScale;

    // camera: y up, x right, z out
    camera = new THREE.OrthographicCamera(-windowWidth / 2, windowWidth / 2,
        windowHeight / 2, -windowHeight / 2, 0, 40); // near = 0, far = 40

    var focus = new THREE.Vector3(0, 0, 0);
    camera.position.x = focus.x;
    camera.position.y = focus.y;
    camera.position.z = 20;

    // lights
    ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);
    light = new THREE.DirectionalLight(0xffffff, 0.7);
    light.position.set(8, 9, 3);
    scene.add(light);

    renderer = new THREE.WebGLRenderer({ antialias: true,
        preserveDrawingBuffer: true });
    renderer.gammaInput = true;
    renderer.gammaOutput = true;
    renderer.setSize(width, height);
    renderer.setClearColor(0xffffff, 1.0);

    // controls
    controls = new THREE.TrackballControls(camera);//, renderer.domElement);
    controls.rotateSpeed = 2;
    controls.staticMoving = true;
    controls.addEventListener('change', render);
}

function addToDOM() { // Using HTML (core)
    var container = document.getElementById("container");
    var canvas = document.getElementById("canvas");
    if (canvas.length > 0) {
        container.removeChild(canvas[0]);
    }
    container.appendChild(renderer.domElement);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
}

function render() { // Using three.js library (webgl)
    renderer.render(scene, camera);
}

function constructRGB(r, g, b) {
    var rgb = r * 256 * 256 + g * 256 + b;
    return rgb;
}

function updateScene(colors) {
  if (colors === null) {
    return;
  }
  for (let i = 0; i < 20; i++) {
    for (let j = 0; j < 20; j++) {
      for (let k = 0; k < 20; k++) {
        let argb = colors[i][j][k];
        if (argb == 0) {
          myObjs.meshes[i][j][k].material.opacity = 0;
        } else {
          myObjs.meshes[i][j][k].material = new THREE.MeshLambertMaterial({
              color: argb,
              side: THREE.FrontSide,
              transparent: true
          });
        }
      }
    }
  }
  render();
}

function renderModel(colors) {

    try { // call all of the above (core)
        setup();
        animate();
        addToDOM();

        myObjs.index = 0;
        myObjs.meshes = [];

        var cubeSize = 20; // change the number of cubes here
        for (var i = 0; i < cubeSize; i++) {
            myObjs.meshes.push([]);
            for (var j = 0; j < cubeSize; j++) {
                myObjs.meshes[i].push([]);
                for (var k = 0; k < cubeSize; k++) {
                    myObjs.meshes[i][j].push(
                        drawCube(constructRGB(0, 0, 255), [i, j, k]));
                }
            }
        }
        render();
        updateScene(colors);

    } catch(e) {
        console.log("Error occurred: " + e);
    }

}


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
    //console.log(video);
    const fd = new FormData();
    fd.append('video', video, 'video.webm');
    fetch('/process', {
        method: 'post',
        body: fd
    })
        .then(response => {
            response.json().then(data => {
                const colors = data.colors;

                console.log(colors);
                log(`SERVER RESPONSE: ${colors}`);

                log('RENDERING');
                renderModel(colors);
                log('DONE RENDERING');
            });
        });
}

let recordingTimeMS = 15000;
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

            log("Successfully recorded " + recordedBlob.size + " bytes of " +
                recordedBlob.type + " media.");
        })
        .catch(log);
}, false);stopButton.addEventListener("click", function() {
    stop(preview.srcObject);
}, false);

