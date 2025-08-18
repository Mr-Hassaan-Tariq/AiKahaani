import Navbar from "./_component/Navbar";
import Hero from "./_component/Hero";
import HowItWorks from "./_component/HowItWorks";
import InsideCards from "./_component/InsideCards";

export default function Home() {
  return (
    <div >
      <Navbar />
      <Hero />
      <HowItWorks />
      <InsideCards />
    </div>
  );
}