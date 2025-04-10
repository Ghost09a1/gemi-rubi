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
  const [editingId, setEditingId] = useState<number | null>(null);
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
      const res = await fetch("http://localhost:8000/api/characters/create/", {
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

  const handleUpdate = async (id: number, newName: string, newDescription: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/characters/${id}/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newName, description: newDescription }),
      });

      if (!res.ok) {
        throw new Error("Failed to update character");
      }

      const updatedChar = await res.json();
      setCharacters(
        characters.map(char => (char.id === id ? updatedChar : char))
      );
      setEditingId(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this character?")) {
      try {
        const res = await fetch(`http://localhost:8000/api/characters/${id}/`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          throw new Error("Failed to delete character");
        }

        setCharacters(characters.filter(char => char.id !== id));
      } catch (err: any) {
        setError(err.message);
      }
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Your Characters</h1>

      <ul className="mb-6 space-y-2">
        {characters.map(char => (
          <li key={char.id} className="border p-2 rounded flex items-center">
            {editingId === char.id ? (
              <div className="flex-1">
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full p-1 border rounded mr-2"
                />
                <textarea
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  className="w-full p-1 border rounded mt-1"
                />
              </div>
            ) : (
              <div className="flex-1">
                <strong>{char.name}</strong>: {char.description}
              </div>
            )}

            {editingId === char.id ? (
              <div>
                <button
                  onClick={() => handleUpdate(char.id, name, description)}
                  className="bg-blue-500 text-white p-1 rounded mr-1"
                >
                  Save
                </button>
                <button onClick={() => setEditingId(null)} className="p-1 rounded">
                  Cancel
                </button>
              </div>
            ) : (
              <div>
                <button onClick={() => { setName(char.name); setDescription(char.description); setEditingId(char.id) }} className="bg-yellow-500 text-white p-1 rounded mr-1">Update</button>
                <button onClick={() => handleDelete(char.id)} className="bg-red-500 text-white p-1 rounded">Delete</button>
              </div>
            )}
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
