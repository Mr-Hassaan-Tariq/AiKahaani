import dynamic from 'next/dynamic';

import { Hero, Marquee, Navbar } from 'components/landing';

const Features = dynamic(() => import('components/landing').then((m) => ({ default: m.Features })));
const Steps = dynamic(() => import('components/landing').then((m) => ({ default: m.Steps })));
const PricingAndIdentity = dynamic(() =>
  import('components/landing').then((m) => ({ default: m.PricingAndIdentity }))
);
const FAQSection = dynamic(() =>
  import('components/landing').then((m) => ({ default: m.FAQSection }))
);
const Footer = dynamic(() => import('components/landing').then((m) => ({ default: m.Footer })));

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white font-sans transition-colors duration-300 selection:bg-red-500 selection:text-white dark:bg-[#0a0a0a] dark:text-white">
      <div className="relative">
        <Navbar />
        <main>
          <Hero />
          <Marquee />
          <Features />
          <Steps />
          <PricingAndIdentity />
          <FAQSection />
        </main>
        <Footer />
      </div>
    </div>
  );
}
