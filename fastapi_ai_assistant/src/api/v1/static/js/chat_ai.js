var ws = null;
var aiMessageName = null

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById("dropdownLanguage").value =
        document.getElementById("dropdownLanguage").options[0].value;
    document.getElementById("dropdownModel").value =
        document.getElementById("dropdownLanguage").options[0].value;
    var messageButton = document.getElementById('sendMessageButton');
    messageButton.disabled = true;
    var startRecordButton = document.getElementById('recordButton');
    startRecordButton.disabled = true;

    const stream = navigator.mediaDevices.getUserMedia({ audio: true });
});

function toggleMenu() {
    var menuContent = document.getElementById("menuContent");

    if (menuContent.classList.contains("expanded")) {
        menuContent.classList.remove("expanded");
        menuContent.classList.add("collapsed");
    } else {
        menuContent.classList.remove("collapsed");
        menuContent.classList.add("expanded");
    }
}

async function connect(event) {
    var chat_topic = document.getElementById("chatTopic");
    var model_index = document.getElementById("dropdownModel");
    var language_index = document.getElementById("dropdownLanguage");
    var checkbox_rag = document.getElementById("checkboxRag");
    var checkbox_sound = document.getElementById("checkboxSound");

    var messageButton = document.getElementById('sendMessageButton');
    var recordButton = document.getElementById('recordButton');

    messageButton.disabled = true;
    recordButton.disabled = true;

    if (previousChat === "False") {
        var messages = document.getElementById('messages');

        while (messages.firstChild) {
            messages.removeChild(messages.firstChild);
        }
    }

    ws = new WebSocket(
        "ws://" + serviceHost + "/api/v1/chat_ai/" +
        chatId +
        "/ws?chat_topic=" + chat_topic.value +
        "&model_index=" + model_index.value +
        "&language_index=" + language_index.value +
        "&use_rag=" + checkbox_rag.checked +
        "&use_sound=" + checkbox_sound.checked
    );

    toggleMenu()

    ws.onopen = function () {
        // console.log("WebSocket connection established!");
        messageButton.disabled = false;
        recordButton.disabled = false;
    };


    ws.onmessage = function (event) {
        const data = event.data;
        const chunksElement = document.getElementsByClassName('temporary')[0];
        const paragraph = chunksElement.querySelector('div');

        if (data === '<<<end>>>') {
            if (paragraph.id === 'aiMessage'
                && checkbox_sound.checked === true
                && aiMessageName !== null) {
                fetchAndPlayWav(aiMessageName);
            }
            moveTemporaryToFinal(paragraph);
            aiMessageName = null
            messageButton.disabled = false;
            recordButton.disabled = false;

        } else {
            if (data.startsWith("<<<ai_file_name>>>")) {
                aiMessageName = data.split(" ", 2)[1];
            } else {
                messageButton.disabled = true;
                recordButton.disabled = true;
                appendToTemporary(paragraph, data);
            }
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
            const regex = /] (AI|ИИ):\s*(.*)/;
            const match = partialMessage.match(regex);
            if (match && match.length > 0) {
                textContainer.id = "aiMessage"
            } else {
                textContainer.id = "systemMessage"
            }
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