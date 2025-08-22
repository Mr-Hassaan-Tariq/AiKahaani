// components/AffiliateBenefits.tsx
import { CreditCard, DollarSign, Gift, Headphones, Monitor } from 'lucide-react';

const benefits = [
  {
    icon: <DollarSign className="h-6 w-6 text-green-400" />,
    title: '30% commission, <br/> recurring for 12 months',
  },
  {
    icon: <Monitor className="h-6 w-6 text-green-400" />,
    title: 'High-converting <br/> landing & tools',
  },
  {
    icon: <CreditCard className="h-6 w-6 text-green-400" />,
    title: 'Monthly payouts via <br/> Stripe or PayPal',
  },
  {
    icon: <Gift className="h-6 w-6 text-green-400" />,
    title: 'Promo codes or custom links',
  },
  {
    icon: <Headphones className="h-6 w-6 text-green-400" />,
    title: 'Priority support',
  },
];

export default function AffiliateBenefits({ id }: { id?: string }) {
  return (
    <section id={id} className="w-full bg-black py-16">
      <div className="mx-auto max-w-5xl text-center">
        {/* Heading */}
        <h2 className="mb-2 text-2xl font-semibold text-white md:text-3xl">
          Why affiliates love TubeGenius
        </h2>
        <p className="mb-12 text-sm text-gray-400 md:text-base">
          We built this program to make it simple (and worth it).
        </p>

        {/* Grid */}
        <div className="grid grid-cols-12 gap-6">
          {benefits.map((item, index) => (
            <div
              key={index}
              className={`col-span-12 ${
                index < 3 ? 'md:col-span-4' : 'md:col-span-6'
              } flex flex-col items-center justify-center gap-4 rounded-2xl border border-[#BAFF381F] p-8 text-center shadow-md [background:linear-gradient(180deg,#181916_0%,#292929_50%,#333333_100%)]`}
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#1c1c1c] shadow-inner">
                {item.icon}
              </div>
              <p
                className="text-sm text-white md:text-base"
                dangerouslySetInnerHTML={{ __html: item.title }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
