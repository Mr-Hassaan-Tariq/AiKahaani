'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Menu, X } from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  return (
    <nav className="relative flex items-center justify-between bg-black px-8 py-8 text-white md:px-12">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <Image src="/images/logo.png" alt="logo" width={200} height={100} />
      </div>

      {/* Desktop Menu */}
      <ul className="hidden gap-8 md:flex">
        <li className="cursor-pointer transition duration-300 hover:text-green-500">
          How it works
        </li>
        <li className="cursor-pointer transition duration-300 hover:text-green-500">Features</li>
        <li className="cursor-pointer transition duration-300 hover:text-green-500">
          Success stories
        </li>
        <li className="cursor-pointer transition duration-300 hover:text-green-500">Affiliates</li>
      </ul>

      {/* Desktop Buttons */}
      <div className="hidden gap-4 md:flex">
        <button className="rounded-full bg-[#262724] px-4 py-3">Login</button>
        <button
          className="flex items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black"
          style={{ fontWeight: '600' }}
        >
          Get Started
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
            <Image src="/images/arrow_right.svg" alt="arrow_right" width={20} height={20} />
          </span>
        </button>
      </div>

      {/* Mobile Hamburger Button */}
      <button
        className="text-white md:hidden"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="Toggle menu"
      >
        {isOpen ? <X size={28} /> : <Menu size={28} />}
      </button>

      {/* Mobile Dropdown Menu */}
      {isOpen && (
        <div className="animate-slideDown absolute left-0 top-16 z-50 w-full border-t border-gray-800 bg-black/95 backdrop-blur-md md:hidden">
          <ul className="flex flex-col gap-6 p-6 text-lg">
            <li className="cursor-pointer transition duration-300 hover:text-green-500">
              How it works
            </li>
            <li className="cursor-pointer transition duration-300 hover:text-green-500">
              Features
            </li>
            <li className="cursor-pointer transition duration-300 hover:text-green-500">
              Success stories
            </li>
            <li className="cursor-pointer transition duration-300 hover:text-green-500">FAQ</li>
          </ul>
          <div className="flex flex-col gap-4 p-6">
            <button className="rounded-lg bg-gray-800 px-4 py-2 transition duration-300 hover:bg-gray-700">
              Login
            </button>
            <button className="rounded-lg bg-green-500 px-4 py-2 transition duration-300 hover:bg-green-600">
              Get Started →
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
