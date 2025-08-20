import FooterWidget from '@/(Website)/_component/FooterWidget';
import Navbar from '@/(Website)/_component/Navbar';
import QuestionWidget from '@/(Website)/_component/QuestionWidget';

import Hero from './_components/Hero';
import HowItWorks from './_components/HowItWorks';
import Trends from './_components/trends';
import AffiliatesSection from './_components/WhyAffiliatesSection';

export default function Affiliate() {
  return (
    <div>
      <Navbar />
      <Hero />
      <HowItWorks />
      <AffiliatesSection />
      <Trends />
      <QuestionWidget />
      <FooterWidget />
    </div>
  );
}
