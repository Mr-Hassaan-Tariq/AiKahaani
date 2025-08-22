'use client';

import { useState } from 'react';
import Image from 'next/image';
import { FcGoogle } from 'react-icons/fc';

import Button from 'components/common/Button';
import TextField from 'components/common/TextField';

export default function Signup() {
  const [email, setEmail] = useState<string>('');

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0a0a0a] px-3">
      {/* Background grid effect */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)] opacity-50" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,#1a2e1d,transparent_40%)] opacity-50" />

      {/* Card */}
      <div className="relative z-10 w-[500px] w-full rounded-2xl bg-[#161616] p-8 shadow-lg">
        {/* Heading */}
        <h1 className="text-center text-3xl font-semibold text-white">Let’s get you creating</h1>
        <p className="mt-1 text-center text-sm text-gray-400">
          Sign in or create an account in seconds — no password needed.
        </p>

        {/* Email input */}
        <div className="mt-6">
          <TextField
            label="Label"
            placeholder="placeholder"
            type="email"
            className="w-full rounded-lg border border-transparent bg-[#2d2d2d] px-4 py-3 text-white placeholder-[#aaaca6] outline-none focus:border-green-500"
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
        <div className="my-4 flex items-center">
          <div className="h-px flex-grow bg-gray-700"></div>
          <span className="px-2 text-sm text-gray-500">or</span>
          <div className="h-px flex-grow bg-gray-700"></div>
        </div>

        {/* Google button */}
        <button className="flex w-full items-center justify-center space-x-2 rounded-full border border-gray-700 bg-[#1a1a1a] py-3 font-medium text-white transition hover:bg-[#222222]">
          <FcGoogle className="text-xl" />
          <span>Continue with Google</span>
        </button>
      </div>
    </div>
  );
}
