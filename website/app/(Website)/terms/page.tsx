import type { Metadata } from 'next';

import { LegalLayout, P, UL, type LegalSection } from 'components/legal/LegalLayout';

export const metadata: Metadata = {
  title: 'Terms of Service',
  description:
    'The terms and conditions that govern your use of AIKahaani, the AI YouTube script and title generator operated by BinaryBursts.',
  alternates: { canonical: '/terms' },
};

const LAST_UPDATED = 'June 28, 2026';

const sections: LegalSection[] = [
  {
    id: 'acceptance',
    heading: '1. Acceptance of Terms',
    content: (
      <>
        <P>
          These Terms of Service (&ldquo;Terms&rdquo;) form a binding agreement between you and
          BinaryBursts (&ldquo;BinaryBursts&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;, or
          &ldquo;our&rdquo;), the operator of AIKahaani (the &ldquo;Service&rdquo;), available at
          https://aikahaani.com.
        </P>
        <P>
          By creating an account, accessing, or using the Service, you confirm that you have read,
          understood, and agree to be bound by these Terms and our Privacy Policy. If you do not
          agree, you must not use the Service.
        </P>
      </>
    ),
  },
  {
    id: 'eligibility',
    heading: '2. Eligibility',
    content: (
      <>
        <P>To use AIKahaani, you must:</P>
        <UL
          items={[
            'Be at least 16 years old, or the age of digital consent in your jurisdiction.',
            'Have the legal capacity to enter into a binding contract.',
            'Not be barred from using the Service under any applicable law.',
          ]}
        />
        <P>
          If you use the Service on behalf of an organization, you represent that you are authorized
          to bind that organization to these Terms.
        </P>
      </>
    ),
  },
  {
    id: 'accounts',
    heading: '3. User Accounts',
    content: (
      <>
        <P>
          Some features require an account. You are responsible for maintaining the confidentiality
          of your login credentials and for all activity that occurs under your account. You agree
          to provide accurate information and to keep it up to date.
        </P>
        <P>
          Notify us promptly at support@aikahaani.com if you suspect any unauthorized use of your
          account. We are not liable for losses resulting from compromised credentials that you
          failed to protect.
        </P>
      </>
    ),
  },
  {
    id: 'subscriptions',
    heading: '4. Subscription Services',
    content: (
      <P>
        AIKahaani may be offered on a free tier and one or more paid subscription plans. The
        features, usage limits, and price of each plan will be described at the point of purchase.
        We may add, modify, or discontinue plans, with reasonable notice for changes that materially
        affect active subscriptions.
      </P>
    ),
  },
  {
    id: 'billing',
    heading: '5. Billing',
    content: (
      <>
        <P>
          Payments for paid plans are processed securely by{' '}
          <strong className="text-gray-900 dark:text-white">Paddle</strong>, which acts as our
          Merchant of Record. Paddle handles checkout, payment processing, billing, tax collection,
          and invoicing. Your purchase is also subject to Paddle&rsquo;s buyer terms.
        </P>
        <P>
          You agree to provide a valid payment method and authorize Paddle to charge the applicable
          fees, including any taxes, for your selected plan. All prices are stated exclusive of taxes
          unless noted otherwise.
        </P>
      </>
    ),
  },
  {
    id: 'renewals',
    heading: '6. Automatic Renewals',
    content: (
      <P>
        Subscriptions renew automatically at the end of each billing cycle (monthly or annually)
        unless cancelled before the renewal date. By subscribing, you authorize recurring charges
        through Paddle at the then-current price for your plan until you cancel. We will provide
        notice before any price increase that applies to your renewal.
      </P>
    ),
  },
  {
    id: 'cancellation',
    heading: '7. Cancellation',
    content: (
      <P>
        You may cancel your subscription at any time from your account settings or via the management
        link in your Paddle receipt. Cancellation stops future renewals; your plan remains active
        until the end of the current paid period. Refunds, where applicable, are governed by our
        Refund Policy.
      </P>
    ),
  },
  {
    id: 'ip',
    heading: '8. Intellectual Property',
    content: (
      <>
        <P>
          The Service, including its software, design, branding, and content (excluding your inputs
          and generated outputs), is owned by BinaryBursts and protected by intellectual property
          laws. We grant you a limited, non-exclusive, non-transferable license to use the Service in
          accordance with these Terms.
        </P>
        <P>
          You retain ownership of the content you submit. Subject to your plan, you own the outputs
          you generate, and you grant us a limited license to process them solely to operate and
          improve the Service.
        </P>
      </>
    ),
  },
  {
    id: 'acceptable-use',
    heading: '9. Acceptable Use',
    content: (
      <P>
        You agree to use AIKahaani only for lawful purposes and in a manner that respects the rights
        of others. You are solely responsible for the content you create with the Service and for
        ensuring it complies with applicable laws and the policies of any platform where you publish
        it.
      </P>
    ),
  },
  {
    id: 'prohibited',
    heading: '10. Prohibited Activities',
    content: (
      <>
        <P>You must not:</P>
        <UL
          items={[
            'Reverse engineer, scrape, or attempt to access the Service outside the provided interfaces.',
            'Generate content that is unlawful, defamatory, hateful, infringing, or sexually exploitative.',
            'Resell, sublicense, or share access to the Service without our written permission.',
            'Interfere with, overload, or disrupt the Service or its infrastructure.',
            'Use the Service to build a competing product or to train competing AI models.',
            'Circumvent usage limits, billing, or access controls.',
          ]}
        />
      </>
    ),
  },
  {
    id: 'third-party',
    heading: '11. Third-Party Services',
    content: (
      <P>
        The Service integrates with third-party providers such as Paddle (payments), analytics
        providers, authentication providers, and AI model providers. Your use of those integrations
        may be subject to the respective provider&rsquo;s terms. We are not responsible for the
        availability, accuracy, or practices of third-party services.
      </P>
    ),
  },
  {
    id: 'ai-content',
    heading: '12. AI-Generated Content Disclaimer',
    content: (
      <>
        <P>
          AIKahaani uses artificial intelligence to generate scripts, titles, outlines, and related
          content. AI output may be inaccurate, incomplete, or unintentionally similar to existing
          material. It does not constitute professional, legal, or financial advice.
        </P>
        <P>
          You are responsible for reviewing, editing, and verifying any generated content before
          using or publishing it, including checking for originality and compliance with the rules of
          your chosen platform.
        </P>
      </>
    ),
  },
  {
    id: 'availability',
    heading: '13. Service Availability',
    content: (
      <P>
        We strive to keep the Service available but do not guarantee uninterrupted or error-free
        operation. The Service may be unavailable during maintenance, updates, or events beyond our
        control. We may modify or discontinue features at any time.
      </P>
    ),
  },
  {
    id: 'warranties',
    heading: '14. Disclaimer of Warranties',
    content: (
      <P>
        The Service is provided &ldquo;as is&rdquo; and &ldquo;as available&rdquo; without warranties
        of any kind, whether express or implied, including warranties of merchantability, fitness for
        a particular purpose, and non-infringement. We do not warrant that the Service will meet your
        requirements or that generated content will achieve any particular result.
      </P>
    ),
  },
  {
    id: 'liability',
    heading: '15. Limitation of Liability',
    content: (
      <P>
        To the maximum extent permitted by law, BinaryBursts shall not be liable for any indirect,
        incidental, special, consequential, or punitive damages, or for any loss of profits, data, or
        goodwill arising from your use of the Service. Our total aggregate liability for any claim
        relating to the Service shall not exceed the amount you paid to us in the twelve months
        preceding the claim.
      </P>
    ),
  },
  {
    id: 'termination',
    heading: '16. Termination',
    content: (
      <P>
        We may suspend or terminate your access if you breach these Terms, misuse the Service, or
        create risk or legal exposure for us. You may stop using the Service at any time. Provisions
        that by their nature should survive termination (including intellectual property, disclaimers,
        and limitation of liability) will continue to apply.
      </P>
    ),
  },
  {
    id: 'contact',
    heading: '17. Contact Information',
    content: (
      <>
        <P>Questions about these Terms? Reach us at:</P>
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

export default function TermsPage() {
  return (
    <LegalLayout
      title="Terms of Service"
      lastUpdated={LAST_UPDATED}
      intro={
        <P>
          Please read these Terms carefully before using AIKahaani. They explain your rights and
          responsibilities when using our AI-powered tools for creating YouTube scripts, titles, and
          outlines.
        </P>
      }
      sections={sections}
    />
  );
}
