function toggleChatbot() {
    const container = document.getElementById("chatbot-container");
    container.style.display = container.style.display === "none" ? "flex" : "none";
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("chatbot-button").addEventListener("click", toggleChatbot);
});

function appendMessage(sender, text) {
    const msgBox = document.getElementById("chat-messages");
    const msg = document.createElement("div");
    msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
    msgBox.appendChild(msg);
    msgBox.scrollTop = msgBox.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage("You", message);
    input.value = "";

    fetch(chatbotUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({ message: message })
    })
        .then(res => res.json())
        .then(data => appendMessage("Bot", data.reply))
        .catch(() => appendMessage("Bot", "Error: Could not reach server."));
}
