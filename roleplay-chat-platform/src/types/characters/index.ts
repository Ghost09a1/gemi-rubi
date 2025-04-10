// Character Status Types
export type CharacterStatus = 'available' | 'busy' | 'away' | 'looking' | 'private';

// Character Mood Types
export type CharacterMood = 'neutral' | 'flirty' | 'playful' | 'passionate' | 'dominant' | 'submissive' | 'shy' | 'confident' | 'curious' | 'seductive';

// Character Model
export interface Character {
  id: string;
  userId: string;
  name: string;
  age?: string | null;
  gender: string;
  species: string;
  height?: string | null;
  bodyType?: string | null;
  personality: string;
  background?: string | null;
  appearance?: string | null;
  public: boolean;
  views: number;
  createdAt: string;
  updatedAt: string;
  currentStatus: CharacterStatus;
  currentMood?: CharacterMood | null;
  customStatus?: string | null;
  allowRandomRp: boolean;
  privateDetails?: string | null;
  contentPreferences?: Record<string, any>;
}

// Character Summary (for lists)
export interface CharacterSummary {
  id: string;
  name: string;
  species: string;
  gender: string;
  age?: string | null;
  currentStatus: CharacterStatus;
  image?: string | null; // Primary image URL
  updatedAt: string;
}

// Character Image
export interface CharacterImage {
  id: string;
  characterId: string;
  url: string;
  thumbnailUrl?: string;
  title?: string | null;
  description?: string | null;
  isPrimary: boolean;
  order: number;
  uploadedAt: string;
  width?: number;
  height?: number;
  fileSize?: number;
  fileType?: string;
}

// Character Kink Rating
export type KinkRating = 'fave' | 'yes' | 'maybe' | 'no';

// Character Kink
export interface CharacterKink {
  id: string;
  characterId: string;
  kinkId: string;
  rating: KinkRating;
}

// Kink Category
export interface KinkCategory {
  id: string;
  name: string;
  description?: string;
  order?: number;
}

// Kink
export interface Kink {
  id: string;
  categoryId: string;
  name: string;
  description?: string;
  order?: number;
}

// Custom Kink
export interface CustomKink {
  id: string;
  characterId: string;
  name: string;
  category?: string;
  description?: string;
  rating: KinkRating;
}

// Character Creation Request
export interface CharacterCreateRequest {
  name: string;
  species: string;
  gender: string;
  age?: string;
  height?: string;
  bodyType?: string;
  personality: string;
  background?: string;
  appearance?: string;
  public?: boolean;
  currentStatus?: CharacterStatus;
  currentMood?: CharacterMood;
  customStatus?: string;
  allowRandomRp?: boolean;
  privateDetails?: string;
  contentPreferences?: Record<string, any>;
}

// Character Update Request
export interface CharacterUpdateRequest extends Partial<CharacterCreateRequest> {
  id: string;
}

// Image Upload Request
export interface ImageUploadRequest {
  characterId: string;
  file: File;
  title?: string;
  description?: string;
  isPrimary?: boolean;
}

// Image Update Request
export interface ImageUpdateRequest {
  id: string;
  title?: string;
  description?: string;
  isPrimary?: boolean;
  order?: number;
}

// Reorder Images Request
export interface ReorderImagesRequest {
  characterId: string;
  imageIds: string[]; // New order of image IDs
}

// Character Search Filters
export interface CharacterSearchFilters {
  query?: string;
  species?: string[];
  gender?: string[];
  age?: { min?: number; max?: number };
  status?: CharacterStatus[];
  kinks?: { id: string; rating: KinkRating[] }[];
  sort?: 'newest' | 'updated' | 'popular' | 'name_asc' | 'name_desc';
  page?: number;
  limit?: number;
}

// Character Search Response
export interface CharacterSearchResponse {
  characters: CharacterSummary[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
