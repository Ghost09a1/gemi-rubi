import {
  Character,
  CharacterContentPreferences,
  CharacterSummary,
  CharacterCreateRequest,
  CharacterUpdateRequest,
  CharacterImage,
  ImageUploadRequest,
  ImageUpdateRequest,
  ReorderImagesRequest,
  CharacterSearchFilters,
  CharacterSearchResponse,
  CharacterKinks,
  CustomKink,
} from '@/types/characters';

import axios from 'axios';
import { authService } from '../auth.service';

// Mock data
import { mockCharacters } from './mock/characters';
import { mockCharacterImages } from './mock/images';

const API_BASE_URL = '/api';

const getHeaders = () => {
  const token = authService.getAccessToken();
  return {
    headers: {
      Authorization: token ? `Bearer ${token}` : undefined,
    },
  };
};

class CharacterService {
  private static instance: CharacterService;


  private constructor() {}

  public static getInstance(): CharacterService {
    if (!CharacterService.instance) {
      CharacterService.instance = new CharacterService();
    }
    return CharacterService.instance;
  }

  private async handleApiCall<T>(apiCall: Promise<any>): Promise<T> {
    try {
      const response = await apiCall;
      return response.data as T;
    } catch (error: any) {
      const message = error.response?.data?.error || 'An unexpected error occurred';
      return Promise.reject(message);
    }
  }

  /**
   * Get all characters for the current user
   */
  async getUserCharacters(userId: string): Promise<CharacterSummary[]> {

    const apiCall = axios.get<Character[]>(`${API_BASE_URL}/characters/`, getHeaders());

    try {
      const allCharacters = await this.handleApiCall<Character[]>(apiCall)

      return allCharacters.filter(char => char.userId === userId).map(char => this.characterToSummary(char));
    } catch (error: any) {
      const characters = mockCharacters
        .filter(char => char.userId === userId)
        .map(char => this.characterToSummary(char));
  
      // Reject with error message even if returning mock data
      const errorMessage = error?.message || 'Failed to load user characters';

      return Promise.reject(errorMessage);

    }

  }

  /**
   * Get a character by ID
   */
  async getCharacter(id: string): Promise<Character | null> {
    const apiCall = axios.get<Character>(`${API_BASE_URL}/characters/${id}/`, getHeaders());
    return this.handleApiCall<Character | null>(apiCall)
      .catch(()=> mockCharacters.find(char => char.id === id) || null);
  }

  /**
   * Create a new character
   */
  async createCharacter(request: CharacterCreateRequest, userId: string): Promise<Character> {
    // Input validation for character creation
    if (!request.name || typeof request.name !== 'string' || request.name.length < 2 || request.name.length > 50) {
      return Promise.reject('Name must be between 2 and 50 characters.');
    }
    if (!request.species || typeof request.species !== 'string' || request.species.length < 2 || request.species.length > 50) {
      return Promise.reject('Species must be between 2 and 50 characters.');
    }
    if (!request.gender || typeof request.gender !== 'string' || !['male', 'female', 'other'].includes(request.gender)) {
      return Promise.reject('Gender must be one of: male, female, other.');
    }
    if (!request.personality || typeof request.personality !== 'string' || request.personality.length < 10 || request.personality.length > 200) {
      return Promise.reject('Personality must be between 10 and 200 characters.');
    }


    







    // In a real app, this would be an API call
    const apiCall = axios.post<Character>(`${API_BASE_URL}/characters/create/`, request, getHeaders());
    
    try {
      return await this.handleApiCall<Character>(apiCall);
    } catch (error) {
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
        // Reject with error message even if returning mock data
        const errorMessage = error?.message || 'Failed to create character';
        return Promise.reject(errorMessage);
    }
  }

  /**
   * Update a character
   */
  async updateCharacter(request: CharacterUpdateRequest): Promise<Character> {
    // Input validation for character update
    if (!request.id || typeof request.id !== 'string') {
      return Promise.reject('Character ID is required.');
    }
    if (request.name && (typeof request.name !== 'string' || request.name.length < 2 || request.name.length > 50)) {
      return Promise.reject('Name must be between 2 and 50 characters.');
    }
    if (request.species && (typeof request.species !== 'string' || request.species.length < 2 || request.species.length > 50)) {
      return Promise.reject('Species must be between 2 and 50 characters.');
    }
    if (request.gender && (typeof request.gender !== 'string' || !['male', 'female', 'other'].includes(request.gender))) {
      return Promise.reject('Gender must be one of: male, female, other.');
    }
    if (request.personality && (typeof request.personality !== 'string' || request.personality.length < 10 || request.personality.length > 200)) {
      return Promise.reject('Personality must be between 10 and 200 characters.');
    }


    // In a real app, this would be an API call
    const apiCall = axios.put<Character>(`${API_BASE_URL}/characters/${request.id}/update/`, request, getHeaders());
    try{
      return await this.handleApiCall<Character>(apiCall);
    } catch(error) {
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
        
        const errorMessage = error?.message || 'Failed to update character';
        return Promise.reject(errorMessage);

    }

    // In a real app, we would save to database
    // For mock, pretend it worked

    return updatedCharacter;
  }

  /**
   * Delete a character
   */
  async deleteCharacter(id: string): Promise<void> {    
    try {
      const apiCall = axios.delete(`${API_BASE_URL}/characters/${id}/delete/`, getHeaders());
      await this.handleApiCall(apiCall);
      
    } catch(error) {
      const character = mockCharacters.find(char => char.id === id);

        const errorMessage = error?.message || 'Failed to delete character';

        if (!character) {throw new Error(errorMessage)}
        return Promise.reject(errorMessage);
    }

   
    // In a real app, we would delete from database
    // For mock, pretend it worked
  }

  /**
   * Get all images for a character
   */
  async getCharacterImages(characterId: string): Promise<CharacterImage[]> {    
    const apiCall = axios.get<CharacterImage[]>(`${API_BASE_URL}/characters/${characterId}/images/`, getHeaders());
    try{
        return await this.handleApiCall<CharacterImage[]>(apiCall);
    } catch (error) {
      const images = mockCharacterImages
        .filter(img => img.characterId === characterId)
        .sort((a, b) => {
          // Primary images first, then by order
          if (a.isPrimary && !b.isPrimary) return -1;
          if (!a.isPrimary && b.isPrimary) return 1;
          return a.order - b.order;
        });
  
        const errorMessage = error?.message || 'Failed to load character images';

        return Promise.reject(errorMessage);
    }

    const images = []
    return images;
  }

  /**
   * Get an image by ID
   */
  async getCharacterImage(id: string, characterId: string): Promise<CharacterImage | null> {
    const images = await this.getCharacterImages(characterId);
    const image = images.find(img => img.id === id) || null;
    return image;
  }

  /**
   * Upload a new image for a character
   */
  async uploadCharacterImage(request: ImageUploadRequest): Promise<CharacterImage> {
    // In a real app, this would upload to a storage service
    try{
      const formData = new FormData();
      formData.append('file', request.file);
      formData.append('title', request.title || '');
      formData.append('description', request.description || '');
      formData.append('isPrimary', request.isPrimary ? 'true' : 'false');
      const apiCall = axios.post<CharacterImage>(`${API_BASE_URL}/characters/${request.characterId}/images/add/`, formData, getHeaders());
      return await this.handleApiCall<CharacterImage>(apiCall);
    } catch (error) {
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

        const errorMessage = error?.message || 'Failed to upload image';
        return Promise.reject(errorMessage);

  }

  /**
   * Update an image
   */
  async updateCharacterImage(request: ImageUpdateRequest): Promise<CharacterImage> {
    try{
      const apiCall = axios.put<CharacterImage>(`${API_BASE_URL}/characters/${request.characterId}/images/${request.id}/update/`, request, getHeaders());
      return await this.handleApiCall<CharacterImage>(apiCall);
    } catch (error) {
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
        const errorMessage = error?.message || 'Failed to update image';

        return Promise.reject(errorMessage);
    }

    
  
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
    try{
      //this call has to use getCharacterImages because we need to have the characterId to build the api path
      const allImages = await this.getCharacterImages(id)
      const imageToDelete = allImages.find(img => img.id === id);

      const apiCall = axios.delete(`${API_BASE_URL}/characters/${imageToDelete?.characterId}/images/${id}/delete/`, getHeaders());
      await this.handleApiCall(apiCall)
    } catch (error) {
        const image = mockCharacterImages.find(img => img.id === id);

        const errorMessage = error?.message || 'Failed to delete image';

        if (!image) {throw new Error(errorMessage);}
    }
    // In a real app, we would delete from storage and database
    // For mock, pretend it worked
  }

  /**
   * Reorder images for a character
   */
  async reorderCharacterImages(request: ReorderImagesRequest): Promise<CharacterImage[]> {    
    try{
      const apiCall = axios.post<CharacterImage[]>(`${API_BASE_URL}/characters/${request.characterId}/images/reorder/`, request, getHeaders());
      return await this.handleApiCall<CharacterImage[]>(apiCall);
    } catch (error) {
      const images = mockCharacterImages.filter(img => img.characterId === request.characterId);

      if (images.length !== request.imageIds.length) {
          const errorMessage = error?.message || 'Invalid image IDs provided for reordering';
        throw new Error(errorMessage);
      }
      // Sort images based on the provided order
    const sortedImages = [...images].sort((a, b) => {
      const aIndex = request.imageIds.indexOf(a.id);
      const bIndex = request.imageIds.indexOf(b.id);
      return aIndex - bIndex;
    });
        const errorMessage = error?.message || 'Failed to reorder images';

        return Promise.reject(errorMessage);
    return sortedImages;
    }
  }

  /**
   * Update the kinks of a character
   */
  async updateCharacterKinks(characterId: string, kinks: CharacterKinks): Promise<CharacterKinks> {
    try{
        const apiCall = axios.put<CharacterKinks>(`${API_BASE_URL}/characters/${characterId}/kinks/`, kinks, getHeaders());
        return await this.handleApiCall<CharacterKinks>(apiCall);
    } catch(error) {
      // in a real app, the characterKinks would be persisted in the mock data
      const errorMessage = error?.message || 'Failed to update character kinks';

      return Promise.reject(errorMessage);
    }
  }

  /**
   * Add a custom kink to a character
   */
  async addCustomKink(characterId: string, kinkData: CustomKink): Promise<CustomKink> {
    try{
        const apiCall = axios.post<CustomKink>(`${API_BASE_URL}/characters/${characterId}/kinks/custom/`, kinkData, getHeaders());
        return await this.handleApiCall<CustomKink>(apiCall);
    } catch(error) {
        // Simulate adding a new custom kink
        const newKink: CustomKink = {
            id: `custom_kink_${Date.now()}`,
            characterId: characterId,
            name: kinkData.name,
            description: kinkData.description || null,
            // In a real app, more properties might be required
        };
        const errorMessage = error?.message || 'Failed to add custom kink';

      return Promise.reject(errorMessage);
    }
  }

  /**
   * Update a custom kink
   */
  async updateCustomKink(characterId: string, kinkId: string, kinkData: CustomKink): Promise<CustomKink> {
    try{
        const apiCall = axios.put<CustomKink>(`${API_BASE_URL}/characters/${characterId}/kinks/custom/${kinkId}/update/`, kinkData, getHeaders());
        return await this.handleApiCall<CustomKink>(apiCall);
    } catch(error) {
      // In a real app, this would fetch from the database
      // For mock, we just update the data
      const updatedKink: CustomKink = {
        id: kinkId,
        characterId,
        name: kinkData.name,
        description: kinkData.description,
      };
        const errorMessage = error?.message || 'Failed to update custom kink';

        return Promise.reject(errorMessage);
    }
  }

  /**
   * Delete a custom kink
   */
  async deleteCustomKink(characterId: string, kinkId: string): Promise<void> {
    try {
      const apiCall = axios.delete(`${API_BASE_URL}/characters/${characterId}/kinks/custom/${kinkId}/delete/`, getHeaders());
      await this.handleApiCall(apiCall);
    } catch (error) {
      // Simulate the deletion for mock data
      // In a real app, this would need to find the data and delete it

      // For mock data, we could use an array to store customKinks, but it is not implemented
      // As the method return void, it is okay to just return and mock that it worked
      const errorMessage = error?.message || 'Failed to delete custom kink';

        return Promise.reject(errorMessage);
      return;
    }
  }

  async getAllKinks(characterId: string): Promise<CharacterKinks> {
    try {
        const apiCall = axios.get<CharacterKinks>(`${API_BASE_URL}/characters/${characterId}/kinks/`, getHeaders());
        return await this.handleApiCall<CharacterKinks>(apiCall);
    } catch (error) {
        // Return a default value when there is an error
        return {

            characterId, 

            dom: false,
            sub: false,
            switch: false,
            brat: false,
            pet: false,
            cnc: false,
            dubcon: false,
            noncon: false,
            humiliation: false,
            degradation: false,
            exhibitionism: false,
            voyeurism: false,
            public: false,
            pain: false,
            gore: false,
            vore: false,
            scat: false,
            watersports: false
        };
        const errorMessage = error?.message || 'Failed to get all kinks';
        return Promise.reject(errorMessage);
    }
}

  /**
   * Search for characters
   */
  async searchCharacters(filters: CharacterSearchFilters): Promise<CharacterSearchResponse> {
    try {
      const params: any = {};

      if (filters.query) {
        params.search = filters.query; // Assuming backend uses 'search' for general term
      }
      if (filters.species && filters.species.length > 0) {
        params.species = filters.species.join(','); // Assuming comma-separated values
      }
      if (filters.gender && filters.gender.length > 0) {
        params.gender = filters.gender.join(',');
      }
      if (filters.status && filters.status.length > 0) {
        params.currentStatus = filters.status.join(','); // Adjust if backend field is different
      }

      // Add other filters as needed, mapping to backend field names
      // Example for age range (assuming min_age and max_age in backend):
      if (filters.age_min) {
        params.age_min = filters.age_min;
      }
      if (filters.age_max) {
        params.age_max = filters.age_max;
      }
      //Kinks
       if (filters.kinks && filters.kinks.length > 0) {
        params.kinks = filters.kinks.join(','); // Assuming comma-separated values
      }


      // Pagination
      params.page = filters.page || 1;
      params.page_size = filters.limit || 20; // Assuming 'page_size' for limit

      // Sorting
      if (filters.sort) {
        switch (filters.sort) {
          case 'newest':
            params.order_by = '-createdAt'; // Assuming '-createdAt' for newest first
            break;
          case 'updated':
            params.order_by = '-updatedAt';
            break;
          case 'popular':
            params.order_by = '-views';
            break;
          case 'name_asc':
            params.order_by = 'name';
            break;
          case 'name_desc':
            params.order_by = '-name';
            break;
          // Add other sorting options as needed
        }
      }

      const apiCall = axios.get<CharacterSearchResponse>(`${API_BASE_URL}/characters/`, {
        ...getHeaders(),
        params,
      });
      return await this.handleApiCall<CharacterSearchResponse>(apiCall);
    } catch (error: any) {
      const message = error.response?.data?.error || 'An unexpected error occurred during search';
      return Promise.reject(message);
    }
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
