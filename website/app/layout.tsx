import '../styles/globals.css';

import { Figtree } from 'next/font/google';
import Image from 'next/image';

import FooterWidget from 'components/ui/FooterWidget';
import NavSection from 'components/ui/NavSection';

const FIGTREE = Figtree({
  variable: '--figtree-font',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
});

export const metadata = {
  title: 'Tubegenius',
  description:
    'TubeGenius is envisioned as an AI-powered script writing platform specifically designed to automate and enhance the YouTube content creation process. The platform\'s overarching goal is to function as "Your Genius AI Assistant for YouTube Automation," empowering content creators to effortlessly transform nascent video ideas into professionally structured and engaging scripts with minimal manual intervention.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${FIGTREE.variable} bg-black font-figtree`}>
        <Image
          src="/images/grid.svg"
          alt="grid"
          width={7000}
          height={7000}
          className="absolute left-0 top-0"
        />
        {/* Navbar outside container for mobile */}
        <div className="block rounded-b-3xl border-b-4 border-b-gray-800 px-8 py-4 md:hidden">
          <NavSection />
        </div>

        <div className="container mx-auto px-8 py-8 md:px-12">
          {/* Navbar inside container for desktop */}
          <div className="hidden md:block">
            <NavSection />
          </div>
          {children}
          <FooterWidget />
        </div>
      </body>
    </html>
  );
}
