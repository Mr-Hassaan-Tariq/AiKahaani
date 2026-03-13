import Link from 'next/link';
import { Sparkles } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-gray-100 bg-gray-50 px-6 py-16 transition-colors duration-300 dark:border-white/5 dark:bg-[#0a0a0a]">
      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col items-center justify-between gap-10 md:flex-row">
          <div className="flex flex-col items-center gap-4 md:items-start">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-600 shadow-lg shadow-red-600/20">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-2xl font-black tracking-tighter text-gray-900 dark:text-white">
                videoScript
              </span>
            </div>
            <p className="font-bold text-gray-400">Empowering the next generation of creators.</p>
          </div>

          <div className="flex flex-wrap justify-center gap-10 text-[10px] font-bold uppercase tracking-widest text-gray-500">
            <Link href="#" className="transition-colors hover:text-red-500">
              Product
            </Link>
            <Link href="#" className="transition-colors hover:text-red-500">
              Resources
            </Link>
            <Link href="#" className="transition-colors hover:text-red-500">
              Company
            </Link>
            <Link href="#" className="transition-colors hover:text-red-500">
              Social
            </Link>
          </div>
        </div>

        <div className="mt-16 flex flex-col items-center justify-between gap-6 border-t border-gray-200 pt-8 dark:border-white/5 md:flex-row">
          <div className="text-sm font-bold text-gray-400">
            © 2025 videoScript Inc. All rights reserved.
          </div>

          <div className="flex gap-8">
            <Link
              href="#"
              className="text-sm font-bold text-gray-400 transition-colors hover:text-red-500"
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              className="text-sm font-bold text-gray-400 transition-colors hover:text-red-500"
            >
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
