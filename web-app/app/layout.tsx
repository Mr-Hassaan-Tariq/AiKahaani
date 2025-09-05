import '../styles/globals.css';

import { Figtree } from 'next/font/google';

import ReactQueryProvider from 'lib/reactQuery/ReactQueryProvider';
import { Toaster } from 'components/shadcn_ui/sonner';

const FIGTREE = Figtree({
  variable: '--figtree-font',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
});
export const metadata = {
  title: 'Tubegenius',
  description:
    'TubeGenius is envisioned as an AI-powered script writing platform specifically designed to automate and enhance the YouTube content creation process. The platform’s overarching goal is to function as "Your Genius AI Assistant for YouTube Automation," empowering content creators to effortlessly transform nascent video ideas into professionally structured and engaging scripts with minimal manual intervention',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${FIGTREE.variable} bg-black font-figtree`}>
        <ReactQueryProvider>{children}</ReactQueryProvider>
        <Toaster
          toastOptions={{
            classNames: {
              toast: 'bg-white/10 w-[558px] p-3 rounded-2xl',
              title: 'pl-4 text-white',
              description: 'pl-4 text-white',
            },
          }}
          position="top-right"
        />
      </body>
    </html>
  );
}
