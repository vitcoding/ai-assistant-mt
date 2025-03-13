var ws = null;

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById("dropdownLanguage").value =
        document.getElementById("dropdownLanguage").options[0].value;
    document.getElementById("dropdownModel").value =
        document.getElementById("dropdownLanguage").options[0].value;
    var messageButton = document.getElementById('sendMessageButton');
    messageButton.disabled = true;
    var startRecordButton = document.getElementById('recordButton');
    startRecordButton.disabled = true;
});

async function connect(event) {

    var itemId = document.getElementById("itemId");
    var token = document.getElementById("token");
    var model_index = document.getElementById("dropdownModel");
    var language_index = document.getElementById("dropdownLanguage");
    var checkbox_rag = document.getElementById("checkboxRag");

    var messageButton = document.getElementById('sendMessageButton');
    var recordButton = document.getElementById('recordButton');

    ws = new WebSocket(
        "ws://localhost:8005/api/v1/chat_ai/items/" +
        itemId.value +
        "/ws?token=" + token.value +
        "&model_index=" + model_index.value +
        "&language_index=" + language_index.value +
        "&use_rag=" + checkbox_rag.checked
    );
    messageButton.disabled = false;
    recordButton.disabled = false;


    ws.onmessage = function (event) {
        const data = event.data;
        const chunksElement = document.getElementsByClassName('temporary')[0];
        const paragraph = chunksElement.querySelector('div');

        if (data === '<<<end>>>') {
            if (paragraph.id === 'aiMessage') {
                fetchAndPlayWav("output");
            }
            moveTemporaryToFinal(paragraph);
            messageButton.disabled = false;
            recordButton.disabled = false;

        } else {
            messageButton.disabled = true;
            recordButton.disabled = true;
            appendToTemporary(paragraph, data);
        }

    };
    event.preventDefault();
}

function appendToTemporary(textContainer, partialMessage) {

    if (textContainer.textContent == "") {
        const regex = /] (Me|Я):\s*(.*)/;
        const match = partialMessage.match(regex);
        if (match && match.length > 0) {
            textContainer.id = "userMessage"
        } else {
            textContainer.id = "aiMessage"
        }

    }
    textContainer.innerHTML += partialMessage.replace(/\n/g, '<br>');

    scrollChat();
}

function moveTemporaryToFinal(sourceElement) {
    const content = sourceElement.innerHTML;
    var messages = document.getElementById('messages');
    var message = document.createElement('div');

    message.id = sourceElement.id
    message.innerHTML = content;
    messages.appendChild(message);
    sourceElement.id = "noneMessage";
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