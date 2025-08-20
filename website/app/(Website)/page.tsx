import AffiliateProgram from './_component/AffiliateProgram';
import FooterWidget from './_component/FooterWidget';
import Hero from './_component/Hero';
import HowItWorks from './_component/HowItWorks';
import InsideCards from './_component/InsideCards';
import Navbar from './_component/Navbar';
import QuestionWidget from './_component/QuestionWidget';
import SuccessStoryWidget from './_component/SuccessStoryWidget';

export default function Home() {
  return (
    <div>
      <Navbar />
      <Hero />
      <HowItWorks />
      <InsideCards />
      <SuccessStoryWidget />
      <QuestionWidget />
      <AffiliateProgram />
      <FooterWidget />
    </div>
  );
}
