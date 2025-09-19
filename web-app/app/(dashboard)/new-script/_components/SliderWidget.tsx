'use client';

import { useEffect, useState } from 'react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { LengthRangeType } from '../types';
import InfoModal from './InfoModal';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import { Slider } from 'components/shadcn_ui/slider';

const MIN_LENGTH = 'min_length';
const MAX_LENGTH = 'max_length';

export default function SliderWidget({
  range,
  validationSchema,
}: {
  range: LengthRangeType;
  validationSchema?: RegisterOptions;
}) {
  const [worldCounter, setWorldCounter] = useState([range.min, range.default]);

  const {
    register,
    formState: { errors },
  } = useFormContext();

  const { onChange: onMinLength } = register(MIN_LENGTH);
  const { onChange: onMaxLength } = register(MAX_LENGTH, validationSchema);

  useEffect(() => {
    if (worldCounter) {
      onMinLength({ target: { name: MIN_LENGTH, value: worldCounter[0] } });
      onMaxLength({ target: { name: MAX_LENGTH, value: worldCounter[1] } });
    }
  }, [onMinLength, onMaxLength, worldCounter]);

  return (
    <Col className="gap-4">
      <Row className="justify-normal gap-2 text-white">
        <span> {'What’s your video about?'}</span>
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
        min={range.min}
        max={range.max}
        step={10}
        className="h-2"
      />

      <Row>
        <Text variant="xs" className="text-[#AAACA6]">
          {worldCounter[1] - worldCounter[0]} words
        </Text>

        <Text variant="xs" className="text-[#AAACA6]">
          {range.max} words
        </Text>
      </Row>

      {errors[MAX_LENGTH]?.message && (
        <Text variant="xs" className="-mt-2 text-rose-500">
          {errors[MAX_LENGTH]?.message?.toString()}
        </Text>
      )}
    </Col>
  );
}
