import { useState, useRef, useEffect } from "react";

interface ChatMessage {
  type: "ai" | "user";
  text: string;
}

interface ChatWidgetProps {
  isOpen: boolean;
  onToggle: () => void;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const API_URL = `${API_BASE_URL}/api`;

export default function ChatWidget({ isOpen, onToggle }: ChatWidgetProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      type: "ai",
      text: "Hi! Ask me about my experience, projects, or skills.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    
    // Add user message to chat
    setMessages((prev) => [...prev, { type: "user", text: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/ai-chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();
      
      // Save session ID for subsequent messages
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Add AI response to chat
      setMessages((prev) => [
        ...prev,
        { type: "ai", text: data.response },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          type: "ai",
          text: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div
      className={`chat-widget ${isOpen ? "is-open" : "is-collapsed"}`}
      aria-live="polite"
    >
      <button
        className="chat-toggle"
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
        aria-label={isOpen ? "Collapse chat" : "Open chat"}
      >
        {isOpen ? "−" : "AI"}
      </button>
      <div className="chat-widget__header">
        <div className="chat-widget__title">
          <span className="chat-dot" />
          AI Assistant
        </div>
      </div>
      <div className="chat-widget__body">
        <div className="chat-widget__messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble chat-bubble--${msg.type}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div className="chat-bubble chat-bubble--ai">
              <span className="typing-indicator">
                <span>.</span><span>.</span><span>.</span>
              </span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="chat-widget__input">
          <input
            type="text"
            placeholder="Ask about skills, education, or projects..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button 
            type="button" 
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
