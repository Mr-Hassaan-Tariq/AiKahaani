import type { Metadata } from 'next';

import { LegalLayout, P, UL, type LegalSection } from 'components/legal/LegalLayout';

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description:
    'How AIKahaani, operated by BinaryBursts, collects, uses, stores, and protects your personal data, and the rights you have under GDPR.',
  alternates: { canonical: '/privacy' },
};

const LAST_UPDATED = 'June 28, 2026';

const sections: LegalSection[] = [
  {
    id: 'overview',
    heading: '1. Overview',
    content: (
      <P>
        This Privacy Policy explains how BinaryBursts (&ldquo;we&rdquo;, &ldquo;us&rdquo;,
        &ldquo;our&rdquo;), the operator of AIKahaani, collects and processes your personal data when
        you use https://aikahaani.com. We act as the data controller for the personal data described
        below and are committed to handling it in line with the EU General Data Protection Regulation
        (GDPR) and other applicable privacy laws.
      </P>
    ),
  },
  {
    id: 'information-we-collect',
    heading: '2. Information We Collect',
    content: (
      <>
        <P>We collect the following categories of data:</P>
        <UL
          items={[
            <>
              <strong className="text-gray-900 dark:text-white">Name</strong> &mdash; provided when
              you register or contact us.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">Email address</strong> &mdash; used
              for your account, communication, and receipts.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">Account information</strong> &mdash;
              profile details, plan, preferences, and content you generate.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">Usage analytics</strong> &mdash;
              pages visited, features used, and interactions with the Service.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">Cookies</strong> &mdash; small files
              used for authentication, preferences, and analytics.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">Device information</strong> &mdash;
              browser type, operating system, IP address, and similar technical data.
            </>,
          ]}
        />
        <P>
          Payment card details are <strong>not</strong> collected or stored by us. Payments are
          handled by Paddle, which processes your payment information directly.
        </P>
      </>
    ),
  },
  {
    id: 'how-we-use',
    heading: '3. Why We Collect Your Data',
    content: (
      <>
        <P>We use your data to:</P>
        <UL
          items={[
            'Provide, operate, and maintain the Service.',
            'Create and manage your account and subscription.',
            'Process payments and send receipts through Paddle.',
            'Respond to support requests and communicate service updates.',
            'Improve features, performance, and user experience.',
            'Detect, prevent, and address fraud, abuse, and security issues.',
            'Comply with legal and regulatory obligations.',
          ]}
        />
      </>
    ),
  },
  {
    id: 'legal-basis',
    heading: '4. Legal Basis for Processing (GDPR)',
    content: (
      <>
        <P>Where GDPR applies, we rely on the following legal bases:</P>
        <UL
          items={[
            'Performance of a contract — to provide the Service you signed up for.',
            'Legitimate interests — to secure, analyze, and improve the Service.',
            'Consent — for optional analytics and marketing cookies, where required.',
            'Legal obligation — to meet tax, accounting, and regulatory requirements.',
          ]}
        />
      </>
    ),
  },
  {
    id: 'cookies',
    heading: '5. Cookies and Tracking',
    content: (
      <P>
        We use essential cookies to keep you signed in and remember preferences, and optional
        analytics cookies to understand how the Service is used. Where required, we ask for your
        consent before setting non-essential cookies. You can control or delete cookies through your
        browser settings; disabling essential cookies may affect functionality.
      </P>
    ),
  },
  {
    id: 'third-party',
    heading: '6. Third-Party Services',
    content: (
      <>
        <P>We share limited data with trusted processors who help us run the Service:</P>
        <UL
          items={[
            <>
              <strong className="text-gray-900 dark:text-white">Paddle</strong> &mdash; our Merchant
              of Record for payments, billing, invoicing, and tax. Paddle processes your payment and
              billing details under its own privacy policy.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">Google Analytics</strong> (if
              enabled) &mdash; aggregated usage analytics to improve the Service.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">
                Authentication providers (e.g. Google / Auth0)
              </strong>{' '}
              &mdash; to enable secure sign-in where you choose to use them.
            </>,
            <>
              <strong className="text-gray-900 dark:text-white">AI model providers</strong> &mdash;
              to process your inputs and generate content.
            </>,
          ]}
        />
        <P>
          These providers may process data outside your country. Where this involves transfers from
          the EEA/UK, we rely on appropriate safeguards such as Standard Contractual Clauses.
        </P>
      </>
    ),
  },
  {
    id: 'storage',
    heading: '7. How Your Data Is Stored',
    content: (
      <P>
        We store data on secure cloud infrastructure and apply technical and organizational measures
        such as encryption in transit, access controls, and regular security reviews. While no system
        is completely secure, we work to protect your data against unauthorized access, loss, or
        misuse.
      </P>
    ),
  },
  {
    id: 'retention',
    heading: '8. Data Retention',
    content: (
      <P>
        We keep personal data only as long as needed to provide the Service and meet legal
        obligations. Account data is retained while your account is active and for a reasonable
        period afterward; billing records are retained as required by tax and accounting law. You may
        request deletion of your data at any time, subject to these obligations.
      </P>
    ),
  },
  {
    id: 'your-rights',
    heading: '9. Your Rights',
    content: (
      <>
        <P>Depending on your location, you may have the right to:</P>
        <UL
          items={[
            'Access the personal data we hold about you.',
            'Correct inaccurate or incomplete data.',
            'Request deletion of your data (the right to be forgotten).',
            'Restrict or object to certain processing.',
            'Receive your data in a portable format.',
            'Withdraw consent at any time, where processing is based on consent.',
            'Lodge a complaint with your local data protection authority.',
          ]}
        />
        <P>
          To exercise any of these rights, contact us at support@aikahaani.com. We will respond
          within the timeframe required by applicable law.
        </P>
      </>
    ),
  },
  {
    id: 'children',
    heading: '10. Children&rsquo;s Privacy',
    content: (
      <P>
        AIKahaani is not directed to children under 16, and we do not knowingly collect their
        personal data. If you believe a child has provided us with personal data, please contact us
        so we can remove it.
      </P>
    ),
  },
  {
    id: 'changes',
    heading: '11. Changes to This Policy',
    content: (
      <P>
        We may update this Privacy Policy from time to time. We will post the updated version on this
        page and revise the &ldquo;Last updated&rdquo; date. Material changes will be communicated
        through the Service or by email where appropriate.
      </P>
    ),
  },
  {
    id: 'contact',
    heading: '12. Contact Information',
    content: (
      <>
        <P>For privacy questions or to exercise your rights, contact:</P>
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
            'Data controller: BinaryBursts',
          ]}
        />
      </>
    ),
  },
];

export default function PrivacyPage() {
  return (
    <LegalLayout
      title="Privacy Policy"
      lastUpdated={LAST_UPDATED}
      intro={
        <P>
          Your privacy matters to us. This policy describes what data AIKahaani collects, why we
          collect it, how we protect it, and the choices and rights you have over your information.
        </P>
      }
      sections={sections}
    />
  );
}
