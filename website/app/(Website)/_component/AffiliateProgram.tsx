import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

import Col from 'components/ui/Col';
import Text from 'components/ui/Text';

export default function AffiliateProgram({ id }: { id?: string }) {
  return (
    <section
      id={id}
      className="container relative mx-auto overflow-hidden bg-black px-4 pt-20 text-center text-white md:px-12 lg:pt-40"
    >
      <Col
        className="relative w-full gap-6 overflow-hidden rounded-[32px] border border-brand-green/[32%] bg-brand-black lg:flex-row lg:items-center lg:justify-between"
        // style={{
        //   backgroundImage: `
        //     linear-gradient(to right, rgba(43, 255, 19, 0.02), transparent),
        //     linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        //     linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
        //   `,
        //   backgroundSize: '100% 100%, 40px 40px, 40px 40px',
        // }}

        style={{
          backgroundImage: "url('/images/offer-bg.png')",
          backgroundSize: '100% 100%',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          objectFit: 'cover',
        }}
      >
        <Col className="my-8 flex w-full flex-col items-center gap-8 lg:my-0 lg:my-16 lg:items-start lg:pl-16">
          <Col className="max-w-[300px] gap-4 text-center lg:max-w-[415px] lg:text-left">
            <Text className="text-3xl lg:text-5xl">Get paid to share videoScript</Text>
            <Text variant="xl" className="text-[#AAACA6]">
              Join our affiliate program and earn 50% lifetime commission for every user you bring.
            </Text>
          </Col>
          <Link href="/affiliates">
            <button
              className="flex w-fit items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black active:scale-95"
              style={{ fontWeight: '600' }}
            >
              Learn more
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
                <ArrowRight size={20} />
              </span>
            </button>
          </Link>
        </Col>

        <Image
          alt="affiliate-program"
          src="/images/affiliate-program.jpg"
          width={500}
          height={500}
          className="/* mobile: no top radius */ /* apply top radius only from sm+ */ h-[408px] w-full rounded-t-none bg-white object-cover sm:rounded-t-[32px] lg:rounded-r-[32px] lg:rounded-t-none"
        />
      </Col>
    </section>
  );
}
