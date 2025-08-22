import { Fragment } from 'react';

import QuestionWidget from '../../components/ui/QuestionWidget';
import SuccessStoryWidget from '../../components/ui/SuccessStoryWidget';
import AffiliateProgram from './_component/AffiliateProgram';
import HowItWorks from './_component/HowItWorks';
import InsideCards from './_component/InsideCards';
import OfferSection from './_component/offer';
import HeroSection from 'components/ui/HeroSection';

export default async function Home() {
  return (
    <Fragment>
      <HeroSection page="home" />
      <HowItWorks id="how-it-works" />
      <InsideCards id="features" />
      <OfferSection />
      <SuccessStoryWidget id="success-stories" />
      <QuestionWidget id="faq" />
      <AffiliateProgram id="affiliates" />
    </Fragment>
  );
}
