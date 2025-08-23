import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

import { WEB_APP_URL } from '../../lib/constants';
import { heroSectionContent } from '../../lib/localData';

export default function HeroSection({ page }: { page: 'home' | 'partner' | 'affiliates' }) {
  return (
    <section className="flex flex-col items-center justify-between py-12 text-white md:flex-row">
      {/* Left Side */}
      <div className="max-w-lg space-y-6">
        <span className="flex w-fit items-center gap-2 rounded-full bg-[#292A27] px-3 py-1 text-sm">
          <Image src="/images/magicpen.svg" alt="idea" width={20} height={20} />
          {heroSectionContent[page].label}
        </span>
        <h1 className="text-4xl font-bold leading-tight">{heroSectionContent[page].title}</h1>
        <p className="text-[#AAACA6]">{heroSectionContent[page].description}</p>
        <div className="flex items-center justify-center sm:flex sm:items-center sm:justify-center">
          <Link href={`${WEB_APP_URL}/signup`} target="_blank">
            <button
              className="flex items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black"
              style={{ fontWeight: '600' }}
            >
              {heroSectionContent[page].btnLabel}
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
                <ArrowRight size={20} />
              </span>
            </button>
          </Link>
        </div>
      </div>

      {/* Right Side */}
      <div className="hidden sm:block">{heroSectionContent[page].rightSection}</div>
    </section>
  );
}
