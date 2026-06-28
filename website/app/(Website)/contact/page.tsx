import type { Metadata } from 'next';

import { ContactForm } from 'components/contact/ContactForm';
import { Footer, Navbar } from 'components/landing';

export const metadata: Metadata = {
  title: 'Contact',
  description:
    'Get in touch with the AIKahaani team. Email us at support@aikahaani.com or use our contact form. We typically respond within one business day.',
  alternates: { canonical: '/contact' },
};

const faqs = [
  {
    q: 'How quickly will I get a response?',
    a: 'We typically respond to emails and form submissions within one business day.',
  },
  {
    q: 'Where can I get billing or refund help?',
    a: 'Email support@aikahaani.com with your Paddle order reference. See our Refund Policy for what may qualify.',
  },
  {
    q: 'Do you offer enterprise or team plans?',
    a: 'Yes. Mention your team size and needs in your message and we will follow up with custom pricing.',
  },
];

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-white font-sans transition-colors duration-300 selection:bg-red-500 selection:text-white dark:bg-[#0a0a0a] dark:text-white">
      <Navbar />
      <main className="container mx-auto max-w-6xl px-6 pb-24 pt-32">
        <section className="mx-auto max-w-3xl space-y-5 text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-6xl">
            Get in touch
          </h1>
          <p className="text-lg font-medium leading-relaxed text-gray-500 dark:text-gray-400">
            Have a question, need support, or want enterprise pricing? We&rsquo;d love to hear from
            you.
          </p>
        </section>

        <div className="mt-16 grid gap-12 lg:grid-cols-[1fr_1.4fr]">
          <aside className="space-y-8">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-widest text-gray-400">Email</h2>
              <a
                href="mailto:support@aikahaani.com"
                className="mt-2 block text-lg font-bold text-red-500 hover:underline"
              >
                support@aikahaani.com
              </a>
            </div>
            <div>
              <h2 className="text-xs font-bold uppercase tracking-widest text-gray-400">
                Business hours
              </h2>
              <p className="mt-2 font-medium text-gray-600 dark:text-gray-300">
                Monday &ndash; Friday
                <br />
                9:00 AM &ndash; 6:00 PM (GMT)
              </p>
            </div>
            <div>
              <h2 className="text-xs font-bold uppercase tracking-widest text-gray-400">
                Response time
              </h2>
              <p className="mt-2 font-medium text-gray-600 dark:text-gray-300">
                We typically reply within one business day.
              </p>
            </div>
          </aside>

          <section
            aria-label="Contact form"
            className="rounded-[2rem] border border-gray-200 bg-gray-50 p-8 shadow-sm dark:border-white/5 dark:bg-white/[0.02]"
          >
            <ContactForm />
          </section>
        </div>

        <section aria-labelledby="contact-faq" className="mx-auto mt-28 max-w-3xl">
          <h2
            id="contact-faq"
            className="text-center text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-4xl"
          >
            Frequently asked questions
          </h2>
          <div className="mt-12 space-y-4">
            {faqs.map((faq) => (
              <details
                key={faq.q}
                className="group rounded-2xl border border-gray-200 bg-gray-50 px-6 open:shadow-sm dark:border-white/5 dark:bg-white/[0.02]"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between py-5 text-lg font-bold text-gray-900 dark:text-white">
                  {faq.q}
                  <span
                    aria-hidden
                    className="ml-4 text-red-500 transition-transform group-open:rotate-45"
                  >
                    +
                  </span>
                </summary>
                <p className="pb-5 font-medium leading-relaxed text-gray-500 dark:text-gray-400">
                  {faq.a}
                </p>
              </details>
            ))}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
