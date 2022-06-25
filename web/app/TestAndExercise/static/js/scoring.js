navigator
        .mediaDevices
        .getUserMedia({audio: true})
        .then(stream => {
            handlerFunction(stream)
        });

    function handlerFunction(stream) {
        rec = new MediaRecorder(stream);
        rec.ondataavailable = e => {
            audioChunks.push(e.data);
            if (rec.state == "inactive") {
                // let blob = new Blob(audioChunks, {type: 'audio/wav'});
                let blob = new Blob(audioChunks, {type: 'audio/webm'});
                sendData(blob);
            }
        }
    }

    function sendData(data) {
        var form = new FormData();
        form.append('file', data, 'data.mp3');
        form.append('title', 'data.mp3');
        //Chrome inspector shows that the post data includes a file and a title.
        $.ajax({
            type: 'POST',
            // url: '/save-record',
            url: '/asr',
            data: form,
            cache: false,
            processData: false,
            contentType: false
        }).done(function (data) {
            console.log(data);
            alert(JSON.stringify(data))
        });
    }

    startRecording.onclick = e => {
        console.log('Recording are started..');
        startRecording.disabled = true;
        stopRecording.disabled = false;
        audioChunks = [];
        rec.start();
    };

    stopRecording.onclick = e => {
        console.log("Recording are stopped.");
        startRecording.disabled = false;
        stopRecording.disabled = true;
        rec.stop();
    };