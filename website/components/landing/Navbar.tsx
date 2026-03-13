'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, Sparkles, X } from 'lucide-react';

import { Button } from 'components/shadcn_ui/button';
import { ThemeToggle } from 'components/ThemeToggle';

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed left-0 right-0 top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md transition-colors duration-300 dark:border-white/5 dark:bg-[#0a0a0a]/80">
      <div className="container mx-auto flex h-20 items-center justify-between px-6 md:grid md:grid-cols-3 md:gap-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-600 shadow-lg shadow-red-600/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            videoScript
          </span>
        </div>

        <div className="hidden items-center justify-center gap-8 text-gray-600 dark:text-gray-400 md:flex">
          <Link
            href="#features"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            Features
          </Link>
          <Link
            href="#how-it-works"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            How it works
          </Link>
          <Link
            href="#pricing"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            Pricing
          </Link>
          <Link
            href="#faq"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            FAQ
          </Link>
        </div>

        <div className="hidden items-center justify-end gap-3 md:flex">
          <ThemeToggle className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-white/10 dark:hover:text-white" />
          <Link
            href="/login"
            className="text-sm font-medium text-gray-700 transition-colors hover:text-red-500 dark:text-gray-300"
          >
            Login
          </Link>
          <Button className="rounded-full bg-red-600 px-6 font-semibold text-white transition-all hover:translate-y-[-2px] hover:bg-red-700 hover:shadow-lg hover:shadow-red-600/30 active:translate-y-0">
            Try Free
          </Button>
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle className="rounded-lg p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white" />
          <button className="text-gray-900 dark:text-white" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="flex flex-col gap-6 border-b border-gray-200 bg-white px-6 py-8 duration-300 animate-in slide-in-from-top dark:border-white/5 dark:bg-[#0a0a0a] md:hidden">
          <Link
            href="#features"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            Features
          </Link>
          <Link
            href="#how-it-works"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            How it works
          </Link>
          <Link
            href="#pricing"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            Pricing
          </Link>
          <Link
            href="#faq"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            FAQ
          </Link>
          <div className="flex flex-col gap-4 pt-4">
            <Link
              href="/login"
              className="text-center text-lg font-medium text-gray-900 dark:text-white"
            >
              Login
            </Link>
            <Button className="rounded-full bg-red-600 py-6 text-lg font-semibold text-white hover:bg-red-700">
              Try Free
            </Button>
          </div>
        </div>
      )}
    </nav>
  );
}
