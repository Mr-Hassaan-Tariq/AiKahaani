import Image from 'next/image';

import Col from 'components/ui/Col';
import Text from 'components/ui/Text';

export default function AffiliateProgram() {
  return (
    <section className="relative overflow-hidden bg-black px-6 pt-40 text-center text-white md:px-32">
      <Col
        className="relative w-full flex-col-reverse gap-6 overflow-hidden rounded-[32px] border border-brand-green/[32%] bg-brand-black lg:flex-row lg:items-center lg:justify-between"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(43, 255, 19, 0.02), transparent),
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 40px 40px, 40px 40px',
        }}
      >
        <Col className="my-16 w-full gap-8 pl-16 lg:my-0">
          <Col className="max-w-[415px] gap-4 text-left">
            <Text variant="5xl">Get paid to share TubeGenius</Text>
            <Text variant="xl" className="text-[#AAACA6]">
              Join our affiliate program and earn 50% lifetime commission for every user you bring.
            </Text>
          </Col>
          <button
            className="flex w-fit items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black active:scale-95"
            style={{ fontWeight: '600' }}
          >
            Learn more
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
              <Image src="/images/arrow_right.svg" alt="arrow_right" width={20} height={20} />
            </span>
          </button>
        </Col>

        <Image
          alt="affiliate-program"
          src="/images/affiliate-program.jpg"
          width={500}
          height={500}
          className="h-[408px] w-full rounded-t-[32px] bg-white object-cover lg:rounded-r-[32px] lg:rounded-t-none"
        />
      </Col>
    </section>
  );
}
