'use client';

import { useState } from 'react';
import { Clock, InfoIcon } from 'lucide-react';

import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import H5 from 'components/ui/H5';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function TemplatesWidget() {
  const [isActive, setIsActive] = useState<string>();
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
              'rounded-2xl bg-white/10 p-4',
              isActive === template.id && 'border border-[#BAFF38]/[12%] bg-[#F9F9FF]/[.16]',
            )}
            onClick={() => setIsActive(template.id === isActive ? undefined : template.id)}
          >
            <Row>
              <H5>{template.title}</H5>
              <Row className="gap-2 text-xs text-white">
                <Clock size={16} /> {template.duration}, {template.wordCount}
              </Row>
            </Row>
            <Text variant="xs" className="text-brand-secondary">
              {template.description}
            </Text>
          </Col>
        ))}
      </div>
    </Col>
  );
}

const templates = [
  {
    id: 'short',
    title: 'Short',
    duration: '~20 m',
    wordCount: '2.6k-3k words',
    description: 'Great for concise explainers or presentations',
  },
  {
    id: 'medium',
    title: 'Medium',
    duration: '~40 m',
    wordCount: '5.2k-6k words',
    description: 'Ideal for in-depth videos, product demos, interviews',
  },
  {
    id: 'long',
    title: 'Long',
    duration: '~60 m',
    wordCount: '7.8k-9k words',
    description: 'Best for comprehensive tutorials, webinars, lectures',
  },
  {
    id: 'flexible-outline',
    title: 'Flexible Outline',
    duration: 'Flexible',
    wordCount: '100-300 words',
    description: 'High-level structure without full script',
  },
];
