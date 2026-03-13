'use client';

import {
  FAQSection,
  Features,
  Footer,
  Hero,
  Marquee,
  Navbar,
  PricingAndIdentity,
  Steps,
} from 'components/landing';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white font-sans transition-colors duration-300 selection:bg-red-500 selection:text-white dark:bg-[#0a0a0a] dark:text-white">
      <style jsx global>{`
        @keyframes marquee {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .animate-marquee {
            animation: none;
          }
        }

        ::-webkit-scrollbar {
          width: 8px;
        }
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        ::-webkit-scrollbar-thumb {
          background: #333;
          border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: #444;
        }
      `}</style>

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
