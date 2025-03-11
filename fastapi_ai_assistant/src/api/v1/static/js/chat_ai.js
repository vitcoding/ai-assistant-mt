var ws = null;
function connect(event) {

    var itemId = document.getElementById("itemId");
    var token = document.getElementById("token");
    var checkbox_rag = document.getElementById("checkbox_rag");

    ws = new WebSocket(
        "ws://localhost:8005/api/v1/chat_ai/items/" +
        itemId.value +
        "/ws?token=" + token.value +
        "&use_rag=" + checkbox_rag.checked
    );

    ws.onmessage = function (event) {
        const data = event.data;
        const chunksElement = document.getElementsByClassName('temporary')[0];
        const paragraph = chunksElement.querySelector('div');

        if (data === '<<<end>>>') {
            moveTemporaryToFinal(paragraph);
        } else {
            appendToTemporary(paragraph, data);
        }

    };
    event.preventDefault();
}

function appendToTemporary(textContainer, partialMessage) {
    textContainer.innerHTML += partialMessage.replace(/\n/g, '<br>');

    scrollChat();
}

function moveTemporaryToFinal(sourceElement) {
    const content = sourceElement.innerHTML;
    var messages = document.getElementById('messages');
    var message = document.createElement('div');

    var lastMessage = messages.lastElementChild;

    if (lastMessage && lastMessage.id === 'aiMessage') {
        message.id = 'userMessage';
    } else {
        message.id = 'aiMessage';
    }

    message.innerHTML = content;
    messages.appendChild(message);
    sourceElement.textContent = '';

    scrollChat();
}

function sendMessage(event) {
    var input = document.getElementById("messageText");
    ws.send(input.value);
    input.value = '';
    event.preventDefault();
}

function scrollChat() {
    const chatBody = document.querySelector(".chat_body");
    chatBody.scrollTop = chatBody.scrollHeight;
}