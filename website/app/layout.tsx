import '../styles/globals.css';

import { Figtree } from 'next/font/google';
import { ThemeProvider as NextThemesProvider } from 'next-themes';

// import TopLeftSvg from '../assert/svg/top-left-gid.svg';

const FIGTREE = Figtree({
  variable: '--figtree-font',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
});

export const metadata = {
  title: 'videoScript',
  description:
    'videoScript is an AI-powered script writing platform specifically designed to automate and enhance the YouTube content creation process. The platform\'s overarching goal is to function as "Your Genius AI Assistant for YouTube Automation," empowering content creators to effortlessly transform nascent video ideas into professionally structured and engaging scripts with minimal manual intervention.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${FIGTREE.variable} bg-white font-figtree transition-colors dark:bg-[#0a0a0a]`}
      >
        <NextThemesProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          storageKey="videoscript-theme"
          disableTransitionOnChange
        >
          <img src="/svg/top-left-gid.svg" alt="grid" className="absolute left-0 top-0" />
          {/* Navbar outside container for mobile */}

          <div className="block rounded-b-3xl border-b-2 border-b-green-800 px-8 py-4 md:hidden">
            {/* <NavSection /> */}
          </div>

          <div className="">
            {/* Navbar inside container for desktop */}
            <div className="container mx-auto hidden px-8 py-8 md:block md:px-12">
              {/* <NavSection /> */}
            </div>
            {children}
            {/* <FooterWidget /> */}
          </div>
        </NextThemesProvider>
      </body>
    </html>
  );
}
