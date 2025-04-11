'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CharacterContentPreferences } from '@/types/content-preferences';
import { Character, CharacterSummary, CharacterImage, CharacterCreateRequest, CharacterUpdateRequest, ImageUploadRequest } from '@/types/characters';
import { characterService } from '@/services/characters/character.service';
import { useAuth } from './AuthContext';

// Context type definition
type CharacterContextType = {
  userCharacters: CharacterSummary[];
  currentCharacter: Character | null;
  characterKinks: CharacterContentPreferences | null;
  characterImages: CharacterImage[];
  isLoading: boolean;
  error: string | null;

  // Character actions
  loadUserCharacters: () => Promise<void>;
  getCharacter: (id: string) => Promise<Character | null>;
  createCharacter: (data: CharacterCreateRequest) => Promise<Character | null>;
  updateCharacter: (data: CharacterUpdateRequest) => Promise<Character | null>;
  deleteCharacter: (id: string) => Promise<boolean>;

  // Image actions
  loadCharacterImages: (characterId: string) => Promise<CharacterImage[]>;
  uploadImage: (request: ImageUploadRequest) => Promise<CharacterImage | null>;
  deleteImage: (imageId: string) => Promise<boolean>;
  setImageAsPrimary: (imageId: string) => Promise<boolean>;
  reorderImages: (characterId: string, imageIds: string[]) => Promise<CharacterImage[]>;

  // Kink actions
  loadCharacterKinks: (characterId: string) => Promise<void>;
  updateCharacterKinks: (characterId: string, kinks: CharacterContentPreferences) => Promise<void>;
  addCustomKink: (characterId: string, kinkData: any) => Promise<void>;
  updateCustomKink: (characterId: string, kinkId: string, kinkData: any) => Promise<void>;
  deleteCustomKink: (characterId: string, kinkId: string) => Promise<void>;

  // Selection actions
  setCurrentCharacter: (character: Character | null) => void;
  clearError: () => void;
};

// Create the context with default values
const CharacterContext = createContext<CharacterContextType>({
  userCharacters: [],
  currentCharacter: null,
  characterKinks: null,
  characterImages: [],
  isLoading: false,
  error: null,

  loadUserCharacters: async () => {},
  getCharacter: async () => null,
  createCharacter: async () => null,
  updateCharacter: async () => null,
  deleteCharacter: async () => false,

  loadCharacterImages: async () => [],
  uploadImage: async () => null,
  deleteImage: async () => false,
  setImageAsPrimary: async () => false,
  reorderImages: async () => [],

  loadCharacterKinks: async () => { },
  updateCharacterKinks: async () => { },
  addCustomKink: async () => { },
  updateCustomKink: async () => { },
  deleteCustomKink: async () => { },

  setCurrentCharacter: () => {},
  clearError: () => {},
});

// Provider component
export const CharacterProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [userCharacters, setUserCharacters] = useState<CharacterSummary[]>([]);
  const [characterKinks, setCharacterKinks] = useState<CharacterContentPreferences | null>(null);
  const [currentCharacter, setCurrentCharacter] = useState<Character | null>(null);
  const [characterImages, setCharacterImages] = useState<CharacterImage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const router = useRouter();

  // Load the user's characters on mount if authenticated
  useEffect(() => {
    if (user) {
      loadUserCharacters();
    }
  }, [user]);

  // Load user characters
  const loadUserCharacters = async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      const characters = await characterService.getUserCharacters(user.id);
      setUserCharacters(characters);
    } catch (err: any) {
      setError(err.message || 'Failed to load your characters. There might be a problem with the server or your internet connection.');
      console.error('Error loading characters:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Get a single character
  const getCharacter = async (id: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const character = await characterService.getCharacter(id);
      if (character) {
        setCurrentCharacter(character);
        if (character.contentPreferences) {
          setCharacterKinks(character.contentPreferences);
        }

        return character;
      }
      return null;
    } catch (err: any) {
      setError(err.message || 'Failed to load the character. Please check the character ID or try again later.');
      console.error('Error loading character:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Create a new character
  const createCharacter = async (data: CharacterCreateRequest) => {
    if (!user) {
      setError('You must be logged in to create a character');
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const newCharacter = await characterService.createCharacter(data, user.id);
      setUserCharacters([...userCharacters, characterService.characterToSummary(newCharacter)]);
      setCurrentCharacter(newCharacter);
      return newCharacter;
    } catch (err: any) {
      setError(err.message || 'Failed to create the new character. Please check the entered data and try again.');
      console.error('Error creating character:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Update a character
  const updateCharacter = async (data: CharacterUpdateRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const updatedCharacter = await characterService.updateCharacter(data);

      // Update the current character if it's the one being updated
      if (currentCharacter && currentCharacter.id === updatedCharacter.id) {
        setCurrentCharacter(updatedCharacter);
      }

      // Update the character in the user's character list
      setUserCharacters(userCharacters.map(char =>
        char.id === updatedCharacter.id
          ? characterService.characterToSummary(updatedCharacter)
          : char
      ));

      return updatedCharacter;
    } catch (err: any) {
      setError(err.message || 'Failed to update the character. Please verify the data and try again.');
      console.error('Error updating character:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Delete a character
  const deleteCharacter = async (id: string) => {
    setIsLoading(true);
    setError(null);

    try {
      await characterService.deleteCharacter(id);

      // Remove the character from the user's character list
      setUserCharacters(userCharacters.filter(char => char.id !== id));

      // Clear the current character if it's the one being deleted
      if (currentCharacter && currentCharacter.id === id) {
        setCurrentCharacter(null);
      }

      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to delete the character. The character may no longer exist, or there might be an issue with the server.');
      console.error('Error deleting character:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Load character images
  const loadCharacterImages = async (characterId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const images = await characterService.getCharacterImages(characterId);
      setCharacterImages(images);
      return images;
    } catch (err: any) {
      setError(err.message || 'Failed to load the character images. Please verify the character ID or try again.');
      console.error('Error loading character images:', err);
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  // Upload an image
  const uploadImage = async (request: ImageUploadRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const newImage = await characterService.uploadCharacterImage(request);
      setCharacterImages([...characterImages, newImage]);

      // If this is the primary image, update the character summary
      if (newImage.isPrimary) {
        const updatedUserCharacters = userCharacters.map(char =>
          char.id === request.characterId
            ? { ...char, image: newImage.url }
            : char
        );
        setUserCharacters(updatedUserCharacters);
      }

      return newImage;
    } catch (err: any) {
      setError(err.message || 'Failed to upload the image. Please check the image file and try again.');
      console.error('Error uploading image:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Delete an image
  const deleteImage = async (imageId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Get the image info before deleting
      const imageToDelete = characterImages.find(img => img.id === imageId);
      if (!imageToDelete) {
        throw new Error('Image not found');
      }

      await characterService.deleteCharacterImage(imageId);

      // Remove the image from the character images
      const updatedImages = characterImages.filter(img => img.id !== imageId);
      setCharacterImages(updatedImages);

      // If this was the primary image, update the character summary
      if (imageToDelete.isPrimary) {
        // Find a new primary image or set to null
        const newPrimaryImage = updatedImages.length > 0 ? updatedImages[0] : null;

        if (newPrimaryImage) {
          // Set the new image as primary
          await setImageAsPrimary(newPrimaryImage.id);
        } else {
          // No images left, update character summary with null image
          const updatedUserCharacters = userCharacters.map(char =>
            char.id === imageToDelete.characterId
              ? { ...char, image: null }
              : char
          );
          setUserCharacters(updatedUserCharacters);
        }
      }

      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to delete the image. The image may no longer exist, or there might be an issue with the server.');
      console.error('Error deleting image:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Set an image as primary
  const setImageAsPrimary = async (imageId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const imageToUpdate = characterImages.find(img => img.id === imageId);
      if (!imageToUpdate) {
        throw new Error('Image not found');
      }

      // Update the image
      const updatedImage = await characterService.updateCharacterImage({
        id: imageId,
        isPrimary: true,
      });

      // Update all other images to be non-primary
      const updatedImages = characterImages.map(img =>
        img.id === imageId
          ? updatedImage
          : { ...img, isPrimary: false }
      );

      setCharacterImages(updatedImages);

      // Update the character summary
      const updatedUserCharacters = userCharacters.map(char =>
        char.id === updatedImage.characterId
          ? { ...char, image: updatedImage.url }
          : char
      );
      setUserCharacters(updatedUserCharacters);

      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to set the image as primary. Please try again or check the image list.');
      console.error('Error setting image as primary:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Reorder images
  const reorderImages = async (characterId: string, imageIds: string[]) => {
    setIsLoading(true);
    setError(null);

    try {
      const sortedImages = await characterService.reorderCharacterImages({
        characterId,
        imageIds,
      });

      setCharacterImages(sortedImages);
      return sortedImages;
    } catch (err: any) {
      setError(err.message || 'Failed to reorder the images. Please try again or refresh the page.');
      console.error('Error reordering images:', err);
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  // Load character kinks
  const loadCharacterKinks = async (characterId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // This call doesnt exist in character service, probably should be add in the future
      // const kinks = await characterService.getCharacterKinks(characterId);
      // setCharacterKinks(kinks);
    } catch (err: any) {
      setError(err.message || 'Failed to load the character kinks. Please try again later or check your connection.');
      console.error('Error loading character kinks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Update character kinks
  const updateCharacterKinks = async (characterId: string, kinks: CharacterContentPreferences) => {
    setIsLoading(true);
    setError(null);

    try {
      await characterService.updateCharacterKinks(characterId, kinks);
      setCharacterKinks(kinks);
    } catch (err: any) {
      setError(err.message || 'Failed to update the character kinks. Please verify the data and try again.');
      console.error('Error updating character kinks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Add custom kink
  const addCustomKink = async (characterId: string, kinkData: any) => {
    setIsLoading(true);
    setError(null);

    try {
      await characterService.addCustomKink(characterId, kinkData);
      // Optionally, refresh kinks after adding
      await loadCharacterKinks(characterId);
    } catch (err: any) {
      setError(err.message || 'Failed to add the custom kink. Please verify the data and try again.');
      console.error('Error adding custom kink:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Update custom kink
  const updateCustomKink = async (characterId: string, kinkId: string, kinkData: any) => {
    setIsLoading(true);
    setError(null);

    try {
      await characterService.updateCustomKink(characterId, kinkId, kinkData);
      // Optionally, refresh kinks after updating
      await loadCharacterKinks(characterId);
    } catch (err: any) {
      setError(err.message || 'Failed to update the custom kink. Please verify the data and try again.');
      console.error('Error updating custom kink:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Delete custom kink
  const deleteCustomKink = async (characterId: string, kinkId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await characterService.deleteCustomKink(characterId, kinkId);
    } catch (error: any) {
      setError(error.message || 'Failed to delete the custom kink. The kink may no longer exist, or there might be an issue with the server.');
      console.error('Error deleting custom kink:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear any errors
  const clearError = () => {
    setError(null);
  };

  const contextValue = {
    userCharacters,
    currentCharacter,
    characterKinks,
    characterImages,
    isLoading,
    error,

    loadUserCharacters,
    getCharacter,
    createCharacter,
    updateCharacter,
    deleteCharacter,

    loadCharacterImages,
    uploadImage,
    deleteImage,
    setImageAsPrimary,
    reorderImages,

    loadCharacterKinks,
    updateCharacterKinks,
    addCustomKink,
    updateCustomKink,
    deleteCustomKink,

    setCurrentCharacter,
    clearError,
  };

  return (
    <CharacterContext.Provider value={contextValue}>
      {children}
    </CharacterContext.Provider>
  );
};

// Custom hook to use the character context
export const useCharacters = () => useContext(CharacterContext);
