'use client';

import { Clock, InfoIcon } from 'lucide-react';
import { RegisterOptions, useFormContext } from 'react-hook-form';

import { TemplateStyleType } from '../types';
import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import H5 from 'components/ui/H5';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function TemplatesWidget({
  templates,
  name,
  validationSchema,
}: {
  templates: TemplateStyleType[];
  name: string;
  validationSchema?: RegisterOptions;
}) {
  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext();

  const { onChange } = register(name, validationSchema);

  return (
    <Col>
      <Row>
        <Text variant="base" className="font-medium text-white">
          Choose a template style
        </Text>
        <Row className="gap-2">
          <InfoIcon size={16} className="cursor-pointer text-brand-secondary" />
          <Text variant="xs" className="text-brand-secondary">
            Optional
          </Text>
        </Row>
      </Row>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {templates.map((template) => (
          <Col
            key={template.id}
            className={cn(
              'cursor-pointer rounded-2xl bg-white/10 p-4',
              watch(name) === template.id && 'border border-[#BAFF38]/[12%] bg-[#F9F9FF]/[.16]',
            )}
            // onClick={() => setIsActive(template.id === isActive ? undefined : template.id)}
            onClick={() => onChange({ target: { name, value: template.id } })}
          >
            <Row>
              <H5 className="tracking-normal">{template.name}</H5>
              <Row className="gap-2 text-xs text-white">
                <Clock size={16} /> ~{template.duration}m, {template.word_range}
              </Row>
            </Row>
            <Text variant="xs" className="text-brand-secondary">
              {template.description}
            </Text>
          </Col>
        ))}
      </div>
      {errors[name]?.message && (
        <Text variant="xs" className="text-rose-500">
          {errors[name]?.message?.toString()}
        </Text>
      )}
    </Col>
  );
}
