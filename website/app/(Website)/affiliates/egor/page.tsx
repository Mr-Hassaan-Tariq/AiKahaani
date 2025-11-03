import { Fragment } from 'react';

import HeroSection from 'components/ui/HeroSection';
import QuestionWidget from '../../../../components/ui/QuestionWidget';
import SuccessStoryWidget from '../../../../components/ui/SuccessStoryWidget';
import InsideCards from '../../_component/InsideCards';
import AboutPartnerSection from './_components/AboutPartnerSection';
import CreatorsCard from './_components/CreatorsCard';
import UnlockTubeGenius from './_components/UnlockTubeGenius';

export default function Page() {
  return (
    <Fragment>
      <HeroSection page="partner" />
      <AboutPartnerSection id="about-partner" />
      <InsideCards id="platform" page="partner" />
      <CreatorsCard id="benefits" />
      <SuccessStoryWidget id="success-stories" />
      <QuestionWidget id="faq" />
      <UnlockTubeGenius />
    </Fragment>
  );
}
