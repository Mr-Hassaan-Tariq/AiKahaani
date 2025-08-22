import FooterWidget from '../_component/FooterWidget';
import Hero from '../_component/Hero';  
import InsideCards from '../_component/InsideCards';
import CreatorsCard from './_components/CreatorsCard';
import Navbar from '../_component/Navbar';
import QuestionWidget from '../_component/QuestionWidget';
import SuccessStoryWidget from '../_component/SuccessStoryWidget';
import AboutPartnerSection from './_components/AboutPartnerSection';
import UnlockTubeGenius from './_components/UnlockTubeGenius';

export default function Page() {
  return (
    <div>
      <Navbar />
      <Hero aboutPartner />
      <AboutPartnerSection />
      <InsideCards />
      <CreatorsCard />
      <SuccessStoryWidget />
      <QuestionWidget />
      <UnlockTubeGenius />
      <FooterWidget />
    </div>
  );
}
