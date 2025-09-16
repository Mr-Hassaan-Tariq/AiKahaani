'use client';

import { useState } from 'react';

import InfoModal from './InfoModal';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Slider } from 'components/shadcn_ui/slider';

export default function SliderWidget() {
  const [worldCounter, setWorldCounter] = useState([1000, 2000]);

  return (
    <Col className="gap-4">
      <Row className="justify-normal gap-2 text-white">
        <span> What’s your video about?</span>
        <InfoModal
          description={
            <Row className="gap-1 text-sm tracking-normal text-white">
              Approx. <b>150 words ≈ 1 minute</b> of speech
            </Row>
          }
        />
      </Row>
      <Slider
        defaultValue={worldCounter}
        onValueChange={setWorldCounter}
        max={10000}
        step={10}
        className="h-2"
      />

      <Row>
        <Text variant="xs" className="text-[#AAACA6]">
          {worldCounter[1] - worldCounter[0]} words
        </Text>

        <Text variant="xs" className="text-[#AAACA6]">
          10,000 words
        </Text>
      </Row>
    </Col>
  );
}
