"use client";

import { useState, useRef, useEffect } from "react";
import { sendChatMessage, ChatSource } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  confidence?: number | null;
  isEmergency?: boolean;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Namaste! I'm your public health assistant. Ask me about diseases, prevention, government health schemes, or how to find a doctor. I provide educational information only — not a diagnosis.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(input, sessionId);
      setSessionId(res.session_id);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          confidence: res.confidence,
          isEmergency: res.is_emergency,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong. Please try again or contact a healthcare provider directly." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-white">
      <header className="px-4 py-3 border-b bg-emerald-700 text-white">
        <h1 className="text-lg font-semibold">JanSwasthya AI</h1>
        <p className="text-xs text-emerald-100">Educational health information only — not a substitute for a doctor</p>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4" aria-live="polite" role="log">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-emerald-600 text-white rounded-br-sm"
                  : msg.isEmergency
                  ? "bg-red-50 border-2 border-red-400 text-red-900 rounded-bl-sm"
                  : "bg-gray-100 text-gray-900 rounded-bl-sm"
              }`}
            >
              {msg.isEmergency && (
                <div className="font-bold text-red-700 mb-1 flex items-center gap-1">⚠️ Emergency</div>
              )}
              <p className="whitespace-pre-line">{msg.content}</p>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-500">
                  Sources: {msg.sources.map((s) => s.publisher).join(", ")}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-sm text-gray-400 italic">Thinking...</div>}
        <div ref={bottomRef} />
      </div>

      <div className="border-t px-4 py-3 flex gap-2">
        <input
          className="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          placeholder="Ask about a health topic..."
          aria-label="Health question input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          aria-label="Send message"
          className="bg-emerald-700 text-white rounded-full px-5 py-2 text-sm font-medium disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
