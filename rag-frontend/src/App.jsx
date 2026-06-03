import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [sessionId] = useState("test-session");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! Ask me anything about your account docs.",
      sources: [],
    },
  ]);

  async function sendMessage() {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage = { role: "user", text: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId,
          message: trimmed,
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        const errorMessage =
          errText || `Request failed with status ${res.status}`;
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: `Error from server: ${errorMessage}`,
            sources: [],
          },
        ]);
        return;
      }

      const data = await res.json();

      const assistantMessage = {
        role: "assistant",
        text: data.reply,
        sources: data.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Network error talking to backend.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) sendMessage();
    }
  }

  return (
    <div style={styles.app}>
      <div style={styles.chatContainer}>
        <h2 style={styles.header}>Account Support RAG Chat</h2>

        <div style={styles.messages}>
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                ...styles.message,
                alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                backgroundColor:
                  m.role === "user" ? "#2563eb" : "rgba(148, 163, 184, 0.2)",
                color: m.role === "user" ? "white" : "#0f172a",
              }}
            >
              <div style={styles.roleLabel}>
                {m.role === "user" ? "You" : "Assistant"}
              </div>
              <div style={styles.text}>{m.text}</div>

              {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                <div style={styles.sources}>
                  <div style={styles.sourcesLabel}>Sources:</div>
                  {m.sources.map((s, sIdx) => (
                    <div key={sIdx} style={styles.sourceItem}>
                      <span style={{ fontWeight: 600 }}>{s.title}</span>
                      {s.category && (
                        <span style={styles.category}>({s.category})</span>
                      )}
                      <span style={styles.score}>
                        score: {s.score.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={styles.inputRow}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask something about reset password, account deletion, billing..."
            style={styles.textarea}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={styles.button}
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  app: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#0f172a",
    padding: "16px",
  },
  chatContainer: {
    width: "100%",
    maxWidth: "720px",
    backgroundColor: "white",
    borderRadius: "12px",
    padding: "16px",
    boxShadow: "0 10px 25px rgba(15,23,42,0.5)",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  header: {
    margin: 0,
    paddingBottom: "8px",
    borderBottom: "1px solid #e5e7eb",
    fontSize: "18px",
    fontWeight: 600,
    color: "#0f172a",
  },
  messages: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    padding: "8px 0",
    maxHeight: "60vh",
    overflowY: "auto",
  },
  message: {
    maxWidth: "80%",
    padding: "8px 10px",
    borderRadius: "8px",
    display: "flex",
    flexDirection: "column",
    gap: "4px",
  },
  roleLabel: {
    fontSize: "11px",
    opacity: 0.8,
  },
  text: {
    fontSize: "14px",
    whiteSpace: "pre-wrap",
  },
  sources: {
    marginTop: "4px",
    paddingTop: "4px",
    borderTop: "1px dashed rgba(148,163,184,0.8)",
  },
  sourcesLabel: {
    fontSize: "11px",
    opacity: 0.8,
    marginBottom: "2px",
  },
  sourceItem: {
    fontSize: "12px",
    color: "#0f172a",
  },
  category: {
    marginLeft: "4px",
    color: "#64748b",
  },
  score: {
    marginLeft: "6px",
    fontSize: "11px",
    color: "#94a3b8",
  },
  inputRow: {
    display: "flex",
    gap: "8px",
    paddingTop: "8px",
    borderTop: "1px solid #e5e7eb",
  },
  textarea: {
    flex: 1,
    resize: "none",
    minHeight: "48px",
    maxHeight: "96px",
    padding: "8px",
    borderRadius: "8px",
    border: "1px solid #cbd5f5",
    fontSize: "14px",
    fontFamily: "system-ui, sans-serif",
  },
  button: {
    minWidth: "96px",
    borderRadius: "8px",
    border: "none",
    backgroundColor: "#16a34a",
    color: "white",
    fontWeight: 600,
    fontSize: "14px",
    cursor: "pointer",
    padding: "0 12px",
  },
};

export default App;