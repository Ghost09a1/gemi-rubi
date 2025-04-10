"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Layout from "@/components/Layout";
import CharacterTabs, { TabPanel } from "@/components/characters/CharacterTabs";
import { mockKinkCategories, mockKinks } from "@/components/characters/KinkManagement";

// Mock user for layout
const mockUser = {
  username: "player123",
};

// Mock character data
const mockCharacters = [
  {
    id: "1",
    name: "Azura Nightshade",
    species: "Elf",
    gender: "Female",
    age: "182",
    status: "available",
    height: "5'8\"",
    bodyType: "Slender",
    eyeColor: "Violet",
    hairColor: "Silver",
    created_at: "2023-04-15T14:00:00Z",
    updated_at: "2024-03-01T09:30:00Z",
    image: "https://ext.same-assets.com/2421641290/elf-character.jpg",
    personality: "Azura is mysterious and reserved, preferring the company of ancient tomes to most people. She has a dry wit that emerges once she becomes comfortable around others. Her dedication to mastering arcane arts borders on obsessive, often causing her to forget basic needs like eating or sleeping when deep in study.",
    background: "Born to a noble elven family in the ancient forest of Silvermoon, Azura showed an aptitude for magic at a young age. She left her homeland to study at the prestigious Academy of Arcane Arts, where she excelled but was often criticized for her unorthodox approach to spellcrafting. After a magical experiment went awry, she was forced to leave the Academy and now wanders the realm seeking forgotten knowledge and rare magical artifacts.",
    appearanceDescription: "Azura has pale skin with a subtle silver sheen that seems to glow in moonlight. Her waist-length silver hair is usually adorned with small braids and magical trinkets. She has delicate elven features with high cheekbones and pointed ears adorned with multiple earrings. Her eyes are an unusual violet color that shifts to a deep purple when she uses magic. She typically wears flowing robes in deep blues and purples with silver embroidery, and always carries a staff crafted from ancient silverwood.",
    kinkPreferences: [
      { kinkId: "long-term", rating: "fave" },
      { kinkId: "story-focused", rating: "fave" },
      { kinkId: "adventure", rating: "yes" },
      { kinkId: "magic", rating: "fave" },
      { kinkId: "forbidden-love", rating: "yes" },
      { kinkId: "enemies-to-lovers", rating: "maybe" },
      { kinkId: "dom-sub", rating: "maybe" },
      { kinkId: "bondage", rating: "no" },
    ],
  },
  {
    id: "2",
    name: "Grimlock",
    species: "Orc",
    gender: "Male",
    age: "32",
    status: "away",
    height: "6'8\"",
    bodyType: "Muscular",
    eyeColor: "Amber",
    hairColor: "Black",
    created_at: "2023-07-22T11:20:00Z",
    updated_at: "2024-02-15T13:45:00Z",
    image: null,
    personality: "Grimlock is gruff and straightforward, with little patience for deception or political maneuvering. Despite his intimidating appearance, he has a strong sense of honor and loyalty to those who earn his respect. He enjoys simple pleasures like good food, strong drink, and honest combat, and has a surprising appreciation for poetry and song.",
    background: "Grimlock was born to the Bloodaxe clan, known for their fierce warriors. When his clan was decimated by a rival tribe, he was taken as a slave and forced to fight in gladiatorial arenas for many years. He eventually earned his freedom through combat prowess and now works as a mercenary, though he dreams of one day rebuilding his clan and reclaiming their ancestral lands.",
    appearanceDescription: "Grimlock stands well above most humans, with broad shoulders and a powerful build developed through years of combat. His green skin is covered in ritual scarification and battle scars, each telling a story of his past. He has prominent tusks and a strong jaw, with amber eyes that seem to glow with intensity when he's angry. His black hair is worn in warrior braids adorned with small bones and metal rings. He typically wears leather and fur armor reinforced with metal plates, and carries a massive double-bladed axe that most humans would struggle to even lift.",
    kinkPreferences: [
      { kinkId: "adventure", rating: "fave" },
      { kinkId: "short-term", rating: "yes" },
      { kinkId: "master-servant", rating: "maybe" },
      { kinkId: "capture", rating: "yes" },
      { kinkId: "enemies-to-lovers", rating: "fave" },
    ],
  },
  {
    id: "3",
    name: "Luna Moonshadow",
    species: "Kitsune",
    gender: "Female",
    age: "103",
    status: "looking",
    height: "5'4\"",
    bodyType: "Petite",
    eyeColor: "Gold",
    hairColor: "White with blue tips",
    created_at: "2024-01-10T16:30:00Z",
    updated_at: "2024-04-01T10:15:00Z",
    image: "https://ext.same-assets.com/2421641290/kitsune-character.jpg",
    personality: "Luna is playful and mischievous, delighting in clever tricks and riddles. She's naturally curious about everything, which often leads her into trouble. She can be flirtatious and charming when it suits her purposes, but genuinely values deep connections and will fiercely protect those she cares about. Her mood can shift as quickly as the phases of the moon she's named after.",
    background: "Luna comes from an ancient line of nine-tailed kitsune who serve as guardians of the sacred mountain shrines. Currently possessing four tails, she left her home to gain the experiences and wisdom needed to earn her remaining tails. She travels between the mortal and spirit realms, acting as a messenger and sometimes trickster. She's particularly drawn to human settlements, fascinated by their creativity and emotional complexity.",
    appearanceDescription: "Luna has a delicate build with fox-like features including pointed ears atop her head and four fluffy tails that seem to shimmer with moonlight. Her hair falls to her mid-back in waves, predominantly white with ethereal blue tips that glow faintly in darkness. Her golden eyes have vertical pupils that widen when excited or hunting. Her skin is fair with occasional patches of white fur at her joints and along her spine. She typically wears traditional shrine maiden attire in white and celestial blue, adorned with silver bells that chime softly as she moves. In her more playful moments, she may partially transform, showing more fox-like features.",
    kinkPreferences: [
      { kinkId: "transformation", rating: "fave" },
      { kinkId: "casual", rating: "yes" },
      { kinkId: "mythical-creatures", rating: "fave" },
      { kinkId: "supernatural", rating: "fave" },
      { kinkId: "playful", rating: "yes" },
      { kinkId: "size-difference", rating: "maybe" },
    ],
  },
];

export default function CharacterDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [character, setCharacter] = useState<typeof mockCharacters[0] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("profile");

  useEffect(() => {
    const characterId = params.id as string;

    // Simulate API fetch with a delay
    const timer = setTimeout(() => {
      const foundCharacter = mockCharacters.find(char => char.id === characterId);
      if (foundCharacter) {
        setCharacter(foundCharacter);
      }
      setIsLoading(false);
    }, 600);

    return () => clearTimeout(timer);
  }, [params.id]);

  // Function to get kink category name
  const getKinkCategoryName = (kinkId: string) => {
    const kink = mockKinks.find(k => k.id === kinkId);
    if (!kink) return "Unknown";

    const category = mockKinkCategories.find(c => c.id === kink.categoryId);
    return category ? category.name : "Unknown";
  };

  const tabs = [
    { id: "profile", label: "Profile" },
    { id: "appearance", label: "Appearance" },
    { id: "kinks", label: "Kinks & Preferences" },
  ];

  // Define rating colors
  const ratingColors = {
    fave: "text-green-400 border-green-500",
    yes: "text-blue-400 border-blue-500",
    maybe: "text-yellow-400 border-yellow-500",
    no: "text-red-400 border-red-500",
  };

  // Status indicators
  const getStatusIndicator = (status: string) => {
    switch (status) {
      case "available":
        return { icon: "🟢", color: "text-green-500", label: "Available for RP" };
      case "away":
        return { icon: "🟠", color: "text-amber-500", label: "Away" };
      case "busy":
        return { icon: "🔴", color: "text-red-500", label: "Currently in RP" };
      case "looking":
        return { icon: "🔍", color: "text-blue-500", label: "Looking for RP" };
      case "private":
        return { icon: "🔒", color: "text-purple-500", label: "In Private RP" };
      default:
        return { icon: "⚪", color: "text-gray-500", label: "Unknown" };
    }
  };

  return (
    <Layout user={mockUser}>
      <div className="container mx-auto py-8 px-4">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 border-4 border-slate-600 border-t-blue-500 rounded-full animate-spin"></div>
            <p className="mt-6 text-slate-400">Loading character profile...</p>
          </div>
        ) : character ? (
          <div>
            {/* Character Header */}
            <div className="mb-8 flex flex-col md:flex-row gap-6">
              <div className="md:w-1/3 lg:w-1/4">
                <div className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700">
                  {character.image ? (
                    <img
                      src={character.image}
                      alt={character.name}
                      className="w-full h-auto object-cover aspect-square"
                    />
                  ) : (
                    <div className="w-full aspect-square bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
                      <div className="text-8xl opacity-60 font-light">
                        {character.name.charAt(0)}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="md:w-2/3 lg:w-3/4">
                <div className="flex flex-wrap items-center gap-3 mb-3">
                  <h1 className="text-3xl font-bold text-white">{character.name}</h1>
                  <div className={`px-3 py-1 rounded-full text-sm ${getStatusIndicator(character.status).color} border border-slate-700 bg-slate-800/50`}>
                    {getStatusIndicator(character.status).icon} {getStatusIndicator(character.status).label}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="bg-slate-800 rounded-md p-3 border border-slate-700">
                    <span className="text-sm text-slate-400 block">Species</span>
                    <span className="font-medium">{character.species}</span>
                  </div>
                  <div className="bg-slate-800 rounded-md p-3 border border-slate-700">
                    <span className="text-sm text-slate-400 block">Gender</span>
                    <span className="font-medium">{character.gender}</span>
                  </div>
                  <div className="bg-slate-800 rounded-md p-3 border border-slate-700">
                    <span className="text-sm text-slate-400 block">Age</span>
                    <span className="font-medium">{character.age}</span>
                  </div>
                  <div className="bg-slate-800 rounded-md p-3 border border-slate-700">
                    <span className="text-sm text-slate-400 block">Last Activity</span>
                    <span className="font-medium">{new Date(character.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="flex gap-4 flex-wrap mb-2">
                  <button
                    className="bg-blue-600 hover:bg-blue-500 text-white font-medium py-2 px-4 rounded-md inline-flex items-center"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    Send Message
                  </button>
                  <button
                    className="bg-purple-600 hover:bg-purple-500 text-white font-medium py-2 px-4 rounded-md inline-flex items-center"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    View Gallery
                  </button>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
              <CharacterTabs
                tabs={tabs}
                activeTab={activeTab}
                onChange={setActiveTab}
              />

              <div className="p-6">
                {/* Profile Tab */}
                <TabPanel id="profile" activeId={activeTab}>
                  <div className="space-y-8">
                    <div>
                      <h2 className="text-xl font-semibold mb-3 text-blue-400">Personality</h2>
                      <div className="bg-slate-700/30 rounded-md p-4 border border-slate-700">
                        <p className="whitespace-pre-line">{character.personality}</p>
                      </div>
                    </div>

                    <div>
                      <h2 className="text-xl font-semibold mb-3 text-blue-400">Background</h2>
                      <div className="bg-slate-700/30 rounded-md p-4 border border-slate-700">
                        <p className="whitespace-pre-line">{character.background}</p>
                      </div>
                    </div>
                  </div>
                </TabPanel>

                {/* Appearance Tab */}
                <TabPanel id="appearance" activeId={activeTab}>
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                      <div className="bg-slate-700/30 rounded-md p-3 border border-slate-700">
                        <span className="text-sm text-slate-400 block">Height</span>
                        <span className="font-medium">{character.height || "Not specified"}</span>
                      </div>
                      <div className="bg-slate-700/30 rounded-md p-3 border border-slate-700">
                        <span className="text-sm text-slate-400 block">Body Type</span>
                        <span className="font-medium">{character.bodyType || "Not specified"}</span>
                      </div>
                      <div className="bg-slate-700/30 rounded-md p-3 border border-slate-700">
                        <span className="text-sm text-slate-400 block">Eye Color</span>
                        <span className="font-medium">{character.eyeColor || "Not specified"}</span>
                      </div>
                      <div className="bg-slate-700/30 rounded-md p-3 border border-slate-700">
                        <span className="text-sm text-slate-400 block">Hair Color</span>
                        <span className="font-medium">{character.hairColor || "Not specified"}</span>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold mb-3 text-blue-400">Detailed Appearance</h3>
                      <div className="bg-slate-700/30 rounded-md p-4 border border-slate-700">
                        <p className="whitespace-pre-line">{character.appearanceDescription || "No detailed appearance provided."}</p>
                      </div>
                    </div>
                  </div>
                </TabPanel>

                {/* Kinks Tab */}
                <TabPanel id="kinks" activeId={activeTab}>
                  <div>
                    <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                        <span className="text-sm text-slate-300">Favorite: Strong interest</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                        <span className="text-sm text-slate-300">Yes: Interested</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
                        <span className="text-sm text-slate-300">Maybe: Might be open to</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                        <span className="text-sm text-slate-300">No: Not interested</span>
                      </div>
                    </div>

                    {character.kinkPreferences?.length > 0 ? (
                      <div className="space-y-6">
                        {/* Group preferences by category */}
                        {mockKinkCategories.map(category => {
                          // Get kinks for this category
                          const categoryKinks = character.kinkPreferences
                            .filter(pref => {
                              const kink = mockKinks.find(k => k.id === pref.kinkId);
                              return kink && kink.categoryId === category.id;
                            })
                            .sort((a, b) => {
                              // Sort by rating: fave > yes > maybe > no
                              const ratingOrder = { fave: 0, yes: 1, maybe: 2, no: 3 };
                              return ratingOrder[a.rating] - ratingOrder[b.rating];
                            });

                          if (categoryKinks.length === 0) return null;

                          return (
                            <div key={category.id}>
                              <h3 className="text-lg font-semibold mb-3 text-blue-400">{category.name}</h3>
                              <div className="bg-slate-700/30 rounded-md p-4 border border-slate-700">
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                                  {categoryKinks.map(pref => {
                                    const kink = mockKinks.find(k => k.id === pref.kinkId);
                                    if (!kink) return null;

                                    return (
                                      <div
                                        key={pref.kinkId}
                                        className={`px-3 py-2 rounded-md border ${ratingColors[pref.rating]} bg-slate-800/60`}
                                      >
                                        <div className="flex items-center justify-between">
                                          <span>{kink.name}</span>
                                          <span className={`text-xs font-medium ${ratingColors[pref.rating]}`}>
                                            {pref.rating.charAt(0).toUpperCase() + pref.rating.slice(1)}
                                          </span>
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="bg-slate-700/30 rounded-md p-6 text-center border border-slate-700">
                        <p className="text-slate-400">This character has not set any kink preferences yet.</p>
                      </div>
                    )}
                  </div>
                </TabPanel>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-slate-800 rounded-lg p-8 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-semibold mb-2">Character Not Found</h2>
            <p className="text-slate-400 mb-6">
              We couldn't find the character you're looking for. It may have been deleted or you may not have permission to view it.
            </p>
            <button
              onClick={() => router.push("/characters")}
              className="bg-blue-600 hover:bg-blue-500 text-white font-medium py-2 px-6 rounded-md"
            >
              Back to Characters
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
