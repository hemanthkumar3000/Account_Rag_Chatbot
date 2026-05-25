// Generate or reuse a sessionId so the backend can keep short history
let sessionId = localStorage.getItem("sessionId");
if (!sessionId) {
  sessionId = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
  localStorage.setItem("sessionId", sessionId);
}

const chatEl = document.getElementById("chat");
const inputEl = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendButton");
const statusEl = document.getElementById("status");

// Helper: append a message bubble
function appendMessage(role, text) {
  const div = document.createElement("div");
  div.classList.add("message");
  div.classList.add(role === "User" ? "user" : "assistant");

  const roleEl = document.createElement("div");
  roleEl.classList.add("role");
  roleEl.textContent = role + ":";

  const textEl = document.createElement("div");
  textEl.textContent = text;

  div.appendChild(roleEl);
  div.appendChild(textEl);
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

// Send message to backend
async function sendMessage() {
  const message = inputEl.value.trim();
  if (!message) return;

  // Show user message immediately
  appendMessage("User", message);
  inputEl.value = "";
  inputEl.focus();

  sendBtn.disabled = true;
  statusEl.textContent = "Thinking...";

  try {
    const res = await fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId: sessionId,
        message: message,
      }),
    });

    if (!res.ok) {
      appendMessage("Assistant", "Error: " + res.status + " " + res.statusText);
      statusEl.textContent = "";
      sendBtn.disabled = false;
      return;
    }

    const data = await res.json();

    if (data.error) {
      appendMessage("Assistant", "Error: " + data.error);
    } else {
      appendMessage("Assistant", data.reply);
    }

    statusEl.textContent =
      "Retrieved chunks: " + (data.retrievedChunks ?? 0) + ", tokens used: " + (data.tokensUsed ?? 0);
  } catch (err) {
    appendMessage("Assistant", "Network error: " + err.message);
    statusEl.textContent = "";
  } finally {
    sendBtn.disabled = false;
  }
}

// Event listeners
sendBtn.addEventListener("click", sendMessage);

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Initial status
statusEl.textContent = "Session ID: " + sessionId;