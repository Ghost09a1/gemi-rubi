"use client";

import { useEffect, useRef, useState } from "react";

type Message = {
  id?: number;
  sender: string;
  content: string;
  timestamp?: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access") : null;
    if (!token) return;

    ws.current = new WebSocket("ws://localhost:8000/ws/chat/");

    ws.current.onopen = () => console.log("WebSocket connected");
    ws.current.onclose = () => console.log("WebSocket disconnected");
    ws.current.onerror = (err) => console.error("WebSocket error:", err);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const sendMessage = () => {
    if (ws.current && newMessage.trim() !== "") {
      const message: Message = {
        sender: "You",
        content: newMessage,
      };
      ws.current.send(JSON.stringify(message));
      setMessages((prev) => [...prev, message]);
      setNewMessage("");
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Chat</h1>
      <div className="h-96 overflow-y-auto border p-4 rounded mb-4 bg-white">
        {messages.map((msg, index) => (
          <div key={index} className="mb-2">
            <strong>{msg.sender}</strong>: {msg.content}
          </div>
        ))}
      </div>
      <div className="flex space-x-2">
        <input
          type="text"
          placeholder="Type your message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          className="flex-grow p-2 border rounded"
        />
        <button onClick={sendMessage} className="p-2 bg-blue-600 text-white rounded">
          Send
        </button>
      </div>
    </div>
  );
}
