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
  disabled,
  validationSchema,
  defaultValue,
}: {
  range: LengthRangeType;
  disabled: boolean;
  validationSchema?: RegisterOptions;

  defaultValue?: number[];
}) {
  const [value, setValue] = useState(defaultValue?.[1] ?? range.default);

  const {
    register,
    formState: { errors },
  } = useFormContext();

  const { onChange: onMinLength } = register(MIN_LENGTH);
  const { onChange: onMaxLength } = register(MAX_LENGTH, validationSchema);

  useEffect(() => {
    onMinLength({ target: { name: MIN_LENGTH, value: 0 } });
    onMaxLength({ target: { name: MAX_LENGTH, value } });
  }, [value]);

  return (
    <Col className="gap-4">
      <Row className="justify-normal gap-2 text-white">
        <span> {'Script length & duration'}</span>
        <InfoModal
          description={
            <Row className="gap-1 text-sm tracking-normal text-white">
              Approx. <b>150 words ≈ 1 minute</b> of speech
            </Row>
          }
        />
      </Row>
      <Slider
        value={[value]}
        onValueChange={(val) => setValue(val[0])}
        min={0}
        max={range.max}
        step={10}
        disabled={disabled}
        className="h-2"
      />

      <Row>
        <Text variant="xs" className="text-[#AAACA6]">
          {value} words
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
