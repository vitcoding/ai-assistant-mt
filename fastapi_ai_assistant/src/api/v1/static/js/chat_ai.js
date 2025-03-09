var ws = null;
function connect(event) {
    var itemId = document.getElementById("itemId")
    var token = document.getElementById("token")
    var checkbox_rag = document.getElementById("checkbox_rag")
    ws = new WebSocket("ws://localhost:8005/api/v1/chat_ai/items/" + itemId.value + "/ws?token=" + token.value + "&use_rag=" + checkbox_rag.checked);
    ws.onmessage = function (event) {
        var messages = document.getElementById('messages')
        var message = document.createElement('li')
        var content = document.createTextNode(event.data)
        message.appendChild(content)
        messages.appendChild(message)
    };
    event.preventDefault()
}

function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}