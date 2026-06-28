import Link from 'next/link';

import { Logo } from 'components/Logo';

export function Footer() {
  return (
    <footer className="border-t border-gray-100 bg-gray-50 px-6 py-16 transition-colors duration-300 dark:border-white/5 dark:bg-[#0a0a0a]">
      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col items-center justify-between gap-10 md:flex-row">
          <div className="flex flex-col items-center gap-4 md:items-start">
            <Link href="/" className="flex items-center">
              <Logo size="md" />
            </Link>
            <p className="font-bold text-gray-400">Empowering the next generation of creators.</p>
          </div>

          <div className="flex flex-wrap justify-center gap-10 text-[10px] font-bold uppercase tracking-widest text-gray-500">
            <Link href="/pricing" className="transition-colors hover:text-red-500">
              Pricing
            </Link>
            <Link href="/terms" className="transition-colors hover:text-red-500">
              Terms
            </Link>
            <Link href="/privacy" className="transition-colors hover:text-red-500">
              Privacy
            </Link>
            <Link href="/refund" className="transition-colors hover:text-red-500">
              Refund Policy
            </Link>
            <Link href="/contact" className="transition-colors hover:text-red-500">
              Contact
            </Link>
          </div>
        </div>

        <div className="mt-16 flex flex-col items-center justify-between gap-6 border-t border-gray-200 pt-8 dark:border-white/5 md:flex-row">
          <div className="text-sm font-bold text-gray-400">
            © 2025 AIKahaani. All rights reserved.
          </div>

          <div className="flex gap-8">
            <Link
              href="/privacy"
              className="text-sm font-bold text-gray-400 transition-colors hover:text-red-500"
            >
              Privacy Policy
            </Link>
            <Link
              href="/terms"
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
