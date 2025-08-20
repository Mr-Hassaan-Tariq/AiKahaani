'use client';

import { useState } from 'react';
import { Plus } from 'lucide-react';

import { questions } from 'lib/localData';
import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Text from 'components/ui/Text';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from 'components/shadcn_ui/accordion';

export default function QuestionWidget() {
  return (
    <Col className="gap-16 bg-black px-6 font-figtree lg:px-32">
      {/* heading */}
      <Col className="gap-4">
        <div className="mx-auto max-w-xl text-center">
          <Text variant="5xl" className="text-white">
            Got questions?
          </Text>
        </div>
        <Text variant="lg" className="mx-auto max-w-2xl text-center text-[#AAACA6]">
          {"We've got you covered."}
        </Text>
      </Col>
      <div className="mx-auto w-full">
        <AccordionWidget />
      </div>
    </Col>
  );
}

export function AccordionWidget() {
  const [openItem, setOpenItem] = useState(questions[0].id.toString());

  return (
    <Accordion
      type="single"
      collapsible
      className="w-full space-y-4"
      value={openItem}
      onValueChange={setOpenItem}
    >
      {questions.map((question) => (
        <AccordionItem
          key={question.id}
          value={question.id.toString()}
          className={cn(
            'overflow-hidden rounded-[32px] border border-brand-green/10 bg-brand-black p-12',
            openItem === question.id.toString() &&
              'bg-gradient-to-r from-transparent via-brand-green/[0.02] to-brand-green/[0.02]'
          )}
        >
          <AccordionTrigger
            isIcon={false}
            className="py-0 text-left text-white transition-colors hover:no-underline"
          >
            <div className="flex w-full items-center justify-between">
              <Text variant="2xl">{question.question}</Text>
              <div className="ml-auto flex-shrink-0">
                <div
                  className={cn(
                    'flex size-[52px] items-center justify-center rounded-full bg-white/10 transition-all duration-500',
                    openItem === question.id.toString() && 'rotate-45 bg-white'
                  )}
                >
                  <Plus
                    className={cn(
                      'size-6 text-white transition-all duration-500',
                      openItem === question.id.toString() && 'text-brand-black'
                    )}
                  />
                </div>
              </div>
            </div>
          </AccordionTrigger>
          <AccordionContent className="">
            <Text variant="lg" className="text-[#AAACA6]">
              {question.answer}
            </Text>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
