async function fetchAndPlayWav(fileId) {
    // console.log("play audio")
    try {
        const response = await fetch(`/api/v1/chat_ai/wav/${fileId}`);

        // console.log("response: " + response.body)
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const audio = new Audio(url);
        audio.controls = true;

        audio.play().catch((error) => console.error(error));

        audio.onended = () => URL.revokeObjectURL(url);

    } catch (error) {
        console.error('Error:', error.message);
    }
}