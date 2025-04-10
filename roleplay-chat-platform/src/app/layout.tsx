import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import ClientEffects from "@/components/ClientEffects";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RoleplayHub - Character-Based Roleplay Platform",
  description: "Create detailed character profiles, find roleplay partners, and engage in real-time chats with the RoleplayHub platform. Our enhanced F-list inspired platform offers BBCode/CSS editing, kink ratings, and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="antialiased" suppressHydrationWarning>
        <ClientEffects />
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
