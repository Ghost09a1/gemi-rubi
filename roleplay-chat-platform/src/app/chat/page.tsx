"use client";

import { useState, useEffect, useRef } from "react";
import Layout from "@/components/Layout";
import Link from "next/link";

// Mock user for layout
const mockUser = {
  username: "player123",
};

// Mock character data for the demo
const mockCharacters = [
  {
    id: "1",
    name: "Azura Nightshade",
    image: "https://ext.same-assets.com/2421641290/elf-character.jpg",
    species: "Elf",
    status: "available",
  },
  {
    id: "2",
    name: "Grimlock",
    image: null,
    species: "Orc",
    status: "away",
  },
  {
    id: "3",
    name: "Luna Moonshadow",
    image: "https://ext.same-assets.com/2421641290/kitsune-character.jpg",
    species: "Kitsune",
    status: "looking",
  },
];

// Mock chat rooms
const mockChatRooms = [
  {
    id: "1",
    name: "Mystic Tavern",
    description: "A cozy tavern for adventurers to meet and share tales",
    participants: 12,
    isPrivate: false,
    lastActivity: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
  },
  {
    id: "2",
    name: "Dragon's Lair",
    description: "For those brave enough to face the dragon",
    participants: 5,
    isPrivate: false,
    lastActivity: new Date(Date.now() - 45 * 60 * 1000).toISOString(), // 45 minutes ago
  },
  {
    id: "3",
    name: "Secret Garden",
    description: "A hidden garden where lovers meet",
    participants: 8,
    isPrivate: false,
    lastActivity: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
  },
  {
    id: "4",
    name: "Azura & Grimlock",
    description: "Private chat between Azura and Grimlock",
    participants: 2,
    isPrivate: true,
    lastActivity: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
  },
];

// Mock messages for the demo
const initialMessages = [
  {
    id: "1",
    roomId: "1",
    senderId: "system",
    senderName: "System",
    message: "Welcome to the Mystic Tavern! Please be respectful of other players.",
    timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
    isSystem: true,
  },
  {
    id: "2",
    roomId: "1",
    senderId: "2",
    senderName: "Grimlock",
    message: "*enters the tavern with heavy footsteps, his massive frame causing the wooden floorboards to creak. He surveys the room with piercing amber eyes, then approaches the bar* A mug of your strongest ale, barkeep.",
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(), // 15 minutes ago
    character: mockCharacters.find(c => c.id === "2"),
  },
  {
    id: "3",
    roomId: "1",
    senderId: "5",
    senderName: "Lyra Emberheart",
    message: "*The red-haired bard looks up from her table in the corner, her fingers pausing on the strings of her lute* Well, aren't you a sight. New in town, big fellow?",
    timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(), // 10 minutes ago
    character: {
      id: "5",
      name: "Lyra Emberheart",
      image: null,
      species: "Human",
      status: "available",
    },
  },
];

// Chat Types
interface Message {
  id: string;
  roomId: string;
  senderId: string;
  senderName: string;
  message: string;
  timestamp: string;
  isSystem?: boolean;
  character?: {
    id: string;
    name: string;
    image: string | null;
    species: string;
    status: string;
  };
}

interface ChatRoom {
  id: string;
  name: string;
  description: string;
  participants: number;
  isPrivate: boolean;
  lastActivity: string;
}

export default function ChatPage() {
  const [activeCharacter, setActiveCharacter] = useState(mockCharacters[0]);
  const [activeRoomId, setActiveRoomId] = useState(mockChatRooms[0].id);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [newMessage, setNewMessage] = useState("");
  const [editingRoomId, setEditingRoomId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Time formatting helpers
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatLastActivity = (timestamp: string) => {
    const now = new Date();
    const date = new Date(timestamp);
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (60 * 1000));

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Get current room
  const currentRoom = mockChatRooms.find(room => room.id === activeRoomId);

  // Filter messages for current room
  const roomMessages = messages.filter(msg => msg.roomId === activeRoomId);

  // Handle sending a new message
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const newMsg: Message = {
      id: Date.now().toString(),
      roomId: activeRoomId,
      senderId: activeCharacter.id,
      senderName: activeCharacter.name,
      message: newMessage,
      timestamp: new Date().toISOString(),
      character: activeCharacter,
    };

    setMessages([...messages, newMsg]);
    setNewMessage("");
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "available":
        return "🟢";
      case "away":
        return "🟠";
      case "busy":
        return "🔴";
      case "looking":
        return "🔍";
      case "private":
        return "🔒";
      default:
        return "⚪";
    }
  };

  return (
    <Layout user={mockUser} currentCharacter={activeCharacter}>
      <div className="container mx-auto py-4 px-4">
        <h1 className="text-3xl font-bold mb-2">Chat</h1>
        <p className="text-slate-400 mb-6">
          Engage in roleplay with other characters
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Character Selection */}
            <div className="bg-slate-800 rounded-lg border border-slate-700 p-4">
              <h2 className="text-lg font-semibold mb-3">Your Characters</h2>
              <div className="space-y-2">
                {mockCharacters.map((character) => (
                  <button
                    key={character.id}
                    onClick={() => setActiveCharacter(character)}
                    className={`w-full flex items-center p-2 rounded-md ${
                      activeCharacter.id === character.id
                        ? "bg-blue-600"
                        : "bg-slate-700 hover:bg-slate-600"
                    }`}
                  >
                    <div className="flex-shrink-0 mr-3">
                      {character.image ? (
                        <img
                          src={character.image}
                          alt={character.name}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center">
                          <span className="text-lg">{character.name.charAt(0)}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex-grow overflow-hidden">
                      <div className="font-medium truncate">{character.name}</div>
                      <div className="text-xs text-slate-400 truncate">{character.species}</div>
                    </div>
                    <div className="ml-2">
                      <span className="text-xs">{getStatusIcon(character.status)}</span>
                    </div>
                  </button>
                ))}
              </div>
              <div className="mt-3 pt-3 border-t border-slate-700">
                <Link
                  href="/characters/create"
                  className="text-blue-400 hover:text-blue-300 text-sm flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create New Character
                </Link>
              </div>
            </div>

            {/* Chat Rooms */}
            <div className="bg-slate-800 rounded-lg border border-slate-700 p-4">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-lg font-semibold">Chat Rooms</h2>
                <button
                  onClick={() => {}}
                  className="text-sm bg-blue-600 hover:bg-blue-500 text-white px-2 py-1 rounded flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New
                </button>
              </div>

              <div className="space-y-2">
                {mockChatRooms.map((room) => (
                  <button
                    key={room.id}
                    onClick={() => setActiveRoomId(room.id)}
                    className={`w-full text-left p-2 rounded-md ${
                      activeRoomId === room.id
                        ? "bg-blue-600"
                        : "bg-slate-700 hover:bg-slate-600"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium flex items-center">
                        {room.isPrivate && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                          </svg>
                        )}
                        {room.name}
                      </span>
                      <span className="text-xs text-slate-400">{formatLastActivity(room.lastActivity)}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1 flex justify-between">
                      <span className="truncate max-w-[180px]">{room.description}</span>
                      <span>{room.participants} online</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="bg-slate-800 rounded-lg border border-slate-700 flex flex-col h-[75vh]">
              {/* Chat Header */}
              <div className="p-3 border-b border-slate-700 flex justify-between items-center">
                <div>
                  <h2 className="font-semibold flex items-center">
                    {currentRoom?.isPrivate && (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    )}
                    {currentRoom?.name}
                  </h2>
                  <p className="text-xs text-slate-400">{currentRoom?.description}</p>
                </div>
                <div className="text-sm text-slate-400">
                  {currentRoom?.participants} participants
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {roomMessages.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-slate-400">No messages yet. Start the conversation!</p>
                  </div>
                ) : (
                  roomMessages.map((msg) => (
                    <div key={msg.id} className={`${msg.isSystem ? "opacity-70" : ""}`}>
                      {msg.isSystem ? (
                        <div className="bg-slate-700/30 rounded-md p-2 text-center">
                          <p className="text-sm text-slate-400">{msg.message}</p>
                        </div>
                      ) : (
                        <div className="flex gap-3">
                          <div className="flex-shrink-0">
                            {msg.character?.image ? (
                              <img
                                src={msg.character.image}
                                alt={msg.senderName}
                                className="w-10 h-10 rounded-full object-cover"
                              />
                            ) : (
                              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center">
                                <span className="text-lg">{msg.senderName.charAt(0)}</span>
                              </div>
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center mb-1">
                              <span className="font-medium mr-2">{msg.senderName}</span>
                              <span className="text-xs text-slate-400">
                                {formatTimestamp(msg.timestamp)}
                              </span>
                            </div>
                            <div className="bg-slate-700/30 rounded-md p-3 border border-slate-700">
                              <p className="whitespace-pre-line">{msg.message}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-3 border-t border-slate-700">
                <form onSubmit={handleSendMessage}>
                  <div className="flex items-center">
                    <div className="flex-shrink-0 mr-3">
                      {activeCharacter.image ? (
                        <img
                          src={activeCharacter.image}
                          alt={activeCharacter.name}
                          className="w-8 h-8 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center">
                          <span className="text-sm">{activeCharacter.name.charAt(0)}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex-grow relative">
                      <textarea
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white resize-none"
                        placeholder={`Type a message as ${activeCharacter.name}...`}
                        rows={2}
                      />
                      <div className="absolute right-2 bottom-2 flex space-x-1">
                        <button
                          type="button"
                          className="text-slate-400 hover:text-white p-1"
                          title="Format Text"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                          </svg>
                        </button>
                        <button
                          type="button"
                          className="text-slate-400 hover:text-white p-1"
                          title="Emoji"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    <button
                      type="submit"
                      className="ml-3 bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-md flex-shrink-0"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
