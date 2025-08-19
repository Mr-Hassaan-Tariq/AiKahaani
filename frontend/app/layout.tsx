import '../styles/globals.css';

import { Figtree } from 'next/font/google';

import ReactQueryProvider from 'lib/reactQuery/ReactQueryProvider';

const FIGTREE = Figtree({
  variable: '--figtree-font',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
});

export const metadata = {
  title: 'Tubegenius',
  description:
    "Longevity at the palm of your hand. Access to leading specialists, cutting edge therapies, and the highest quality of care, all available on the Geviti platform. Whether it's TRT, peptide therapy, or nutritional advice, we have you covered. All practices backed by science. Go Geviti, and live a longer, healthier life.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${FIGTREE.variable} font-figtree`}>
        <ReactQueryProvider>{children}</ReactQueryProvider>
      </body>
    </html>
  );
}
