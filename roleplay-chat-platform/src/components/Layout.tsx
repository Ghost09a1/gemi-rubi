"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface HeaderProps {
  // Optional user data for logged in state
  user?: {
    username: string;
    avatar?: string;
  };
  // Optional current character for switching
  currentCharacter?: {
    id: string;
    name: string;
    avatar?: string;
  };
}

export function Header({ user, currentCharacter }: HeaderProps) {
  const pathname = usePathname();

  // Navigation items that appear when logged in
  const navItems = [
    { name: "Home", path: "/" },
    { name: "Characters", path: "/characters" },
    { name: "Chat", path: "/chat" },
    { name: "Browse", path: "/browse" },
    { name: "Help", path: "/help" },
  ];

  return (
    <header className="bg-slate-800 shadow-md p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center">
          <Link href="/" className="mr-8">
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
              RoleplayHub
            </h1>
          </Link>

          {/* Main navigation for logged in users */}
          {user && (
            <nav className="hidden md:flex space-x-6">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`text-sm font-medium ${
                    pathname === item.path
                      ? "text-blue-400"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* User is logged in */}
          {user ? (
            <>
              {/* Current character selection (if applicable) */}
              {currentCharacter && (
                <div className="hidden md:flex items-center bg-slate-700 rounded-md px-3 py-1">
                  <span className="text-xs text-slate-400 mr-2">Playing as:</span>
                  <div className="flex items-center">
                    {currentCharacter.avatar ? (
                      <img
                        src={currentCharacter.avatar}
                        alt={currentCharacter.name}
                        className="w-6 h-6 rounded-full mr-2 object-cover"
                      />
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-blue-500 mr-2 flex items-center justify-center text-xs font-bold">
                        {currentCharacter.name.charAt(0)}
                      </div>
                    )}
                    <span className="text-sm font-medium text-white">
                      {currentCharacter.name}
                    </span>
                  </div>
                </div>
              )}

              {/* User menu */}
              <div className="relative">
                <button className="flex items-center text-white hover:text-blue-400 transition">
                  {user.avatar ? (
                    <img
                      src={user.avatar}
                      alt={user.username}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-teal-500 flex items-center justify-center text-white font-bold">
                      {user.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="hidden md:block ml-2">{user.username}</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 ml-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {/* Dropdown menu (would be implemented with useState in a real component) */}
              </div>
            </>
          ) : (
            /* User is not logged in */
            <nav className="flex space-x-3">
              <Link
                href="/login"
                className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-md transition text-sm"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-md transition text-sm"
              >
                Sign Up
              </Link>
            </nav>
          )}
        </div>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="bg-slate-800 py-8 px-4">
      <div className="container mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl font-semibold mb-4">RoleplayHub</h3>
            <p className="text-slate-300">
              The premier platform for character-based roleplay.
              All characters and content are works of fiction.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-slate-300">
              <li><Link href="/login" className="hover:text-white">Login</Link></li>
              <li><Link href="/register" className="hover:text-white">Register</Link></li>
              <li><Link href="/about" className="hover:text-white">About Us</Link></li>
              <li><Link href="/help" className="hover:text-white">Help</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-4">Legal</h3>
            <ul className="space-y-2 text-slate-300">
              <li><Link href="/terms" className="hover:text-white">Terms of Service</Link></li>
              <li><Link href="/privacy" className="hover:text-white">Privacy Policy</Link></li>
              <li><Link href="/guidelines" className="hover:text-white">Community Guidelines</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-slate-700 mt-8 pt-8 text-center text-slate-400">
          <p>© 2024 RoleplayHub. All rights reserved. 18+ ONLY.</p>
        </div>
      </div>
    </footer>
  );
}

// This layout component combines both Header and Footer with optional props
interface LayoutProps {
  children: React.ReactNode;
  user?: {
    username: string;
    avatar?: string;
  };
  currentCharacter?: {
    id: string;
    name: string;
    avatar?: string;
  };
}

export default function Layout({ children, user, currentCharacter }: LayoutProps) {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col">
      <Header user={user} currentCharacter={currentCharacter} />
      <main className="flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  );
}
