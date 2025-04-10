'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Character, CharacterSummary, CharacterImage, CharacterCreateRequest, CharacterUpdateRequest, ImageUploadRequest } from '@/types/characters';
import { characterService } from '@/services/characters/character.service';
import { useAuth } from './AuthContext';

// Context type definition
type CharacterContextType = {
  userCharacters: CharacterSummary[];
  currentCharacter: Character | null;
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

  // Selection actions
  setCurrentCharacter: (character: Character | null) => void;
  clearError: () => void;
};

// Create the context with default values
const CharacterContext = createContext<CharacterContextType>({
  userCharacters: [],
  currentCharacter: null,
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

  setCurrentCharacter: () => {},
  clearError: () => {},
});

// Provider component
export const CharacterProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [userCharacters, setUserCharacters] = useState<CharacterSummary[]>([]);
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
      setError(err.message || 'Failed to load characters');
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
        return character;
      }
      return null;
    } catch (err: any) {
      setError(err.message || 'Failed to load character');
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
      setError(err.message || 'Failed to create character');
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
      setError(err.message || 'Failed to update character');
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
      setError(err.message || 'Failed to delete character');
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
      setError(err.message || 'Failed to load character images');
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
      setError(err.message || 'Failed to upload image');
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
      setError(err.message || 'Failed to delete image');
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
      setError(err.message || 'Failed to set image as primary');
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
      setError(err.message || 'Failed to reorder images');
      console.error('Error reordering images:', err);
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  // Clear any errors
  const clearError = () => {
    setError(null);
  };

  return (
    <CharacterContext.Provider
      value={{
        userCharacters,
        currentCharacter,
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

        setCurrentCharacter,
        clearError,
      }}
    >
      {children}
    </CharacterContext.Provider>
  );
};

// Custom hook to use the character context
export const useCharacters = () => useContext(CharacterContext);
