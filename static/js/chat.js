console.log("SAGE chat.js loaded");

function addMessage(text, sender) {
    const chatWindow = document.getElementById("chat-window");
    const div = document.createElement("div");
    div.classList.add("message", sender);
    div.innerText = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error(`Backend error: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        addMessage(data.reply || "No reply received.", "bot");
    })
    .catch(err => {
        console.error("Error calling /chat:", err);
        addMessage("[Error contacting SAGE backend. Please try again later.]", "bot");
    });
}

function moreInfo() {
    alert(
        "Welcome to SAGE 🎓\n\n" +
        "You can ask questions about UW–Madison study abroad and internship options, like:\n" +
        "• Programs that fit your major\n" +
        "• Summer vs semester options\n" +
        "• Combining study abroad with internships\n" +
        "• How to start planning based on your goals."
    );
}

// expose so your HTML onclick handlers work
window.sendMessage = sendMessage;
window.moreInfo = moreInfo;
