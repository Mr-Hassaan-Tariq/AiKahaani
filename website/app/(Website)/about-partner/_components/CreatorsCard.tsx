'use client';

import { FC } from 'react';
import Image from 'next/image';
import { ArrowRight } from 'lucide-react';

const features = [
  {
    icon: '/images/tailored.svg',
    title: 'Tailored for creators',
    desc: 'Focused tools to grow your YouTube faster',
  },
  {
    icon: '/images/exclusive.svg',
    title: 'Exclusive $1 trial',
    desc: 'Full access for a fraction of the cost',
  },
  {
    icon: '/images/proven.svg',
    title: 'Proven results',
    desc: 'Trusted by thousands of creators worldwide',
  },
  {
    icon: '/images/cancel.svg',
    title: 'Cancel anytime',
    desc: 'Zero risk for you, all the rewards',
  },
];

const CreatorsCard: FC<{ id: string }> = ({ id }) => {
  return (
    <section id={id} className="bg-black px-6 py-16 text-white">
      <div className="mx-auto flex max-w-6xl flex-col items-center text-center">
        {/* Heading */}
        <h2 className="mb-2 text-3xl font-bold md:text-4xl">
          Why creators love <span className="text-green-400">TubeGenius</span>
        </h2>
        <p className="mb-12 text-gray-400">
          Helping creators save time, grow audiences, and boost earnings
        </p>

        {/* Features grid */}
        <div className="mb-10 grid grid-cols-1 gap-6 md:grid-cols-4">
          {features.map((item, idx) => (
            <div
              key={idx}
              className="flex flex-col items-center rounded-xl border border-[#222] bg-[#171a16] p-6 text-center transition hover:shadow-lg"
            >
              <Image src={item.icon} alt={item.title} width={60} height={80} className="mb-4" />
              <h3 className="mb-2 text-lg font-semibold">{item.title}</h3>
              <p className="text-sm text-gray-400">{item.desc}</p>
            </div>
          ))}
        </div>

        {/* CTA button */}
        <button
          className="flex w-fit items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black"
          style={{ fontWeight: '600' }}
        >
          Start for $1
          <span className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-white">
            <ArrowRight size={20} />
          </span>
        </button>
      </div>
    </section>
  );
};

export default CreatorsCard;
