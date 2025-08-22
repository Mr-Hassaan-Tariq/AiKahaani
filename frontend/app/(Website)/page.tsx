import Hero from "./_component/Hero";
import HowItWorks from "./_component/HowItWorks";
import InsideCards from "./_component/InsideCards";
import Navbar from "./_component/Navbar";
import OfferSection from "./_component/Offer";

export default function Home() {
  return (
    <div>
      <Navbar />
      <Hero />
      <HowItWorks />
      <InsideCards />
      <OfferSection />
    </div>
  );
}
