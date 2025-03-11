let recorder, chunks = [];

// document.getElementById('recordButton').addEventListener('mousedown', startRecording);
// document.getElementById('recordButton').addEventListener('touchstart', startRecording);
// document.getElementById('recordButton').addEventListener('mouseup', stopRecording);
// document.getElementById('recordButton').addEventListener('touchend', stopRecording);


async function startRecording() {
    try {
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
            document.getElementById('downloadLink').download = 'recorded-audio.wav';
            // document.getElementById('downloadLink').click();

            // send file
            const file = new File([blob], 'recorded-audio.wav', { type: 'audio/wav' });

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
                console.log('Файл успешно передан!', data);
                // send info about an audio message
                ws.send("<<<audio>>>");
            }).catch(error => {
                console.error('Ошибка при передаче файла:', error);
            });


        };

        recorder.start();

        document.getElementById('sendMessageButton').disabled = true;
        document.getElementById('startRecordButton').disabled = true;
        document.getElementById('stopRecordButton').disabled = false;
    } catch (error) {
        console.error('Ошибка при попытке начать запись:', error);
    }
}

function stopRecording() {
    if (recorder && recorder.state !== 'inactive') {
        // console.log(recorder.state)
        recorder.stop();
        // console.log(recorder.state)

        document.getElementById('stopRecordButton').disabled = true;
    }
}