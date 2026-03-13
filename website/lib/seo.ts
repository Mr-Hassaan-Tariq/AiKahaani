export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://aikahaani.com';

/**
 * AIKahaani = AI + Kahaani (story)
 * A web-based AI tool for YouTube creators to generate scripts, titles, and outlines in seconds.
 */
export const SEO = {
  title: 'AIKahaani | AI YouTube Script & Title Generator for Creators',
  description:
    'AIKahaani (AI + Kahaani) is an AI-powered web tool that helps YouTube creators generate high-quality video scripts, engaging titles, and video outlines in seconds. Enter a topic or keyword—get a complete YouTube-ready script with hooks, storytelling, and CTAs. Built for beginner creators, faceless channels, and content marketers.',
  shortDescription:
    'AI-powered YouTube script and title generator. Turn topics into publish-ready scripts in seconds.',
  keywords: [
    'AIKahaani',
    'AI Kahaani',
    'AI story',
    'YouTube script generator',
    'AI script writer',
    'YouTube title generator',
    'video script AI',
    'faceless YouTube',
    'content creator tools',
    'YouTube automation',
    'script writing AI',
    'video content generator',
    'AI storytelling',
    'YouTube creator tool',
    'script generator for YouTube',
  ].join(', '),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    siteName: 'AIKahaani',
  },
  twitter: {
    card: 'summary_large_image',
    creator: '@aikahaani',
  },
};

export const FAQ_SCHEMA = [
  {
    question: 'Can I generate scripts for different languages?',
    answer:
      'Yes! AIKahaani supports over 50 languages. Our AI is trained on global YouTube data, so it understands local context and slang as well.',
  },
  {
    question: 'How does the pacing engine work?',
    answer:
      'Our engine analyzes retention patterns from millions of successful videos. It inserts pattern interrupts, transitions, and calls-to-action at the exact moments viewers typically drop off.',
  },
  {
    question: 'Is it really different from using ChatGPT?',
    answer:
      'Absolutely. While ChatGPT is generic, AIKahaani is fine-tuned specifically for YouTube. It includes niche topic discovery, viral hook frameworks, and storyboard generation that generic LLMs fail at.',
  },
  {
    question: 'Can I save my custom voice/style?',
    answer:
      'Yes, you can upload your previous successful scripts to train your personalized style profile, ensuring every generated script sounds exactly like you.',
  },
];
