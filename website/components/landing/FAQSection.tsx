'use client';

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../../components/shadcn_ui/accordion';

const faqs = [
  {
    q: 'Can I generate scripts for different languages?',
    a: 'Yes! videoScript supports over 50 languages. Our AI is trained on global YouTube data, so it understands local context and slang as well.',
  },
  {
    q: 'How does the pacing engine work?',
    a: 'Our engine analyzes retention patterns from millions of successful videos. It inserts pattern interrupts, transitions, and calls-to-action at the exact moments viewers typically drop off.',
  },
  {
    q: 'Is it really different from using ChatGPT?',
    a: 'Absolutely. While ChatGPT is generic, videoScript is fine-tuned specifically for YouTube. It includes niche topic discovery, viral hook frameworks, and storyboard generation that generic LLMs fail at.',
  },
  {
    q: 'Can I save my custom voice/style?',
    a: 'Yes, you can upload your previous successful scripts to train your personalized style profile, ensuring every generated script sounds exactly like you.',
  },
];

export function FAQSection() {
  return (
    <section
      id="faq"
      className="bg-white px-6 py-24 transition-colors duration-300 dark:bg-[#0a0a0a]"
    >
      <div className="container mx-auto max-w-4xl space-y-20 text-center">
        <div className="space-y-4">
          <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-5xl">
            Frequently asked questions
          </h2>
          <p className="text-lg font-medium text-gray-500 dark:text-gray-400">
            Everything you need to know about videoScript
          </p>
        </div>

        <div className="text-left">
          <Accordion type="single" collapsible className="w-full space-y-6">
            {faqs.map((faq, i) => (
              <AccordionItem
                key={faq.q}
                value={`item-${i}`}
                className="rounded-[2rem] border border-gray-200 bg-gray-50 px-8 shadow-sm transition-all hover:bg-gray-100 dark:border-white/5 dark:bg-white/[0.02] dark:hover:bg-white/[0.04]"
              >
                <AccordionTrigger className="py-8 text-gray-900 hover:no-underline dark:text-white">
                  <span className="text-left text-xl font-bold">{faq.q}</span>
                </AccordionTrigger>
                <AccordionContent className="pb-8 text-lg font-medium leading-relaxed text-gray-500 dark:text-gray-400">
                  {faq.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  );
}
