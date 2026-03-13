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
