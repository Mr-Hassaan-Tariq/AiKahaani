'use client';

import { useRouter } from 'next/navigation';

const NotFoundPage = () => {
  const router = useRouter();

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-green-900 via-gray-900 to-black p-4">
      <div className="w-full max-w-md rounded-2xl border border-gray-700 bg-gray-800 bg-opacity-90 p-8 text-center shadow-2xl backdrop-blur-sm">
        {/* 404 Number */}
        <div className="mb-6">
          <h1 className="mb-2 text-6xl font-bold text-green-400">404</h1>
          <div className="mx-auto h-1 w-16 rounded-full bg-green-400"></div>
        </div>

        {/* Main Message */}
        <h2 className="mb-3 text-2xl font-semibold text-white">Page not found</h2>

        {/* Subtitle */}
        <p className="mb-8 leading-relaxed text-gray-400">
          The page you&apos;re looking for doesn&apos;t exist or has been moved to another location.
        </p>

        {/* Action Buttons */}
        <div className="space-y-4">
          {/* Primary Button */}
          <button
            onClick={() => router.back()}
            className="w-full transform rounded-xl bg-green-500 px-6 py-3 font-medium text-black shadow-lg transition-all duration-200 ease-in-out hover:scale-105 hover:bg-green-600 hover:shadow-green-500/25 active:scale-95"
          >
            ← Go back
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
