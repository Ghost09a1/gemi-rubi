"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    confirmEmail: "",
    password: "",
    confirmPassword: "",
    timezone: "0", // GMT by default
    termsAccepted: false,
    age18Plus: false,
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [passwordStrength, setPasswordStrength] = useState(0);
  const { register, error, isLoading, isAuthenticated, clearError } = useAuth();
  const router = useRouter();

  // If already authenticated, redirect to characters page
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/characters");
    }

    // Clear any auth errors when component mounts
    clearError();
  }, [isAuthenticated, router, clearError]);

  const updatePasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (password.match(/[A-Z]/)) strength += 1;
    if (password.match(/[a-z]/)) strength += 1;
    if (password.match(/[0-9]/)) strength += 1;
    if (password.match(/[^A-Za-z0-9]/)) strength += 1;
    setPasswordStrength(strength);
  };

  const getStrengthLabel = () => {
    if (passwordStrength <= 1) return "Weak";
    if (passwordStrength <= 3) return "Moderate";
    return "Strong";
  };

  const getStrengthColor = () => {
    if (passwordStrength <= 1) return "bg-red-500";
    if (passwordStrength <= 3) return "bg-yellow-500";
    return "bg-green-500";
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = type === "checkbox" ? (e.target as HTMLInputElement).checked : undefined;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });

    // Update password strength if password field changes
    if (name === "password") {
      updatePasswordStrength(value);
    }

    // Clear error for this field when user starts typing
    if (formErrors[name]) {
      const newErrors = { ...formErrors };
      delete newErrors[name];
      setFormErrors(newErrors);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.username) newErrors.username = "Username is required";
    if (formData.username.length < 3) newErrors.username = "Username must be at least 3 characters";

    if (!formData.email) newErrors.email = "Email is required";
    if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Email is invalid";

    if (formData.email !== formData.confirmEmail) newErrors.confirmEmail = "Emails do not match";

    if (!formData.password) newErrors.password = "Password is required";
    if (formData.password.length < 8) newErrors.password = "Password must be at least 8 characters";

    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "Passwords do not match";

    if (!formData.termsAccepted) newErrors.termsAccepted = "You must accept the Terms of Service";

    if (!formData.age18Plus) newErrors.age18Plus = "You must confirm you are 18+ to register";

    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        timezone_offset: formData.timezone,
      });
    } catch (err) {
      // Error is handled in the auth context
      console.error("Registration error:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Navigation Bar */}
      <header className="bg-slate-800 shadow-md p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Link href="/" className="flex items-center">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">RoleplayHub</h1>
          </Link>
          <nav className="flex space-x-4">
            <Link href="/login" className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-md transition">
              Login
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto py-8 px-4">
        <div className="max-w-4xl mx-auto bg-slate-800 rounded-lg shadow-lg overflow-hidden">
          <div className="md:flex">
            <div className="md:w-2/3 p-8">
              <h1 className="text-3xl font-bold mb-6">Create Account</h1>
              <p className="mb-6 text-slate-300">
                Join the premier platform for character-based roleplay. Create detailed characters,
                find partners with compatible preferences, and engage in immersive roleplay.
              </p>

              {error && (
                <div className="bg-red-600/30 border border-red-600 text-white px-4 py-3 rounded-md mb-6">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Username <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Choose a unique username"
                  />
                  {formErrors.username && (
                    <p className="mt-1 text-sm text-red-400">{formErrors.username}</p>
                  )}
                </div>

                <div className="space-y-4">
                  <p className="text-sm text-slate-300">
                    Registration requires a valid email address. You will need to verify your email to complete registration.
                  </p>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Email <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="your.email@example.com"
                    />
                    {formErrors.email && (
                      <p className="mt-1 text-sm text-red-400">{formErrors.email}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Confirm Email <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="email"
                      name="confirmEmail"
                      value={formData.confirmEmail}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Re-enter your email"
                    />
                    {formErrors.confirmEmail && (
                      <p className="mt-1 text-sm text-red-400">{formErrors.confirmEmail}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <p className="text-sm text-slate-300">
                    Choose a strong password for your account security.
                  </p>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Password <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Strong password (min. 8 characters)"
                    />
                    <div className="mt-2">
                      <div className="w-full h-2 bg-slate-600 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${getStrengthColor()}`}
                          style={{ width: `${(passwordStrength / 5) * 100}%` }}
                        ></div>
                      </div>
                      <p className="text-xs mt-1 text-slate-300">
                        Strength: <span className={passwordStrength > 3 ? "text-green-400" : passwordStrength > 1 ? "text-yellow-400" : "text-red-400"}>
                          {getStrengthLabel()}
                        </span>
                      </p>
                    </div>
                    {formErrors.password && (
                      <p className="mt-1 text-sm text-red-400">{formErrors.password}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Confirm Password <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Re-enter your password"
                    />
                    {formErrors.confirmPassword && (
                      <p className="mt-1 text-sm text-red-400">{formErrors.confirmPassword}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Your Timezone
                  </label>
                  <select
                    name="timezone"
                    value={formData.timezone}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="-12">GMT -12</option>
                    <option value="-11">GMT -11</option>
                    <option value="-10">GMT -10</option>
                    <option value="-9">GMT -9</option>
                    <option value="-8">GMT -8</option>
                    <option value="-7">GMT -7</option>
                    <option value="-6">GMT -6</option>
                    <option value="-5">GMT -5</option>
                    <option value="-4">GMT -4</option>
                    <option value="-3">GMT -3</option>
                    <option value="-2">GMT -2</option>
                    <option value="-1">GMT -1</option>
                    <option value="0">GMT</option>
                    <option value="1">GMT +1</option>
                    <option value="2">GMT +2</option>
                    <option value="3">GMT +3</option>
                    <option value="4">GMT +4</option>
                    <option value="5">GMT +5</option>
                    <option value="6">GMT +6</option>
                    <option value="7">GMT +7</option>
                    <option value="8">GMT +8</option>
                    <option value="9">GMT +9</option>
                    <option value="10">GMT +10</option>
                    <option value="11">GMT +11</option>
                    <option value="12">GMT +12</option>
                  </select>
                </div>

                <div className="space-y-3">
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        type="checkbox"
                        name="termsAccepted"
                        checked={formData.termsAccepted}
                        onChange={handleInputChange}
                        className="h-4 w-4 text-blue-500 border-slate-600 rounded focus:ring-blue-500"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label className="text-slate-300">
                        I agree to the <Link href="/terms" className="text-blue-400 hover:underline">Terms of Service</Link> and <Link href="/privacy" className="text-blue-400 hover:underline">Privacy Policy</Link>
                      </label>
                      {formErrors.termsAccepted && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.termsAccepted}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        type="checkbox"
                        name="age18Plus"
                        checked={formData.age18Plus}
                        onChange={handleInputChange}
                        className="h-4 w-4 text-blue-500 border-slate-600 rounded focus:ring-blue-500"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label className="text-slate-300">
                        I confirm I am 18 years of age or older
                      </label>
                      {formErrors.age18Plus && (
                        <p className="mt-1 text-sm text-red-400">{formErrors.age18Plus}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-700 hover:to-teal-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors ${
                      isLoading ? "opacity-70 cursor-not-allowed" : ""
                    }`}
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Creating Account...
                      </span>
                    ) : (
                      "Create Account"
                    )}
                  </button>
                </div>

                <div className="text-center mt-4">
                  <p className="text-slate-300">
                    Already have an account? <Link href="/login" className="text-blue-400 hover:underline">Login here</Link>
                  </p>
                </div>
              </form>
            </div>

            <div className="hidden md:block md:w-1/3 bg-gradient-to-br from-blue-900 to-slate-900 p-8 flex items-center justify-center">
              <div className="text-center">
                <img
                  src="https://ext.same-assets.com/2421641290/1360199898.png"
                  alt="Character Illustration"
                  className="mx-auto w-64 mb-6"
                />
                <h3 className="text-xl font-semibold mb-2">Join Our Community</h3>
                <p className="text-slate-300">
                  Create your account to access thousands of characters and connect with roleplayers from around the world.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer className="bg-slate-800 py-6 mt-10">
        <div className="container mx-auto px-4">
          <div className="text-center text-slate-400">
            <p>© 2024 RoleplayHub. All rights reserved. 18+ ONLY.</p>
            <p className="mt-2 text-sm">
              <Link href="/terms" className="hover:text-white mr-4">Terms of Service</Link>
              <Link href="/privacy" className="hover:text-white mr-4">Privacy Policy</Link>
              <Link href="/guidelines" className="hover:text-white">Community Guidelines</Link>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
