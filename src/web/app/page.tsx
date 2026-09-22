"use client";

import { useState, useRef, useEffect } from "react";

export default function Chat() {
  const [messages, setMessages] = useState<{ role: "user" | "agent"; text: string }[]>([
    { role: "agent", text: "Hello! I am the Telesale Agent. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate a random session ID on load
  const [sessionId] = useState(() => Math.random().toString(36).substring(7));

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMessage }]);
    setIsLoading(true);

    try {
      // Determine the API URL (works for local dev and Vercel)
      const apiUrl = process.env.NODE_ENV === "development" 
        ? "http://localhost:8000/api/chat" 
        : "/api/chat";

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: sessionId,
          message: userMessage,
        }),
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { role: "agent", text: data.response || "Sorry, I couldn't process that." }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: "agent", text: "Connection error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans text-gray-900">
      <header className="bg-white shadow-sm py-4 px-6 sticky top-0 z-10 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-blue-600">Telesale Agent</h1>
        <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">Session: {sessionId}</div>
      </header>

      <main className="flex-1 overflow-y-auto p-4 sm:p-6 pb-32">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-none"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 text-gray-500 rounded-2xl rounded-bl-none px-5 py-3 shadow-sm flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 fixed bottom-0 w-full p-4">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={sendMessage} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 border border-gray-300 rounded-full px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white px-6 py-3 rounded-full font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
            >
              Send
            </button>
          </form>
        </div>
      </footer>
    </div>
  );
}
