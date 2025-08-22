import { Fragment } from 'react';

import HowItWorks from './_components/HowItWorks';
import Trends from './_components/trends';
import AffiliatesSection from './_components/WhyAffiliatesSection';
import HeroSection from 'components/ui/HeroSection';
import QuestionWidget from 'components/ui/QuestionWidget';

export default function Affiliate() {
  return (
    <Fragment>
      <HeroSection page="affiliates" />
      <HowItWorks id="how-it-works" />
      <AffiliatesSection id="benefits" />
      <Trends id="target-audience" />
      <QuestionWidget id="faq" />
    </Fragment>
  );
}
