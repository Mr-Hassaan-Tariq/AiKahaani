'use client';

import Image from 'next/image';

export default function MagicLinkSent() {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0a0a0a] px-3">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)] opacity-50" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,#1a2e1d,transparent_40%)] opacity-50" />

      {/* Card */}
      <div className="relative z-10 w-full max-w-md rounded-2xl bg-[#161616] p-10 text-center shadow-lg">
        <h1 className="text-2xl font-semibold text-white">Magic link sent!</h1>
        <p className="mt-2 text-sm text-gray-400">
          Check your inbox — click the link to <br /> enter your workspace.
        </p>

        {/* Success checkmark */}
        <div className="mt-8 flex items-center justify-center">
          <Image src="/images/right-check.svg" alt="check" width={100} height={100} />
        </div>

        {/* Resend */}
        <p className="mt-6 text-sm text-gray-500">
          Didn’t get the email?{' '}
          <button
            type="button"
            className="ml-1 text-white hover:underline"
            onClick={() => alert('Resend clicked')}
          >
            Resend
          </button>
        </p>
      </div>
    </div>
  );
}
