import '../styles/globals.css';

import { Figtree } from 'next/font/google';
import { GoogleOAuthProvider as OriginalGoogleOAuthProvider } from '@react-oauth/google';
import { env } from 'env.mjs';

import { AutoRefreshProvider } from 'lib/hooks/useAutoRefresh';
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
        <OriginalGoogleOAuthProvider clientId={env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''}>
          <ReactQueryProvider>
            <AutoRefreshProvider>{children}</AutoRefreshProvider>
          </ReactQueryProvider>
          <Toaster
            toastOptions={{
              classNames: {
                // Main toast container
                toast: 'rounded-xl border border-[#BAFF38]/[.12] bg-white/10 p-6 backdrop-blur-lg',
                // Toast title
                title: 'pl-4 text-black text-lg font-semibold',
                // Toast description
                description: 'pl-4 text-brand-secondary text-sm',
                // Action buttons
                actionButton: 'bg-blue-500 text-white px-4 py-2 rounded',
                // Cancel button
                cancelButton: 'bg-gray-500 text-white px-4 py-2 rounded',
                // Close button
                closeButton: 'text-gray-400 hover:text-gray-600',
                // Icon
                icon: 'text-green-500',
              },
            }}
            // style={
            //   {
            //     '--normal-bg': '#ffffff69',
            //     '--normal-text': 'black',
            //     '--normal-border': '#b9ff3869',
            //     '--success-bg': '#10b981',
            //     '--success-text': 'white',
            //     '--error-bg': '#ef4444',
            //     '--error-text': 'white',
            //     '--warning-bg': '#f59e0b',
            //     '--warning-text': 'white',
            //   } as React.CSSProperties
            // }
            position="top-right"
          />
        </OriginalGoogleOAuthProvider>
      </body>
    </html>
  );
}
