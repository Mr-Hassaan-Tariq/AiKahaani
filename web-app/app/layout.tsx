import '../styles/globals.css';

import { Inter } from 'next/font/google';
import { GoogleOAuthProvider as OriginalGoogleOAuthProvider } from '@react-oauth/google';
import { env } from 'env.mjs';
import { ThemeProvider as NextThemesProvider } from 'next-themes';

import { AutoRefreshProvider } from 'lib/hooks/useAutoRefresh';
import ReactQueryProvider from 'lib/reactQuery/ReactQueryProvider';
import { Toaster } from 'components/shadcn_ui/sonner';

const INTER = Inter({
  variable: '--inter-font',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
});

export const metadata = {
  metadataBase: new URL(env.NEXT_PUBLIC_WEBSITE_URL),
  title: 'AiKahani',
  description:
    'AiKahani is an AI-powered script writing platform designed to help YouTube creators transform video ideas into professionally structured scripts.',
  icons: {
    icon: [
      { url: '/logos/icon.svg', type: 'image/svg+xml' },
      { url: '/logos/colored-logo.png', type: 'image/png' },
    ],
    apple: '/logos/colored-logo.png',
    shortcut: '/logos/colored-logo.png',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: env.NEXT_PUBLIC_WEBSITE_URL,
    siteName: 'AiKahani',
    title: 'AiKahani',
    description:
      'AiKahani is an AI-powered script writing platform designed to help YouTube creators transform video ideas into professionally structured scripts.',
    images: [
      {
        url: '/logos/colored-logo.png',
        width: 4000,
        height: 4000,
        alt: 'AiKahani',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AiKahani',
    description:
      'AiKahani is an AI-powered script writing platform designed to help YouTube creators transform video ideas into professionally structured scripts.',
    creator: '@aikahaani',
    images: ['/logos/colored-logo.png'],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${INTER.variable} bg-background font-inter antialiased`}>
        <NextThemesProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          storageKey="aikahaani-theme"
          disableTransitionOnChange
        >
          <OriginalGoogleOAuthProvider clientId={env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''}>
            <ReactQueryProvider>
              <AutoRefreshProvider>{children}</AutoRefreshProvider>
            </ReactQueryProvider>
            <Toaster
              toastOptions={{
                classNames: {
                  toast: 'rounded-xl border border-border bg-card shadow-md',
                  title: 'text-card-foreground text-sm font-semibold',
                  description: 'text-muted-foreground text-sm',
                  actionButton:
                    'bg-primary text-primary-foreground px-3 py-1.5 rounded-md text-xs font-medium',
                  cancelButton:
                    'bg-secondary text-secondary-foreground px-3 py-1.5 rounded-md text-xs font-medium',
                  closeButton: 'text-muted-foreground hover:text-foreground',
                  icon: 'text-primary',
                },
              }}
              position="top-right"
            />
          </OriginalGoogleOAuthProvider>
        </NextThemesProvider>
      </body>
    </html>
  );
}
