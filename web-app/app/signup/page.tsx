"use client"
import { FaGoogle } from 'react-icons/fa';
import Image from 'next/image';
import Button from 'components/common/Button';
import TextField from 'components/common/TextField';
import { useState } from "react";
import { FcGoogle } from "react-icons/fc";

export default function Signup() {
  const [email, setEmail] = useState<string>("");

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#0a0a0a] relative overflow-hidden px-3">
    {/* Background grid effect */}
    <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)] opacity-50" />
    <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,#1a2e1d,transparent_40%)] opacity-50" />

    {/* Card */}
    <div className="relative z-10 w-full w-[500px] bg-[#161616] p-8 rounded-2xl shadow-lg">
      {/* Heading */}
      <h1 className="text-white text-3xl font-semibold text-center">
        Let’s get you creating
      </h1>
      <p className="text-gray-400 text-center text-sm mt-1">
        Sign in or create an account in seconds — no password needed.
      </p>

      {/* Email input */}
      <div className="mt-6">
        <TextField
          label='Label'
          placeholder="placeholder"
          type="email"
          className="w-full rounded-lg bg-[#2d2d2d] text-white px-4 py-3 outline-none border border-transparent focus:border-green-500 placeholder-[#aaaca6]"
          value={email}
          onChange={(e) => setEmail(e)}
        />
      </div>

      {/* Magic link button */}
      {/* <button className="mt-4 w-full bg-green-500 hover:bg-green-600 text-black font-medium py-3 rounded-full transition flex items-center justify-center space-x-2">
        <span>✨ Send me the magic link</span>
      </button> */}
      <Button className="mt-4 flex items-center justify-center space-x-2">
        <Image src="/images/maginpan.svg" alt="maginpan" width={20} height={20} />
        <span>Send me the magic link</span>
      </Button>

      {/* Divider */}
      <div className="flex items-center my-4">
        <div className="flex-grow h-px bg-gray-700"></div>
        <span className="px-2 text-gray-500 text-sm">or</span>
        <div className="flex-grow h-px bg-gray-700"></div>
      </div>

      {/* Google button */}
      <button className="w-full bg-[#1a1a1a] border border-gray-700 hover:bg-[#222222] text-white font-medium py-3 rounded-full flex items-center justify-center space-x-2 transition">
        <FcGoogle className="text-xl" />
        <span>Continue with Google</span>
      </button>
    </div>
  </div>
  );
}
