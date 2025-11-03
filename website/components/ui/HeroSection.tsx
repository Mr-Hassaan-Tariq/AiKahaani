import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

import { WEB_APP_URL } from '../../lib/constants';
import { heroSectionContent } from '../../lib/localData';

export default function HeroSection({ page }: { page: 'home' | 'partner' | 'affiliates' }) {
  return (
    <div className="relative">
      <section className="container relative mx-auto flex flex-col items-center justify-between px-8 py-12 py-8 text-white md:flex-row md:px-12">
        {/* Left Side */}
        <div className="flex max-w-lg flex-col items-center space-y-6 lg:items-start">
          <span className="flex w-fit items-center gap-2 rounded-full bg-[#292A27] px-3 py-1 text-sm">
            <Image src="/images/magicpen.svg" alt="idea" width={20} height={20} />
            {heroSectionContent[page].label}
          </span>
          <h1 className="text-center text-4xl font-bold leading-tight lg:text-left">
            {heroSectionContent[page].title}
          </h1>
          <p className="text-center text-[#AAACA6] lg:text-left">
            {heroSectionContent[page].description}
          </p>
          <div className="flex items-center justify-center lg:items-start lg:justify-start">
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
    </div>
  );
}
