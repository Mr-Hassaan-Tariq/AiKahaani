import '../styles/globals.css';

import { Figtree } from 'next/font/google';
import { ThemeProvider as NextThemesProvider } from 'next-themes';

import { FAQ_SCHEMA, SEO, SITE_URL } from 'lib/seo';

const FIGTREE = Figtree({
  variable: '--figtree-font',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
});

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: SEO.title,
    template: '%s | AIKahaani',
  },
  description: SEO.description,
  keywords: SEO.keywords,
  authors: [{ name: 'AIKahaani', url: SITE_URL }],
  creator: 'AIKahaani',
  publisher: 'AIKahaani',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: SITE_URL,
    siteName: SEO.openGraph.siteName,
    title: SEO.title,
    description: SEO.description,
    images: [
      {
        url: `${SITE_URL}/logo.svg`,
        width: 512,
        height: 512,
        alt: 'AIKahaani - AI YouTube Script & Title Generator',
      },
    ],
  },
  twitter: {
    card: SEO.twitter.card,
    title: SEO.title,
    description: SEO.description,
    creator: SEO.twitter.creator,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: SITE_URL,
  },
  category: 'technology',
};

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebApplication',
      '@id': `${SITE_URL}/#webapp`,
      name: 'AIKahaani',
      alternateName: ['AI Kahaani', 'AI Kahaani Story', 'AI Story'],
      description:
        'AIKahaani (AI + Kahaani) is an AI-powered web tool that helps YouTube creators generate high-quality video scripts, engaging titles, and video outlines in seconds. Built for beginner creators, faceless YouTube channels, and content marketers.',
      url: SITE_URL,
      applicationCategory: 'MultimediaApplication',
      operatingSystem: 'Web',
      offers: {
        '@type': 'Offer',
        price: '19',
        priceCurrency: 'USD',
      },
    },
    {
      '@type': 'Organization',
      '@id': `${SITE_URL}/#organization`,
      name: 'AIKahaani',
      url: SITE_URL,
      logo: {
        '@type': 'ImageObject',
        url: `${SITE_URL}/logo.svg`,
      },
    },
    {
      '@type': 'SoftwareApplication',
      '@id': `${SITE_URL}/#software`,
      name: 'AIKahaani',
      applicationCategory: 'MultimediaApplication',
      operatingSystem: 'Web',
      description:
        'AI-powered YouTube script and title generator. Turn topics or keywords into complete YouTube-ready scripts with hooks, storytelling, and CTAs in seconds.',
      featureList: [
        'AI YouTube script generation',
        'Engaging title generator',
        'Video outline creation',
        'Hook and CTA optimization',
        'Multiple script variations',
      ],
    },
    {
      '@type': 'FAQPage',
      '@id': `${SITE_URL}/#faq`,
      mainEntity: FAQ_SCHEMA.map((faq) => ({
        '@type': 'Question',
        name: faq.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: faq.answer,
        },
      })),
    },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${FIGTREE.variable} bg-white font-figtree transition-colors dark:bg-[#0a0a0a]`}
      >
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <NextThemesProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          storageKey="aikahaani-theme"
          disableTransitionOnChange
        >
          <img src="/svg/top-left-gid.svg" alt="grid" className="absolute left-0 top-0" />
          {children}
        </NextThemesProvider>
      </body>
    </html>
  );
}
