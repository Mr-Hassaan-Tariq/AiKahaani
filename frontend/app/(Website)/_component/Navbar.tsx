"use client";
import { Menu, X } from "lucide-react";
import Image from "next/image";
import { useState } from "react";

export default function Navbar() {
    const [isOpen, setIsOpen] = useState<boolean>(false);

    return (
        <nav className="flex justify-between items-center px-8 md:px-12 py-8 bg-black text-white relative">
            {/* Logo */}
            <div className="flex items-center gap-2">
                <Image src="/images/logo.png" alt="logo" width={200} height={100} />
            </div>

            {/* Desktop Menu */}
            <ul className="hidden md:flex gap-8">
                <li className="hover:text-green-500 transition duration-300 cursor-pointer">How it works</li>
                <li className="hover:text-green-500 transition duration-300 cursor-pointer">Features</li>
                <li className="hover:text-green-500 transition duration-300 cursor-pointer">Success stories</li>
                <li className="hover:text-green-500 transition duration-300 cursor-pointer">Affiliates</li>
            </ul>

            {/* Desktop Buttons */}
            <div className="hidden md:flex gap-4">
                <button className="bg-[#262724] px-4 py-3 rounded-full">
                    Login
                </button>
                <button className="flex items-center gap-2 bg-[#2BFF13] pl-4 rounded-full text-black text-sm" style={{ fontWeight: "600" }}>
                    Get Started
                    <span className="bg-white rounded-full w-10 h-10 flex items-center justify-center"><Image src="/images/arrow_right.svg" alt="arrow_right" width={20} height={20} /></span>
                </button>
            </div>

            {/* Mobile Hamburger Button */}
            <button
                className="md:hidden text-white"
                onClick={() => setIsOpen((prev) => !prev)}
                aria-label="Toggle menu"
            >
                {isOpen ? <X size={28} /> : <Menu size={28} />}
            </button>

            {/* Mobile Dropdown Menu */}
            {isOpen && (
                <div className="absolute top-16 left-0 w-full bg-black/95 backdrop-blur-md border-t border-gray-800 md:hidden z-50 animate-slideDown">
                    <ul className="flex flex-col gap-6 p-6 text-lg">
                        <li className="hover:text-green-500 transition duration-300 cursor-pointer">How it works</li>
                        <li className="hover:text-green-500 transition duration-300 cursor-pointer">Features</li>
                        <li className="hover:text-green-500 transition duration-300 cursor-pointer">Success stories</li>
                        <li className="hover:text-green-500 transition duration-300 cursor-pointer">FAQ</li>
                    </ul>
                    <div className="flex flex-col gap-4 p-6">
                        <button className="bg-gray-800 px-4 py-2 rounded-lg hover:bg-gray-700 transition duration-300">
                            Login
                        </button>
                        <button className="bg-green-500 px-4 py-2 rounded-lg hover:bg-green-600 transition duration-300">
                            Get Started →
                        </button>
                    </div>
                </div>
            )}
        </nav>
    );
}
