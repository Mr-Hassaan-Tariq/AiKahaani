import { Fragment } from 'react';

import InsideCards from '../_component/InsideCards';
import QuestionWidget from '../../../components/ui/QuestionWidget';
import SuccessStoryWidget from '../../../components/ui/SuccessStoryWidget';
import AboutPartnerSection from './_components/AboutPartnerSection';
import CreatorsCard from './_components/CreatorsCard';
import UnlockTubeGenius from './_components/UnlockTubeGenius';
import HeroSection from 'components/ui/HeroSection';

export default function Page() {
  return (
    <Fragment>
      <HeroSection page="partner" />
      <AboutPartnerSection id="about-partner" />
      <InsideCards id="platform" />
      <CreatorsCard id="benefits" />
      <SuccessStoryWidget id="success-stories" />
      <QuestionWidget id="faq" />
      <UnlockTubeGenius />
    </Fragment>
  );
}
