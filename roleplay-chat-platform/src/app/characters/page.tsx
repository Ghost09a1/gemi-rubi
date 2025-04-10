"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Layout from "@/components/Layout";

// Mocked character data since we don't have a real backend connection yet
const mockCharacters = [
  {
    id: "1",
    name: "Azura Nightshade",
    species: "Elf",
    gender: "Female",
    status: "available",
    created_at: "2023-04-15T14:00:00Z",
    updated_at: "2024-03-01T09:30:00Z",
    image: "https://ext.same-assets.com/2421641290/elf-character.jpg",
  },
  {
    id: "2",
    name: "Grimlock",
    species: "Orc",
    gender: "Male",
    status: "away",
    created_at: "2023-07-22T11:20:00Z",
    updated_at: "2024-02-15T13:45:00Z",
    image: null,
  },
  {
    id: "3",
    name: "Luna Moonshadow",
    species: "Kitsune",
    gender: "Female",
    status: "looking",
    created_at: "2024-01-10T16:30:00Z",
    updated_at: "2024-04-01T10:15:00Z",
    image: "https://ext.same-assets.com/2421641290/kitsune-character.jpg",
  },
];

// Mock user for layout
const mockUser = {
  username: "player123",
};

interface Character {
  id: string;
  name: string;
  species: string;
  gender: string;
  status: string;
  created_at: string;
  updated_at: string;
  image: string | null;
}

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");

  // Mock loading effect
  useEffect(() => {
    // Simulate API fetch delay
    const timer = setTimeout(() => {
      setCharacters(mockCharacters);
      setIsLoading(false);
    }, 800);

    return () => clearTimeout(timer);
  }, []);

  // Filter characters based on search term
  const filteredCharacters = characters.filter((character) =>
    character.name.toLowerCase().includes(filter.toLowerCase()) ||
    character.species.toLowerCase().includes(filter.toLowerCase())
  );

  // Get status icon and color
  const getStatusIndicator = (status: string) => {
    switch (status) {
      case "available":
        return { icon: "🟢", color: "text-green-500" };
      case "away":
        return { icon: "🟠", color: "text-amber-500" };
      case "busy":
        return { icon: "🔴", color: "text-red-500" };
      case "looking":
        return { icon: "🔍", color: "text-blue-500" };
      case "private":
        return { icon: "🔒", color: "text-purple-500" };
      default:
        return { icon: "⚪", color: "text-gray-500" };
    }
  };

  return (
    <Layout user={mockUser}>
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">Your Characters</h1>
            <p className="text-slate-400">
              Manage your character profiles or create new ones
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative">
              <input
                type="text"
                placeholder="Search characters..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 absolute left-3 top-2.5 text-slate-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>

            <Link
              href="/characters/create"
              className="bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-700 hover:to-teal-600 text-white font-medium py-2 px-4 rounded-md flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Create Character
            </Link>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500 text-white p-4 rounded-md mb-6">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="w-12 h-12 border-4 border-slate-600 border-t-blue-500 rounded-full animate-spin"></div>
            <p className="mt-4 text-slate-400">Loading your characters...</p>
          </div>
        ) : filteredCharacters.length === 0 ? (
          filter ? (
            <div className="bg-slate-800 rounded-lg p-8 text-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-16 w-16 mx-auto text-slate-600 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <h2 className="text-xl font-semibold mb-2">No Characters Found</h2>
              <p className="text-slate-400 mb-4">
                We couldn't find any characters matching "{filter}"
              </p>
              <button
                onClick={() => setFilter("")}
                className="text-blue-400 hover:underline"
              >
                Clear filter
              </button>
            </div>
          ) : (
            <div className="bg-slate-800 rounded-lg p-8 text-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-16 w-16 mx-auto text-slate-600 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              <h2 className="text-xl font-semibold mb-2">No Characters Yet</h2>
              <p className="text-slate-400 mb-6">
                You haven't created any characters yet. Create your first character to get started!
              </p>
              <Link
                href="/characters/create"
                className="bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-700 hover:to-teal-600 text-white font-medium py-2 px-6 rounded-md inline-flex items-center"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Create Your First Character
              </Link>
            </div>
          )
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCharacters.map((character) => {
              const statusInfo = getStatusIndicator(character.status);
              return (
                <div
                  key={character.id}
                  className="bg-slate-800 rounded-lg overflow-hidden hover:shadow-lg transition-shadow border border-slate-700 flex flex-col"
                >
                  <div className="h-48 bg-slate-700 relative">
                    {character.image ? (
                      <img
                        src={character.image}
                        alt={character.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-700 to-slate-800">
                        <div className="text-6xl opacity-60 font-light">
                          {character.name.charAt(0)}
                        </div>
                      </div>
                    )}
                    <div className="absolute top-3 right-3 flex space-x-2">
                      <span className={`text-sm px-2 py-1 rounded-md bg-slate-900/80 ${statusInfo.color}`}>
                        {statusInfo.icon} {character.status}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 flex-grow">
                    <h3 className="text-xl font-semibold mb-1 text-white">
                      {character.name}
                    </h3>
                    <div className="text-sm text-slate-400 mb-2">
                      {character.species} • {character.gender}
                    </div>
                    <div className="mt-3 text-xs text-slate-500">
                      Last updated: {new Date(character.updated_at).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="border-t border-slate-700 p-3 bg-slate-800/50 flex justify-between">
                    <Link
                      href={`/characters/${character.id}`}
                      className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                    >
                      View Profile
                    </Link>
                    <Link
                      href={`/characters/${character.id}/edit`}
                      className="text-slate-400 hover:text-white text-sm font-medium"
                    >
                      Edit
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Layout>
  );
}
