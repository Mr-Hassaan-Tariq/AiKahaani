import type { Metadata } from 'next';
import Link from 'next/link';

import { Footer, Navbar } from 'components/landing';

export const metadata: Metadata = {
  title: 'Pricing',
  description:
    'AIKahaani pricing is launching soon. Plans for creators and teams will be announced before launch. Contact us for enterprise pricing.',
  alternates: { canonical: '/pricing' },
};

const plans = [
  {
    name: 'Starter',
    tagline: 'For creators getting started.',
    price: 'Coming Soon',
    cta: { label: 'Notify me', href: '/contact' },
    featured: false,
    features: [
      'AI YouTube script generation',
      'Engaging title suggestions',
      'Basic video outlines',
      'Multiple script variations',
    ],
  },
  {
    name: 'Professional',
    tagline: 'For serious and full-time creators.',
    price: 'Coming Soon',
    cta: { label: 'Notify me', href: '/contact' },
    featured: true,
    features: [
      'Everything in Starter',
      'Higher generation limits',
      'Advanced pacing & retention tools',
      'Personalized style profiles',
      'Priority support',
    ],
  },
  {
    name: 'Enterprise',
    tagline: 'For teams, agencies, and studios.',
    price: 'Custom',
    cta: { label: 'Contact Sales', href: '/contact' },
    featured: false,
    features: [
      'Everything in Professional',
      'Team seats & collaboration',
      'Custom usage limits',
      'Dedicated onboarding',
      'Custom invoicing & SLAs',
    ],
  },
];

const faqs = [
  {
    q: 'When will pricing be available?',
    a: 'AIKahaani is currently under active development. Final pricing for all plans will be announced before launch.',
  },
  {
    q: 'Will there be a free tier or trial?',
    a: 'We plan to offer a way to try AIKahaani before committing to a paid plan. Details will be shared at launch.',
  },
  {
    q: 'How are payments handled?',
    a: 'Payments will be processed securely by Paddle, our Merchant of Record, which manages checkout, billing, taxes, and invoicing.',
  },
  {
    q: 'Can I get enterprise or custom pricing?',
    a: 'Yes. If you need team seats, custom limits, or custom invoicing, contact our sales team and we will tailor a plan for you.',
  },
  {
    q: 'Can I cancel anytime?',
    a: 'Yes. Subscriptions can be cancelled at any time, and you keep access until the end of your current billing period. See our Refund Policy for details.',
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-white font-sans transition-colors duration-300 selection:bg-red-500 selection:text-white dark:bg-[#0a0a0a] dark:text-white">
      <Navbar />
      <main className="container mx-auto max-w-7xl px-6 pb-24 pt-32">
        <section className="mx-auto max-w-3xl space-y-5 text-center">
          <span className="inline-block rounded-full bg-red-500/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-red-500">
            Launching soon
          </span>
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-6xl">
            Simple pricing, coming soon
          </h1>
          <p className="text-lg font-medium leading-relaxed text-gray-500 dark:text-gray-400">
            AIKahaani is currently under development. Final pricing will be announced before launch.
            Need a plan for your team today? Contact us for enterprise pricing.
          </p>
        </section>

        <section
          aria-label="Pricing plans"
          className="mt-20 grid gap-8 md:grid-cols-2 lg:grid-cols-3"
        >
          {plans.map((plan) => (
            <article
              key={plan.name}
              className={`flex flex-col rounded-[2rem] border p-8 transition-all ${
                plan.featured
                  ? 'border-red-500 bg-gray-50 shadow-xl dark:bg-white/[0.04]'
                  : 'border-gray-200 bg-gray-50 shadow-sm dark:border-white/5 dark:bg-white/[0.02]'
              }`}
            >
              {plan.featured ? (
                <span className="mb-4 w-fit rounded-full bg-red-500 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-white">
                  Most popular
                </span>
              ) : null}
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{plan.name}</h2>
              <p className="mt-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                {plan.tagline}
              </p>
              <p className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                {plan.price}
              </p>

              <ul className="mt-8 flex-1 space-y-3 text-sm font-medium text-gray-600 dark:text-gray-300">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <span aria-hidden className="mt-0.5 font-bold text-red-500">
                      ✓
                    </span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={plan.cta.href}
                className={`mt-8 inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-bold transition-colors ${
                  plan.featured
                    ? 'bg-red-500 text-white hover:bg-red-600'
                    : 'border border-gray-300 text-gray-900 hover:border-red-500 hover:text-red-500 dark:border-white/10 dark:text-white dark:hover:border-red-500 dark:hover:text-red-500'
                }`}
              >
                {plan.cta.label}
              </Link>
            </article>
          ))}
        </section>

        <section aria-labelledby="pricing-faq" className="mx-auto mt-28 max-w-3xl">
          <h2
            id="pricing-faq"
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
