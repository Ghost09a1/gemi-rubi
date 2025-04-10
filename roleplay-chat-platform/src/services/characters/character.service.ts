import {
  Character,
  CharacterSummary,
  CharacterCreateRequest,
  CharacterUpdateRequest,
  CharacterImage,
  ImageUploadRequest,
  ImageUpdateRequest,
  ReorderImagesRequest,
  CharacterSearchFilters,
  CharacterSearchResponse,
} from '@/types/characters';

// Mock data
import { mockCharacters } from './mock/characters';
import { mockCharacterImages } from './mock/images';

class CharacterService {
  private static instance: CharacterService;

  private constructor() {}

  public static getInstance(): CharacterService {
    if (!CharacterService.instance) {
      CharacterService.instance = new CharacterService();
    }
    return CharacterService.instance;
  }

  /**
   * Get all characters for the current user
   */
  async getUserCharacters(userId: string): Promise<CharacterSummary[]> {
    // In a real app, this would be an API call
    // For now, we'll use mock data and filter by userId
    const characters = mockCharacters
      .filter(char => char.userId === userId)
      .map(char => this.characterToSummary(char));

    return characters;
  }

  /**
   * Get a character by ID
   */
  async getCharacter(id: string): Promise<Character | null> {
    // In a real app, this would be an API call
    const character = mockCharacters.find(char => char.id === id);

    return character || null;
  }

  /**
   * Create a new character
   */
  async createCharacter(request: CharacterCreateRequest, userId: string): Promise<Character> {
    // In a real app, this would be an API call

    // Create a new character with default values and provided data
    const newCharacter: Character = {
      id: `char_${Date.now()}`,
      userId,
      name: request.name,
      species: request.species,
      gender: request.gender,
      age: request.age || null,
      height: request.height || null,
      bodyType: request.bodyType || null,
      personality: request.personality,
      background: request.background || null,
      appearance: request.appearance || null,
      public: request.public !== undefined ? request.public : true,
      views: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      currentStatus: request.currentStatus || 'available',
      currentMood: request.currentMood || null,
      customStatus: request.customStatus || null,
      allowRandomRp: request.allowRandomRp !== undefined ? request.allowRandomRp : true,
      privateDetails: request.privateDetails || null,
      contentPreferences: request.contentPreferences || {},
    };

    // In a real app, we would save to database
    // For mock, pretend it worked

    return newCharacter;
  }

  /**
   * Update a character
   */
  async updateCharacter(request: CharacterUpdateRequest): Promise<Character> {
    // In a real app, this would be an API call
    const character = mockCharacters.find(char => char.id === request.id);

    if (!character) {
      throw new Error('Character not found');
    }

    // Update the character with the provided values
    const updatedCharacter: Character = {
      ...character,
      name: request.name || character.name,
      species: request.species || character.species,
      gender: request.gender || character.gender,
      age: request.age !== undefined ? request.age : character.age,
      height: request.height !== undefined ? request.height : character.height,
      bodyType: request.bodyType !== undefined ? request.bodyType : character.bodyType,
      personality: request.personality || character.personality,
      background: request.background !== undefined ? request.background : character.background,
      appearance: request.appearance !== undefined ? request.appearance : character.appearance,
      public: request.public !== undefined ? request.public : character.public,
      currentStatus: request.currentStatus || character.currentStatus,
      currentMood: request.currentMood !== undefined ? request.currentMood : character.currentMood,
      customStatus: request.customStatus !== undefined ? request.customStatus : character.customStatus,
      allowRandomRp: request.allowRandomRp !== undefined ? request.allowRandomRp : character.allowRandomRp,
      privateDetails: request.privateDetails !== undefined ? request.privateDetails : character.privateDetails,
      contentPreferences: request.contentPreferences || character.contentPreferences,
      updatedAt: new Date().toISOString(),
    };

    // In a real app, we would save to database
    // For mock, pretend it worked

    return updatedCharacter;
  }

  /**
   * Delete a character
   */
  async deleteCharacter(id: string): Promise<void> {
    // In a real app, this would be an API call
    const character = mockCharacters.find(char => char.id === id);

    if (!character) {
      throw new Error('Character not found');
    }

    // In a real app, we would delete from database
    // For mock, pretend it worked
  }

  /**
   * Get all images for a character
   */
  async getCharacterImages(characterId: string): Promise<CharacterImage[]> {
    // In a real app, this would be an API call
    const images = mockCharacterImages
      .filter(img => img.characterId === characterId)
      .sort((a, b) => {
        // Primary images first, then by order
        if (a.isPrimary && !b.isPrimary) return -1;
        if (!a.isPrimary && b.isPrimary) return 1;
        return a.order - b.order;
      });

    return images;
  }

  /**
   * Get an image by ID
   */
  async getCharacterImage(id: string): Promise<CharacterImage | null> {
    // In a real app, this would be an API call
    const image = mockCharacterImages.find(img => img.id === id);

    return image || null;
  }

  /**
   * Upload a new image for a character
   */
  async uploadCharacterImage(request: ImageUploadRequest): Promise<CharacterImage> {
    // In a real app, this would upload to a storage service
    // For mock, we'll just pretend it worked

    // Get highest order value for this character's images
    const existingImages = mockCharacterImages.filter(img => img.characterId === request.characterId);
    const highestOrder = existingImages.length > 0
      ? Math.max(...existingImages.map(img => img.order))
      : -1;

    // Create new image object
    const newImage: CharacterImage = {
      id: `img_${Date.now()}`,
      characterId: request.characterId,
      url: URL.createObjectURL(request.file), // This is not how it would work in prod, just for mock
      thumbnailUrl: URL.createObjectURL(request.file), // Same - would normally generate a thumbnail
      title: request.title || null,
      description: request.description || null,
      isPrimary: request.isPrimary !== undefined ? request.isPrimary : existingImages.length === 0, // Make first image primary by default
      order: highestOrder + 1,
      uploadedAt: new Date().toISOString(),
      fileType: request.file.type,
      fileSize: request.file.size,
    };

    // If this is set as primary, make all other images non-primary
    if (newImage.isPrimary) {
      // In real app, we'd update all other images to isPrimary = false
    }

    // In a real app, we would save to database
    // For mock, pretend it worked

    return newImage;
  }

  /**
   * Update an image
   */
  async updateCharacterImage(request: ImageUpdateRequest): Promise<CharacterImage> {
    // In a real app, this would be an API call
    const image = mockCharacterImages.find(img => img.id === request.id);

    if (!image) {
      throw new Error('Image not found');
    }

    // Update the image with the provided values
    const updatedImage: CharacterImage = {
      ...image,
      title: request.title !== undefined ? request.title : image.title,
      description: request.description !== undefined ? request.description : image.description,
      isPrimary: request.isPrimary !== undefined ? request.isPrimary : image.isPrimary,
      order: request.order !== undefined ? request.order : image.order,
    };

    // If this is set as primary, make all other images for this character non-primary
    if (updatedImage.isPrimary && !image.isPrimary) {
      // In real app, we'd update all other images to isPrimary = false
    }

    // In a real app, we would save to database
    // For mock, pretend it worked

    return updatedImage;
  }

  /**
   * Delete an image
   */
  async deleteCharacterImage(id: string): Promise<void> {
    // In a real app, this would be an API call
    const image = mockCharacterImages.find(img => img.id === id);

    if (!image) {
      throw new Error('Image not found');
    }

    // In a real app, we would delete from storage and database
    // For mock, pretend it worked
  }

  /**
   * Reorder images for a character
   */
  async reorderCharacterImages(request: ReorderImagesRequest): Promise<CharacterImage[]> {
    // In a real app, this would be an API call
    const images = mockCharacterImages.filter(img => img.characterId === request.characterId);

    if (images.length !== request.imageIds.length) {
      throw new Error('Invalid image IDs provided for reordering');
    }

    // In a real app, we would update all images with new order values
    // For mock, pretend it worked

    // Sort images based on the provided order
    const sortedImages = [...images].sort((a, b) => {
      const aIndex = request.imageIds.indexOf(a.id);
      const bIndex = request.imageIds.indexOf(b.id);
      return aIndex - bIndex;
    });

    return sortedImages;
  }

  /**
   * Search for characters
   */
  async searchCharacters(filters: CharacterSearchFilters): Promise<CharacterSearchResponse> {
    // In a real app, this would be an API call with filtering

    // For mock, we'll do simple filtering on the name and species
    let filtered = [...mockCharacters];

    if (filters.query) {
      const query = filters.query.toLowerCase();
      filtered = filtered.filter(char =>
        char.name.toLowerCase().includes(query) ||
        char.species.toLowerCase().includes(query)
      );
    }

    if (filters.species && filters.species.length > 0) {
      filtered = filtered.filter(char =>
        filters.species!.some(species => char.species.toLowerCase() === species.toLowerCase())
      );
    }

    if (filters.gender && filters.gender.length > 0) {
      filtered = filtered.filter(char =>
        filters.gender!.some(gender => char.gender.toLowerCase() === gender.toLowerCase())
      );
    }

    if (filters.status && filters.status.length > 0) {
      filtered = filtered.filter(char =>
        filters.status!.includes(char.currentStatus)
      );
    }

    // Sort results
    if (filters.sort) {
      switch(filters.sort) {
        case 'newest':
          filtered.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
          break;
        case 'updated':
          filtered.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
          break;
        case 'popular':
          filtered.sort((a, b) => b.views - a.views);
          break;
        case 'name_asc':
          filtered.sort((a, b) => a.name.localeCompare(b.name));
          break;
        case 'name_desc':
          filtered.sort((a, b) => b.name.localeCompare(a.name));
          break;
      }
    }

    // Paginate results
    const page = filters.page || 1;
    const limit = filters.limit || 20;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedResults = filtered.slice(startIndex, endIndex);

    return {
      characters: paginatedResults.map(char => this.characterToSummary(char)),
      total: filtered.length,
      page,
      limit,
      totalPages: Math.ceil(filtered.length / limit),
    };
  }

  /**
   * Convert a Character to a CharacterSummary
   */
  private characterToSummary(character: Character): CharacterSummary {
    // Find the primary image for this character
    const primaryImage = mockCharacterImages.find(
      img => img.characterId === character.id && img.isPrimary
    );

    return {
      id: character.id,
      name: character.name,
      species: character.species,
      gender: character.gender,
      age: character.age,
      currentStatus: character.currentStatus,
      image: primaryImage?.url || null,
      updatedAt: character.updatedAt,
    };
  }
}

// Export a singleton instance
export const characterService = CharacterService.getInstance();
