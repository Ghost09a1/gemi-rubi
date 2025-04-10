import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Navigation Bar */}
      <header className="bg-slate-800 shadow-md p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">RoleplayHub</h1>
          </div>
          <nav className="flex space-x-4">
            <Link href="/login" className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-md transition">
              Login
            </Link>
            <Link href="/register" className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-md transition">
              Sign Up
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto py-12 px-4 md:py-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              The Ultimate Roleplay Community
            </h2>
            <p className="text-lg mb-8 text-slate-300">
              Join thousands of roleplayers in a vibrant community offering character creation,
              real-time chat, and immersive roleplay experiences. Create detailed character profiles,
              manage preferences, and connect with like-minded players.
            </p>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
              <Link
                href="/register"
                className="bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-700 hover:to-teal-600
                          text-white font-semibold py-3 px-6 rounded-lg text-center"
              >
                Create Account
              </Link>
              <Link
                href="/about"
                className="bg-transparent border border-slate-500 hover:border-slate-400
                          text-white font-semibold py-3 px-6 rounded-lg text-center"
              >
                Learn More
              </Link>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 to-teal-500/30 rounded-lg"></div>
              <img
                src="https://ext.same-assets.com/2421641290/1360199898.png"
                alt="Character Illustration"
                className="rounded-lg shadow-xl w-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-slate-800 py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Platform Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-700 rounded-lg p-6 shadow-lg hover:translate-y-[-5px] transition duration-300">
              <div className="text-blue-400 text-4xl mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/></svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Character Creation</h3>
              <p className="text-slate-300">
                Create detailed character profiles with customizable fields, images, and preferences.
                Use our enhanced BBCode/Markdown editor for rich text formatting.
              </p>
            </div>
            <div className="bg-slate-700 rounded-lg p-6 shadow-lg hover:translate-y-[-5px] transition duration-300">
              <div className="text-teal-400 text-4xl mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4c0-1.1.9-2 2-2h8a2 2 0 0 1 2 2v5Z"/><path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1"/></svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Real-time Chat</h3>
              <p className="text-slate-300">
                Engage in private messages or group chats with multiple participants.
                Switch between characters seamlessly and enjoy rich formatting options.
              </p>
            </div>
            <div className="bg-slate-700 rounded-lg p-6 shadow-lg hover:translate-y-[-5px] transition duration-300">
              <div className="text-purple-400 text-4xl mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 0C1.46 6.7 1.33 10.28 4 13l8 8 8-8c2.67-2.72 2.54-6.3.42-8.42z"/></svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Advanced Preferences</h3>
              <p className="text-slate-300">
                Manage detailed preferences and kinks organized by categories.
                Set ratings from Favorite to No, and find compatible roleplay partners.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Community Stats */}
      <section className="container mx-auto py-16 px-4">
        <div className="bg-slate-800/50 rounded-lg p-8 shadow-lg">
          <h2 className="text-3xl font-bold text-center mb-8">Join Our Growing Community</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div>
              <p className="text-4xl font-bold text-blue-400 mb-2">10,000+</p>
              <p className="text-slate-300">Active Users</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-teal-400 mb-2">25,000+</p>
              <p className="text-slate-300">Characters</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-purple-400 mb-2">5,000+</p>
              <p className="text-slate-300">Daily Chats</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-indigo-400 mb-2">300+</p>
              <p className="text-slate-300">Kink Categories</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
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
    </div>
  );
}
