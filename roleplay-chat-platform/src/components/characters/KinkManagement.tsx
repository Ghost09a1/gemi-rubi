"use client";

import { useState } from "react";
import { KinkRating } from "./FormInputs";

// Kink category type
interface KinkCategory {
  id: string;
  name: string;
  description?: string;
}

// Kink type
interface Kink {
  id: string;
  name: string;
  categoryId: string;
  description?: string;
}

// Character kink preference (what the user has selected)
interface KinkPreference {
  kinkId: string;
  rating: "fave" | "yes" | "maybe" | "no" | "";
}

// Props for the component
interface KinkManagementProps {
  categories: KinkCategory[];
  kinks: Kink[];
  userPreferences: KinkPreference[];
  onPreferenceChange: (kinkId: string, rating: KinkPreference["rating"]) => void;
}

export default function KinkManagement({
  categories,
  kinks,
  userPreferences,
  onPreferenceChange,
}: KinkManagementProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [showOnlyRated, setShowOnlyRated] = useState(false);

  // Get preference for a kink
  const getPreference = (kinkId: string): KinkPreference["rating"] => {
    const pref = userPreferences.find(p => p.kinkId === kinkId);
    return pref ? pref.rating : "";
  };

  // Filter kinks based on search, category, and rated filter
  const filteredKinks = kinks.filter(kink => {
    // Search filter
    const matchesSearch =
      searchTerm === "" ||
      kink.name.toLowerCase().includes(searchTerm.toLowerCase());

    // Category filter
    const matchesCategory =
      selectedCategory === "all" || kink.categoryId === selectedCategory;

    // Rated filter
    const matchesRatedFilter =
      !showOnlyRated || getPreference(kink.id) !== "";

    return matchesSearch && matchesCategory && matchesRatedFilter;
  });

  return (
    <div>
      {/* Filters */}
      <div className="mb-6 space-y-4">
        <div>
          <label htmlFor="search-kinks" className="sr-only">Search kinks</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-slate-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
              </svg>
            </div>
            <input
              id="search-kinks"
              name="search-kinks"
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="p-2 pl-10 block w-full bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Search kinks..."
            />
            {searchTerm && (
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-white"
                onClick={() => setSearchTerm("")}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </button>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="w-full md:w-auto">
            <label htmlFor="category-filter" className="block text-sm font-medium text-slate-400 mb-1">
              Category
            </label>
            <select
              id="category-filter"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="p-2 block w-full bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Categories</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <div className="flex items-center h-10">
              <input
                id="show-rated"
                type="checkbox"
                checked={showOnlyRated}
                onChange={() => setShowOnlyRated(!showOnlyRated)}
                className="h-4 w-4 text-blue-500 border-slate-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="show-rated" className="ml-2 block text-sm text-slate-300">
                Show only rated kinks
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-1 mb-6">
        <h3 className="text-lg font-medium text-white">Kink Ratings</h3>
        <p className="text-sm text-slate-400">
          Rate your preferences for each kink to help others understand your interests.
        </p>
      </div>

      {/* Kinks listing */}
      <div className="space-y-4">
        {filteredKinks.length === 0 ? (
          <div className="bg-slate-800 p-4 rounded-md text-center">
            <p className="text-slate-400">No kinks found matching your filters.</p>
          </div>
        ) : (
          <div>
            {selectedCategory === "all" && !searchTerm ? (
              // Group by category when showing all and not searching
              categories.map((category) => {
                const categoryKinks = filteredKinks.filter(
                  (kink) => kink.categoryId === category.id
                );

                if (categoryKinks.length === 0) return null;

                return (
                  <div key={category.id} className="mb-6">
                    <h4 className="text-md font-medium text-blue-400 mb-2">
                      {category.name}
                    </h4>
                    {category.description && (
                      <p className="text-sm text-slate-400 mb-3">{category.description}</p>
                    )}
                    <div className="space-y-2">
                      {categoryKinks.map((kink) => (
                        <KinkRating
                          key={kink.id}
                          id={kink.id}
                          label={kink.name}
                          value={getPreference(kink.id)}
                          onChange={(value) => onPreferenceChange(kink.id, value as KinkPreference["rating"])}
                        />
                      ))}
                    </div>
                  </div>
                );
              })
            ) : (
              // Flat list when searching or filtering by category
              <div className="space-y-2">
                {filteredKinks.map((kink) => (
                  <KinkRating
                    key={kink.id}
                    id={kink.id}
                    label={`${kink.name} ${searchTerm ? `(${categories.find(c => c.id === kink.categoryId)?.name})` : ""}`}
                    value={getPreference(kink.id)}
                    onChange={(value) => onPreferenceChange(kink.id, value as KinkPreference["rating"])}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-8 bg-slate-800 p-4 rounded-md">
        <h4 className="text-sm font-medium text-white mb-2">Rating Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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
      </div>
    </div>
  );
}

// Mock data for demonstration
export const mockKinkCategories: KinkCategory[] = [
  { id: "general", name: "General", description: "General roleplay preferences" },
  { id: "romance", name: "Romance & Relationships", description: "Relationship dynamics and romantic scenarios" },
  { id: "fantasy", name: "Fantasy Elements", description: "Magic, supernatural, and fantasy themes" },
  { id: "power", name: "Power Dynamics", description: "Control, dominance and submission" },
  { id: "kinks", name: "Specific Kinks", description: "Specific roleplay scenarios and kinks" },
];

export const mockKinks: Kink[] = [
  // General
  { id: "long-term", name: "Long-term RP", categoryId: "general", description: "Extended storylines that develop over time" },
  { id: "short-term", name: "Short-term RP", categoryId: "general", description: "Brief, contained scenarios or one-shots" },
  { id: "story-focused", name: "Story-focused", categoryId: "general", description: "Emphasis on plot and character development" },
  { id: "casual", name: "Casual/Slice of Life", categoryId: "general", description: "Everyday scenarios and relaxed pacing" },
  { id: "adventure", name: "Adventure/Action", categoryId: "general", description: "Quests, battles, and high-energy scenarios" },

  // Romance
  { id: "slow-burn", name: "Slow Burn Romance", categoryId: "romance", description: "Gradually developing romantic feelings" },
  { id: "forbidden-love", name: "Forbidden Love", categoryId: "romance", description: "Relationships that face societal opposition" },
  { id: "polyamory", name: "Polyamory", categoryId: "romance", description: "Multiple-partner relationships" },
  { id: "friends-to-lovers", name: "Friends to Lovers", categoryId: "romance", description: "Friendship evolving into romance" },
  { id: "enemies-to-lovers", name: "Enemies to Lovers", categoryId: "romance", description: "Rivals or enemies developing romantic feelings" },

  // Fantasy
  { id: "magic", name: "Magic Users", categoryId: "fantasy", description: "Characters with magical abilities" },
  { id: "mythical-creatures", name: "Mythical Creatures", categoryId: "fantasy", description: "Creatures from mythology and folklore" },
  { id: "supernatural", name: "Supernatural Elements", categoryId: "fantasy", description: "Ghost, vampires, werewolves, and other supernatural beings" },
  { id: "sci-fi", name: "Sci-Fi Technology", categoryId: "fantasy", description: "Futuristic or alien technology" },
  { id: "alt-history", name: "Alternative History", categoryId: "fantasy", description: "Historical settings with fantastical elements" },

  // Power Dynamics
  { id: "dom-sub", name: "Dom/Sub Dynamics", categoryId: "power", description: "Dominance and submission dynamics" },
  { id: "pet-play", name: "Pet Play", categoryId: "power", description: "Role-playing as pets or owners" },
  { id: "master-servant", name: "Master/Servant", categoryId: "power", description: "Authority figure and subordinate dynamics" },
  { id: "teacher-student", name: "Teacher/Student", categoryId: "power", description: "Educational or mentorship dynamics" },
  { id: "capture", name: "Capture/Captivity", categoryId: "power", description: "Scenarios involving capture or imprisonment" },

  // Specific Kinks
  { id: "bondage", name: "Bondage", categoryId: "kinks", description: "Restraint and restriction of movement" },
  { id: "transformation", name: "Transformation", categoryId: "kinks", description: "Physical changes or shapeshifting" },
  { id: "size-difference", name: "Size Difference", categoryId: "kinks", description: "Significant height or size disparities" },
  { id: "monster", name: "Monster/Creature", categoryId: "kinks", description: "Involvement of monstrous or non-humanoid entities" },
  { id: "tentacles", name: "Tentacles", categoryId: "kinks", description: "Scenarios involving tentacled creatures or appendages" },
];
