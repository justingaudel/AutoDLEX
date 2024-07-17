(function() {
    var width = 1920;
    var height = 1080;
    var streaming = false;
    var video = null;
    var canvas = null;
    var photo = null;
    var startbutton = null;
    var retakebutton = null;
    var flashlightButton = null;
    var extractedTextElement = null;
    var capturedImageElement = null;
    var submit = document.getElementById('submit');
    var track = null; // Store the video track

    function startup() {
        video = document.getElementById('video');
        canvas = document.getElementById('canvas');
        photo = document.getElementById('photo');
        startbutton = document.getElementById('startbutton');
        retakebutton = document.getElementById('retakebutton');
        flashlightButton = document.getElementById('flashlightButton'); // Get the reference to the flashlight button
        extractedTextElement = document.getElementById('extractedText');
        capturedImageElement = document.getElementById('capturedImage');

        navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: { ideal: 'environment' },
                width: { ideal: width },
                height: { ideal: height },
                focusMode: 'continuous'
            },
            audio: false
        })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
            submit.disabled = true;
            track = stream.getVideoTracks()[0]; // Get the video track
        })
        .catch(function(err) {
            console.log("An error occurred: " + err);
        });

        video.addEventListener('canplay', function(ev) {
            if (!streaming) {
                height = video.videoHeight / (video.videoWidth / width);

                if (isNaN(height)) {
                    height = width / (4 / 3);
                }

                video.setAttribute('width', width);
                video.setAttribute('height', height);
                canvas.setAttribute('width', width);
                canvas.setAttribute('height', height);
                streaming = true;
            }
        }, false);

        startbutton.addEventListener('click', function(ev) {
            takepicture();
            ev.preventDefault();
        }, false);

        retakebutton.addEventListener('click', function(ev) {
            retakephoto();
            ev.preventDefault();
        }, false);

        flashlightButton.addEventListener('click', function(ev) {
            toggleFlashlight();
            ev.preventDefault();
        }, false);

        clearphoto();
    }

    function clearphoto() {
        var context = canvas.getContext('2d');
        context.fillStyle = "#AAA";
        context.fillRect(0, 0, canvas.width, canvas.height);
        var data = canvas.toDataURL('image/png');
        photo.setAttribute('src', data);
    }

    function takepicture() {
        var context = canvas.getContext('2d');
        if (width && height) {
            canvas.width = width;
            canvas.height = height;
            context.drawImage(video, 0, 0, width, height);
            var dataURL = canvas.toDataURL('image/png');
            var blobBin = atob(dataURL.split(',')[1]);
            var array = [];
            for(var i = 0; i < blobBin.length; i++) {
                array.push(blobBin.charCodeAt(i));
            }
            var file = new Blob([new Uint8Array(array)], { type: 'image/png' });
            var formData = new FormData();
            formData.append('image', file, 'image.png');
            capturedImageElement.src = dataURL;
            capturedImageElement.style.display = 'block';
            retakebutton.style.display = 'block';
            video.style.display = 'none';
            submit.disabled = true;

            fetch('/process_image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(text => {
                extractedTextElement.textContent = text;
                submit.disabled = false;
            })
            .catch(error => console.error('Error:', error));
        } else {
            clearphoto();
        }
    }

    function retakephoto() {
        capturedImageElement.style.display = 'none';
        startbutton.style.display = 'block';
        video.style.display = 'inline-block';
        submit.disabled = true;
    }

    function toggleFlashlight() {
        if (track) {
            const capabilities = track.getCapabilities();
            if (capabilities.torch) {
                const settings = track.getSettings();
                track.applyConstraints({
                    advanced: [{ torch: !settings.torch }]
                }).catch(e => console.log(e));
            } else {
                alert("Torch mode is not supported by this browser.");
            }
        }
    }

    window.addEventListener('load', startup, false);
})();
