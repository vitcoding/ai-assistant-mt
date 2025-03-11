var ws = null;
function connect(event) {

    var itemId = document.getElementById("itemId")
    var token = document.getElementById("token")
    var checkbox_rag = document.getElementById("checkbox_rag")

    ws = new WebSocket(
        "ws://localhost:8005/api/v1/chat_ai/items/" +
        itemId.value +
        "/ws?token=" + token.value +
        "&use_rag=" + checkbox_rag.checked
    );

    ws.onmessage = function (event) {
        const data = event.data;
        const chunksElement = document.getElementsByClassName('temporary')[0];
        const paragraph = chunksElement.querySelector('p');

        if (data === '<<<end>>>') {
            moveTemporaryToFinal(paragraph);
        } else {
            appendToTemporary(paragraph, data);
        }

    };
    event.preventDefault()
}

function appendToTemporary(textContainer, partialMessage) {
    var content = document.createTextNode(partialMessage)
    textContainer.appendChild(content)

    const chatBody = document.querySelector(".chat_body");
    chatBody.scrollTop = chatBody.scrollHeight;
}

function moveTemporaryToFinal(sourceElement) {
    const text = sourceElement.textContent;
    var messages = document.getElementById('messages')
    var message = document.createElement('div')

    var lastMessage = messages.lastElementChild;

    if (lastMessage && lastMessage.id === 'aiMessage') {
        message.id = 'userMessage';
    } else {
        message.id = 'aiMessage';
    }

    message.textContent = text;
    messages.appendChild(message)
    sourceElement.textContent = '';
}


function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}