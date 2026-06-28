import type { Metadata } from 'next';

import { LegalLayout, P, UL, type LegalSection } from 'components/legal/LegalLayout';

export const metadata: Metadata = {
  title: 'Refund Policy',
  description:
    'AIKahaani refund policy: how subscription refunds work, when they may apply, and how to request one. Payments are processed by Paddle.',
  alternates: { canonical: '/refund' },
};

const LAST_UPDATED = 'June 28, 2026';

const sections: LegalSection[] = [
  {
    id: 'overview',
    heading: '1. Overview',
    content: (
      <P>
        This Refund Policy explains when and how you may be eligible for a refund on AIKahaani
        subscriptions operated by BinaryBursts. It applies alongside our Terms of Service. Payments
        and refunds are processed by Paddle, our Merchant of Record.
      </P>
    ),
  },
  {
    id: 'general',
    heading: '2. General Policy',
    content: (
      <P>
        Subscription payments are generally <strong>non-refundable</strong>, except where a refund is
        required by applicable law (for example, statutory consumer or cancellation rights). Because
        you can evaluate the Service before subscribing, fees already paid for a billing period are
        not automatically refunded when you cancel.
      </P>
    ),
  },
  {
    id: 'eligibility',
    heading: '3. When Refunds May Apply',
    content: (
      <>
        <P>We review refund requests individually. A refund may be granted where, for example:</P>
        <UL
          items={[
            'You are entitled to a refund under mandatory consumer protection law in your country.',
            'You were charged in error or billed more than once for the same period.',
            'A verified technical fault prevented you from using the Service and we could not resolve it.',
          ]}
        />
        <P>
          Approved refunds are issued to the original payment method through Paddle and may take a few
          business days to appear.
        </P>
      </>
    ),
  },
  {
    id: 'technical-issues',
    heading: '4. Technical Issues',
    content: (
      <P>
        If a technical problem on our side prevents you from using a feature you paid for, please
        contact support first so we can investigate and try to fix it. If we are unable to resolve a
        significant, verifiable issue within a reasonable time, you may qualify for a partial or full
        refund for the affected period.
      </P>
    ),
  },
  {
    id: 'how-to-request',
    heading: '5. How to Request a Refund',
    content: (
      <>
        <P>To request a refund, contact us with the details below:</P>
        <UL
          items={[
            <>
              Email{' '}
              <a className="text-red-500 hover:underline" href="mailto:support@aikahaani.com">
                support@aikahaani.com
              </a>{' '}
              from the address on your account.
            </>,
            'Include your order or invoice reference from your Paddle receipt.',
            'Describe the reason for your request and any relevant details.',
          ]}
        />
        <P>
          We aim to acknowledge refund requests within 2 business days and to reach a decision
          promptly after reviewing the details.
        </P>
      </>
    ),
  },
  {
    id: 'cancellation',
    heading: '6. Cancelling Your Subscription',
    content: (
      <P>
        You can cancel at any time from your account settings or via the management link in your
        Paddle receipt. Cancellation stops future renewals, and you keep access until the end of the
        current paid period. Cancelling does not by itself trigger a refund for the current period
        unless one is required under this policy or by law.
      </P>
    ),
  },
  {
    id: 'payment-processor',
    heading: '7. Payments and Paddle',
    content: (
      <P>
        All payments, billing, and refunds for AIKahaani are handled by Paddle as our Merchant of
        Record. When a refund is approved, Paddle processes it back to your original payment method.
        Your purchase is also subject to Paddle&rsquo;s buyer terms.
      </P>
    ),
  },
  {
    id: 'contact',
    heading: '8. Contact',
    content: (
      <>
        <P>Questions about refunds or billing?</P>
        <UL
          items={[
            <>
              Email:{' '}
              <a className="text-red-500 hover:underline" href="mailto:support@aikahaani.com">
                support@aikahaani.com
              </a>
            </>,
            <>
              Website:{' '}
              <a className="text-red-500 hover:underline" href="https://aikahaani.com">
                https://aikahaani.com
              </a>
            </>,
            'Operated by: BinaryBursts',
          ]}
        />
      </>
    ),
  },
];

export default function RefundPage() {
  return (
    <LegalLayout
      title="Refund Policy"
      lastUpdated={LAST_UPDATED}
      intro={
        <P>
          We want you to be satisfied with AIKahaani. This policy explains how refunds work for our
          subscriptions and how to reach us if something isn&rsquo;t right.
        </P>
      }
      sections={sections}
    />
  );
}
