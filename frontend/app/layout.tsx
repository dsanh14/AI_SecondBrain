import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Second Brain",
  description: "AI-powered personal knowledge system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-100 min-h-screen`}>
        <div className="flex flex-col min-h-screen">
          <header className="border-b border-gray-800 bg-gray-900">
            <div className="container mx-auto p-4">
              <div className="flex items-center justify-between">
                <Link href="/" className="text-xl font-bold text-white">
                  AI Second Brain
                </Link>
                <nav className="flex gap-6">
                  <Link href="/" className="hover:text-blue-400 transition">
                    Dashboard
                  </Link>
                  <Link href="/notes" className="hover:text-blue-400 transition">
                    Notes
                  </Link>
                  <Link href="/search" className="hover:text-blue-400 transition">
                    Search
                  </Link>
                  <Link href="/upload" className="hover:text-blue-400 transition">
                    Upload
                  </Link>
                  <Link href="/graph" className="hover:text-blue-400 transition">
                    Graph
                  </Link>
                </nav>
              </div>
            </div>
          </header>
          <main className="container mx-auto p-4 flex-1">
            {children}
          </main>
          <footer className="border-t border-gray-800 bg-gray-900 py-4">
            <div className="container mx-auto text-center text-gray-500 text-sm">
              <p>© {new Date().getFullYear()} AI Second Brain</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
