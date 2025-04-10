"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    rememberMe: false
  });

  const { login, error, isLoading, isAuthenticated, clearError } = useAuth();
  const router = useRouter();

  // If already authenticated, redirect to characters page
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/characters");
    }

    // Clear any auth errors when component mounts
    clearError();
  }, [isAuthenticated, router, clearError]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value
    });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await login({
        username: formData.username,
        password: formData.password,
        rememberMe: formData.rememberMe
      });
    } catch (err) {
      // Error is handled in the auth context
      console.error("Login error:", err);
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
            <Link href="/register" className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-md transition">
              Sign Up
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto py-16 px-4">
        <div className="max-w-md mx-auto bg-slate-800 rounded-lg shadow-lg overflow-hidden">
          <div className="p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
              <p className="text-slate-300">Sign in to your RoleplayHub account</p>
            </div>

            {error && (
              <div className="bg-red-600/30 border border-red-600 text-white px-4 py-3 rounded-md mb-6">
                {error}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="username">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your username"
                  required
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-sm font-medium" htmlFor="password">
                    Password
                  </label>
                  <Link href="/forgot-password" className="text-sm text-blue-400 hover:underline">
                    Forgot password?
                  </Link>
                </div>
                <input
                  id="password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your password"
                  required
                />
              </div>

              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="rememberMe"
                  type="checkbox"
                  checked={formData.rememberMe}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-blue-500 border-slate-600 rounded focus:ring-blue-500"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-300">
                  Remember me
                </label>
              </div>

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
                    Signing in...
                  </span>
                ) : (
                  "Sign In"
                )}
              </button>

              <div className="text-center mt-4">
                <p className="text-slate-300">
                  Don't have an account?{" "}
                  <Link href="/register" className="text-blue-400 hover:underline">
                    Create one now
                  </Link>
                </p>
              </div>
            </form>
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
