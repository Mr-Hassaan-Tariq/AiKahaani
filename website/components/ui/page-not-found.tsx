'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Home } from 'lucide-react';

import { Cursor } from 'components/ui/inverted-cursor';
import { Button } from 'components/shadcn_ui/button';

export default function PageNotFound() {
  const router = useRouter();

  return (
    <>
      <Cursor size={56} variant="red" />
      <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-white px-6 transition-colors duration-300 dark:bg-[#0a0a0a]">
        {/* Gradient orbs */}
        <div className="pointer-events-none absolute -left-32 -top-32 h-64 w-64 rounded-full bg-red-400/20 blur-3xl dark:bg-red-600/15" />
        <div className="pointer-events-none absolute -bottom-32 -right-32 h-80 w-80 rounded-full bg-pink-400/15 blur-3xl dark:bg-pink-600/10" />

        {/* Hero gradient overlay */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-pink-50/60 via-transparent to-transparent dark:from-gray-900/40 dark:via-transparent dark:to-transparent" />

        <div className="animate-fade-in-up relative z-10 w-full max-w-md text-center">
          <div className="group relative overflow-hidden rounded-2xl border border-gray-200/80 bg-white/90 p-8 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.08)] backdrop-blur-sm transition-all duration-300 hover:border-red-200 hover:shadow-xl hover:shadow-red-500/10 dark:border-gray-700/60 dark:bg-[#1C1C1E]/95 dark:hover:border-red-900/40 dark:hover:shadow-red-500/5">
            {/* Subtle inner glow */}
            <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-red-400/10 blur-2xl transition-opacity group-hover:opacity-100 dark:bg-red-500/10" />

            {/* 404 */}
            <div className="relative mb-6">
              <h1 className="mb-2 bg-gradient-to-r from-red-500 via-red-600 to-red-500 bg-clip-text text-6xl font-extrabold tracking-tight text-transparent md:text-7xl">
                404
              </h1>
              <div className="animate-glow-pulse mx-auto h-1.5 w-20 rounded-full bg-gradient-to-r from-red-400 via-red-500 to-red-600 shadow-lg shadow-red-500/30" />
            </div>

            <h2 className="mb-3 text-2xl font-bold text-gray-900 dark:text-white">
              Page not found
            </h2>

            <p className="mb-8 text-base leading-relaxed text-gray-600 dark:text-gray-400">
              The page you&apos;re looking for doesn&apos;t exist or has been moved to another
              location.
            </p>

            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button
                onClick={() => router.back()}
                variant="outline"
                className="h-12 rounded-full border-gray-300 px-6 font-semibold transition-all duration-300 hover:scale-[1.02] hover:border-red-500/50 hover:bg-red-50 hover:text-red-600 dark:border-gray-600 dark:hover:border-red-500/30 dark:hover:bg-red-900/20 dark:hover:text-red-400"
              >
                <ArrowLeft className="mr-2 h-5 w-5" />
                Go back
              </Button>
              <Button
                asChild
                className="group/btn h-12 rounded-full bg-gradient-to-r from-red-500 to-red-600 px-6 font-semibold text-white shadow-lg shadow-red-600/25 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-red-600/30"
              >
                <Link href="/">
                  <Home className="mr-2 h-5 w-5 transition-transform group-hover/btn:translate-x-0.5" />
                  Go home
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
