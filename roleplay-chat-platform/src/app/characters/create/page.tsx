"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Layout from "@/components/Layout";
import { FormStepper } from "@/components/characters/CharacterTabs";
import {
  InputField,
  TextAreaField,
  SelectField,
  RadioGroup,
  ImageUpload,
} from "@/components/characters/FormInputs";
import KinkManagement, {
  mockKinkCategories,
  mockKinks
} from "@/components/characters/KinkManagement";

// Mock user for layout
const mockUser = {
  username: "player123",
};

// Character creation steps
const steps = [
  { id: "basics", label: "Basic Info" },
  { id: "appearance", label: "Appearance" },
  { id: "personality", label: "Personality" },
  { id: "images", label: "Images", optional: true },
  { id: "kinks", label: "Kinks & Preferences", optional: true },
  { id: "review", label: "Review" },
];

// Mock gender options
const genderOptions = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
  { value: "non-binary", label: "Non-Binary" },
  { value: "other", label: "Other" },
  { value: "unspecified", label: "Unspecified" },
];

// Mock species options
const speciesOptions = [
  { value: "human", label: "Human" },
  { value: "elf", label: "Elf" },
  { value: "orc", label: "Orc" },
  { value: "dragon", label: "Dragon" },
  { value: "kitsune", label: "Kitsune" },
  { value: "vampire", label: "Vampire" },
  { value: "werewolf", label: "Werewolf" },
  { value: "demon", label: "Demon" },
  { value: "angel", label: "Angel" },
  { value: "other", label: "Other" },
];

export default function CreateCharacterPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState("basics");
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);

  // Form state
  const [formData, setFormData] = useState({
    // Basic Info
    name: "",
    gender: "",
    species: "",
    age: "",
    status: "available",

    // Appearance
    height: "",
    bodyType: "",
    eyeColor: "",
    hairColor: "",
    appearanceDescription: "",

    // Personality
    personality: "",
    background: "",

    // Images
    primaryImage: null as File | null,

    // Kinks & Preferences
    kinkPreferences: [] as { kinkId: string, rating: "fave" | "yes" | "maybe" | "no" | "" }[],

    // Public/Private settings
    isPublic: true,
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [primaryImagePreview, setPrimaryImagePreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState("");

  // Handle image upload
  const handleImageChange = (file: File | null) => {
    setFormData({ ...formData, primaryImage: file });

    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPrimaryImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setPrimaryImagePreview(null);
    }
  };

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    // Clear error when field is edited
    if (formErrors[name]) {
      const newErrors = { ...formErrors };
      delete newErrors[name];
      setFormErrors(newErrors);
    }
  };

  // Handle radio button changes
  const handleRadioChange = (name: string, value: string) => {
    setFormData({ ...formData, [name]: value });

    // Clear error when field is edited
    if (formErrors[name]) {
      const newErrors = { ...formErrors };
      delete newErrors[name];
      setFormErrors(newErrors);
    }
  };

  // Validate current step
  const validateStep = (step: string): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case "basics":
        if (!formData.name.trim()) {
          newErrors.name = "Character name is required";
        }
        if (!formData.species) {
          newErrors.species = "Species is required";
        }
        if (!formData.gender) {
          newErrors.gender = "Gender is required";
        }
        if (formData.age && isNaN(Number(formData.age))) {
          newErrors.age = "Age must be a number";
        }
        break;

      case "appearance":
        // Appearance fields are optional
        break;

      case "personality":
        if (!formData.personality.trim()) {
          newErrors.personality = "Personality description is required";
        }
        break;

      case "images":
        // Images are optional
        break;

      case "kinks":
        // Kinks are optional
        break;
    }

    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle next step
  const handleNextStep = () => {
    if (validateStep(currentStep)) {
      // Add current step to completed steps if not already there
      if (!completedSteps.includes(currentStep)) {
        setCompletedSteps([...completedSteps, currentStep]);
      }

      // Find current step index
      const currentIndex = steps.findIndex((step) => step.id === currentStep);
      if (currentIndex < steps.length - 1) {
        setCurrentStep(steps[currentIndex + 1].id);
      }
    }
  };

  // Handle back step
  const handleBackStep = () => {
    const currentIndex = steps.findIndex((step) => step.id === currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1].id);
    }
  };

  // Handle navigation to specific step (only if it's completed or the current one)
  const handleStepClick = (stepId: string) => {
    const canNavigate = completedSteps.includes(stepId) || stepId === currentStep;
    if (canNavigate) {
      setCurrentStep(stepId);
    }
  };

  // Handle kink preferences
  const handleKinkPreferenceChange = (kinkId: string, rating: "fave" | "yes" | "maybe" | "no" | "") => {
    const existingPrefIndex = formData.kinkPreferences.findIndex(pref => pref.kinkId === kinkId);

    let newPreferences = [...formData.kinkPreferences];

    if (existingPrefIndex >= 0) {
      // Update existing preference
      if (rating === "") {
        // Remove preference if rating is empty
        newPreferences = newPreferences.filter(pref => pref.kinkId !== kinkId);
      } else {
        // Update preference rating
        newPreferences[existingPrefIndex] = { ...newPreferences[existingPrefIndex], rating };
      }
    } else if (rating !== "") {
      // Add new preference if rating is not empty
      newPreferences.push({ kinkId, rating });
    }

    setFormData({ ...formData, kinkPreferences: newPreferences });
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all steps before submission
    let allValid = true;
    for (const step of steps) {
      // Skip optional steps if they're not marked as completed
      if (step.optional && !completedSteps.includes(step.id)) {
        continue;
      }

      if (!validateStep(step.id)) {
        allValid = false;
        setCurrentStep(step.id);
        break;
      }
    }

    if (!allValid) return;

    setIsSubmitting(true);
    setServerError("");

    try {
      // In a real app, we'd send this to the backend
      // const formDataToSend = new FormData();
      // Object.entries(formData).forEach(([key, value]) => {
      //   if (value !== null) {
      //     formDataToSend.append(key, value);
      //   }
      // });

      // const response = await fetch("http://localhost:8000/api/characters/create/", {
      //   method: "POST",
      //   body: formDataToSend,
      //   headers: {
      //     Authorization: `Bearer ${localStorage.getItem("access")}`,
      //   },
      // });

      // if (!response.ok) {
      //   throw new Error("Failed to create character");
      // }

      // Mock success response
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Redirect to character list
      router.push("/characters");
    } catch (err: any) {
      setServerError(err.message || "An error occurred while creating your character");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Layout user={mockUser}>
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Create a New Character</h1>
          <p className="text-slate-400">
            Create a detailed character profile with personality, appearance, and preferences
          </p>
        </div>

        {serverError && (
          <div className="bg-red-500/20 border border-red-500 text-white p-4 rounded-md mb-6">
            {serverError}
          </div>
        )}

        <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 overflow-hidden">
          <div className="p-6">
            <FormStepper
              steps={steps}
              currentStep={currentStep}
              completedSteps={completedSteps}
              onStepClick={handleStepClick}
            />

            <form onSubmit={handleSubmit}>
              {/* Basic Info Step */}
              {currentStep === "basics" && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">Basic Information</h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InputField
                      id="name"
                      label="Character Name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="Enter character name"
                      error={formErrors.name}
                      required
                      maxLength={50}
                    />

                    <InputField
                      id="age"
                      label="Age"
                      type="number"
                      value={formData.age}
                      onChange={handleInputChange}
                      placeholder="Enter age (optional)"
                      error={formErrors.age}
                    />

                    <SelectField
                      id="gender"
                      label="Gender"
                      value={formData.gender}
                      onChange={handleInputChange}
                      options={genderOptions}
                      error={formErrors.gender}
                      required
                    />

                    <SelectField
                      id="species"
                      label="Species"
                      value={formData.species}
                      onChange={handleInputChange}
                      options={speciesOptions}
                      error={formErrors.species}
                      required
                    />
                  </div>

                  <div className="mt-8">
                    <RadioGroup
                      id="status"
                      legend="Initial Status"
                      options={[
                        { value: "available", label: "Available for RP" },
                        { value: "looking", label: "Actively Looking for RP" },
                        { value: "private", label: "Private (Only visible to you)" },
                      ]}
                      value={formData.status}
                      onChange={(value) => handleRadioChange("status", value)}
                    />
                  </div>
                </div>
              )}

              {/* Appearance Step */}
              {currentStep === "appearance" && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">Appearance</h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InputField
                      id="height"
                      label="Height"
                      value={formData.height}
                      onChange={handleInputChange}
                      placeholder="e.g., 5'10\", 178cm"
                      error={formErrors.height}
                    />

                    <InputField
                      id="bodyType"
                      label="Body Type"
                      value={formData.bodyType}
                      onChange={handleInputChange}
                      placeholder="e.g., Athletic, Slim"
                      error={formErrors.bodyType}
                    />

                    <InputField
                      id="eyeColor"
                      label="Eye Color"
                      value={formData.eyeColor}
                      onChange={handleInputChange}
                      placeholder="e.g., Blue, Green"
                      error={formErrors.eyeColor}
                    />

                    <InputField
                      id="hairColor"
                      label="Hair Color"
                      value={formData.hairColor}
                      onChange={handleInputChange}
                      placeholder="e.g., Blonde, Black"
                      error={formErrors.hairColor}
                    />
                  </div>

                  <div className="mt-6">
                    <TextAreaField
                      id="appearanceDescription"
                      label="Detailed Appearance"
                      value={formData.appearanceDescription}
                      onChange={handleInputChange}
                      placeholder="Describe your character's appearance in detail..."
                      error={formErrors.appearanceDescription}
                      rows={6}
                    />
                  </div>
                </div>
              )}

              {/* Personality Step */}
              {currentStep === "personality" && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">Personality & Background</h2>

                  <TextAreaField
                    id="personality"
                    label="Personality"
                    value={formData.personality}
                    onChange={handleInputChange}
                    placeholder="Describe your character's personality traits, behaviors, and temperament..."
                    error={formErrors.personality}
                    required
                    rows={6}
                  />

                  <TextAreaField
                    id="background"
                    label="Background Story"
                    value={formData.background}
                    onChange={handleInputChange}
                    placeholder="Share your character's history, origins, and important life events..."
                    error={formErrors.background}
                    rows={8}
                  />
                </div>
              )}

              {/* Images Step */}
              {currentStep === "images" && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">Character Images</h2>

                  <div className="max-w-xl">
                    <p className="text-slate-300 mb-6">
                      Upload images of your character to enhance your profile. While optional,
                      having at least one image helps others visualize your character better.
                    </p>

                    <ImageUpload
                      id="primaryImage"
                      label="Primary Character Image"
                      onChange={handleImageChange}
                      previewUrl={primaryImagePreview}
                      error={formErrors.primaryImage}
                    />

                    <p className="text-sm text-slate-400 mt-4">
                      * You can add more images to your character after creation from the character edit page.
                    </p>
                  </div>
                </div>
              )}

              {/* Kinks Step */}
              {currentStep === "kinks" && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">Kinks & Preferences</h2>

                  <div className="max-w-4xl">
                    <p className="text-slate-300 mb-6">
                      Set your character's kinks and preferences. This helps other players understand
                      what types of roleplay scenarios you're interested in.
                    </p>

                    <KinkManagement
                      categories={mockKinkCategories}
                      kinks={mockKinks}
                      userPreferences={formData.kinkPreferences}
                      onPreferenceChange={handleKinkPreferenceChange}
                    />
                  </div>
                </div>
              )}

              {/* Review Step */}
              {currentStep === "review" && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">Review Your Character</h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                      <h3 className="text-lg font-medium mb-3 text-blue-400">Basic Information</h3>
                      <div className="bg-slate-700/50 rounded-md p-4 mb-6">
                        <p className="mb-2"><span className="font-medium">Name:</span> {formData.name}</p>
                        <p className="mb-2"><span className="font-medium">Species:</span> {formData.species}</p>
                        <p className="mb-2"><span className="font-medium">Gender:</span> {formData.gender}</p>
                        <p><span className="font-medium">Age:</span> {formData.age || "Not specified"}</p>
                      </div>

                      <h3 className="text-lg font-medium mb-3 text-blue-400">Appearance</h3>
                      <div className="bg-slate-700/50 rounded-md p-4 mb-6">
                        <p className="mb-2"><span className="font-medium">Height:</span> {formData.height || "Not specified"}</p>
                        <p className="mb-2"><span className="font-medium">Body Type:</span> {formData.bodyType || "Not specified"}</p>
                        <p className="mb-2"><span className="font-medium">Eye Color:</span> {formData.eyeColor || "Not specified"}</p>
                        <p className="mb-2"><span className="font-medium">Hair Color:</span> {formData.hairColor || "Not specified"}</p>

                        {formData.appearanceDescription && (
                          <div className="mt-3 border-t border-slate-600 pt-3">
                            <p className="font-medium mb-1">Detailed Appearance:</p>
                            <p className="text-sm text-slate-300">{formData.appearanceDescription}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    <div>
                      {primaryImagePreview && (
                        <div className="mb-6">
                          <h3 className="text-lg font-medium mb-3 text-blue-400">Primary Image</h3>
                          <img
                            src={primaryImagePreview}
                            alt={formData.name}
                            className="w-full max-w-[300px] h-auto rounded-md border border-slate-600"
                          />
                        </div>
                      )}

                      <h3 className="text-lg font-medium mb-3 text-blue-400">Personality</h3>
                      <div className="bg-slate-700/50 rounded-md p-4 mb-6">
                        <p className="text-sm text-slate-300">{formData.personality}</p>
                      </div>

                      {formData.background && (
                        <>
                          <h3 className="text-lg font-medium mb-3 text-blue-400">Background</h3>
                          <div className="bg-slate-700/50 rounded-md p-4 mb-6">
                            <p className="text-sm text-slate-300">{formData.background}</p>
                          </div>
                        </>
                      )}

                      {/* Add Kink Preferences Review */}
                      {formData.kinkPreferences.length > 0 && (
                        <>
                          <h3 className="text-lg font-medium mb-3 text-blue-400">Kink Preferences</h3>
                          <div className="bg-slate-700/50 rounded-md p-4">
                            <ul className="grid grid-cols-1 lg:grid-cols-2 gap-x-4 gap-y-1">
                              {formData.kinkPreferences.map((pref) => {
                                const kink = mockKinks.find(k => k.id === pref.kinkId);
                                if (!kink) return null;

                                const ratingColors = {
                                  fave: "text-green-400",
                                  yes: "text-blue-400",
                                  maybe: "text-yellow-400",
                                  no: "text-red-400",
                                };

                                return (
                                  <li key={pref.kinkId} className="text-sm flex items-center py-1">
                                    <span className={`font-medium ${ratingColors[pref.rating]}`}>
                                      {pref.rating.charAt(0).toUpperCase() + pref.rating.slice(1)}:
                                    </span>
                                    <span className="ml-2 text-slate-300">
                                      {kink.name}
                                    </span>
                                  </li>
                                );
                              })}
                            </ul>
                            {formData.kinkPreferences.length === 0 && (
                              <p className="text-sm text-slate-300">No kink preferences have been set.</p>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="mt-8 flex justify-between">
                <button
                  type="button"
                  onClick={handleBackStep}
                  disabled={currentStep === steps[0].id}
                  className={`px-5 py-2 rounded-md ${
                    currentStep === steps[0].id
                      ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                      : "bg-slate-700 text-white hover:bg-slate-600"
                  }`}
                >
                  Back
                </button>

                {currentStep !== steps[steps.length - 1].id ? (
                  <button
                    type="button"
                    onClick={handleNextStep}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-md"
                  >
                    Continue
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className={`bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-700 hover:to-teal-600 text-white px-6 py-2 rounded-md ${
                      isSubmitting ? "opacity-70 cursor-not-allowed" : ""
                    }`}
                  >
                    {isSubmitting ? (
                      <span className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Creating Character...
                      </span>
                    ) : (
                      "Create Character"
                    )}
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
}
