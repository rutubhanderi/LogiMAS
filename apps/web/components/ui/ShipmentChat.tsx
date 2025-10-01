"use client";

import { useState, FormEvent, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

// Define the structure for a single chat message
type Message = {
  role: "user" | "assistant";
  content: string;
};

// Simple SVG components for avatars
const UserAvatar = () => (
  <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
    YOU
  </div>
);
const AssistantAvatar = () => (
  <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 16 16"
      fill="currentColor"
      className="w-5 h-5 text-white"
    >
      <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM12.735 14c.618 0 1.093-.561.872-1.139a6.002 6.002 0 0 0-11.215 0c-.22.578.254 1.139.872 1.139h9.47Z" />
    </svg>
  </div>
);

export function ShipmentChat() {
  const [query, setQuery] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! Please provide a Shipment ID to get its status or calculate its cost.",
    },
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    const userMessage: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMessage]);
    setQuery("");

    try {
      const res = await fetch("http://127.0.0.1:8000/agent/invoke", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || `API Error: ${res.statusText}`);
      }

      const data = await res.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "Sorry, I couldn't generate a response.",
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        role: "assistant",
        content: `Sorry, an error occurred: ${err.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-md h-[70vh] flex flex-col">
      {/* Message History Area */}
      <div className="flex-grow p-6 overflow-y-auto">
        <div className="space-y-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              {message.role === "assistant" ? (
                <AssistantAvatar />
              ) : (
                <UserAvatar />
              )}
              <div
                className={`p-3 rounded-lg max-w-xl text-white ${
                  message.role === "user" ? "bg-blue-600" : "bg-slate-700"
                }`}
              >
                <div className="prose prose-invert prose-p:my-0 text-white">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}

          {/* --- THIS IS THE CORRECTED LOADING INDICATOR --- */}
          {isLoading && (
            <div className="flex items-start gap-3 flex-row">
              <AssistantAvatar />
              <div className="p-3 rounded-lg max-w-xl bg-slate-700">
                <div className="flex items-center justify-center gap-2">
                  <span className="h-2 w-2 bg-slate-400 rounded-full animate-pulse [animation-delay:-0.3s]"></span>
                  <span className="h-2 w-2 bg-slate-400 rounded-full animate-pulse [animation-delay:-0.15s]"></span>
                  <span className="h-2 w-2 bg-slate-400 rounded-full animate-pulse"></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form Area */}
      <div className="p-4 border-t border-gray-200 flex-shrink-0">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What is the status of shipment..."
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-blue-600 font-semibold px-4 rounded-md text-white hover:bg-blue-700 disabled:bg-gray-400"
            disabled={isLoading}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
