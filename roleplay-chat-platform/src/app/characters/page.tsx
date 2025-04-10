"use client";

import { useEffect, useState } from "react";

type Character = {
  id: number;
  name: string;
  description: string;
};

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("access") : null;

  useEffect(() => {
    if (token) {
      fetch("http://localhost:8000/api/characters/", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(res => res.json())
        .then(data => setCharacters(data))
        .catch(err => console.error(err));
    }
  }, [token]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/characters/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description }),
      });

      if (!res.ok) {
        throw new Error("Failed to create character");
      }

      const newChar = await res.json();
      setCharacters([...characters, newChar]);
      setName("");
      setDescription("");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Your Characters</h1>

      <ul className="mb-6 space-y-2">
        {characters.map(char => (
          <li key={char.id} className="border p-2 rounded">
            <strong>{char.name}</strong>: {char.description}
          </li>
        ))}
      </ul>

      <h2 className="text-xl font-semibold mb-2">Create New Character</h2>
      <form onSubmit={handleCreate} className="space-y-3">
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={e => setName(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
        <textarea
          placeholder="Description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
        {error && <p className="text-red-500">{error}</p>}
        <button type="submit" className="w-full p-2 bg-purple-600 text-white rounded">
          Create Character
        </button>
      </form>
    </div>
  );
}
