let recorder, chunks = [];

document.getElementById('recordButton').addEventListener('mousedown', startRecording);
document.getElementById('recordButton').addEventListener('touchstart', startRecording);
document.getElementById('recordButton').addEventListener('mouseup', stopRecording);
document.getElementById('recordButton').addEventListener('touchend', stopRecording);


async function startRecording() {
    try {
        // console.log("Start recording.")

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);

        recorder.ondataavailable = event => {
            chunks.push(event.data);
        };
        recorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            chunks = [];

            const url = URL.createObjectURL(blob);
            document.getElementById('downloadLink').href = url;

            const now = new Date();
            const dateTimeString = now.toISOString().replace(/:/g, '-').replace(/\./g, 'MS');
            const fileName = `${chatId}_${dateTimeString}.wav`;
            document.getElementById('downloadLink').download = fileName;

            // document.getElementById('downloadLink').click();

            // send file
            const file = new File([blob], fileName, { type: 'audio/wav' });

            // Create FormData and add file
            const formData = new FormData();
            formData.append('uploaded_audio', file);

            fetch('/api/v1/chat_ai/upload-audio', {
                method: 'POST',
                body: formData,
            }).then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            }).then(data => {
                // console.log('File sent!', data);

                // send info about an audio message
                ws.send("<<<audio>>>");
            }).catch(error => {
                console.error('File transfer error:', error);
            });

            // turn off the microphone
            stream.getTracks().forEach(track => track.stop());
        };

        recorder.start();

        document.getElementById('sendMessageButton').disabled = true;
    } catch (error) {
        console.error('Error when trying to start recording:', error);
    }
}

function stopRecording() {
    // console.log("Stop recording.")
    if (recorder && recorder.state !== 'inactive') {
        // console.log(recorder.state)
        recorder.stop();
        recorder.disabled
        // console.log(recorder.state)
    }
    document.getElementById('recordButton').disabled = true;
}