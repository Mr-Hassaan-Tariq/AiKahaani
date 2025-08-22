import Image from 'next/image';

import Col from 'components/ui/Col';
import Text from 'components/ui/Text';

export default function HowItWorks({ id }: { id?: string }) {
  return (
    <section id={id} className="py-20 text-center text-white">
      {/* Heading */}
      <Col className="mb-16 gap-4">
        <div className="mx-auto max-w-xl text-center">
          <Text variant="5xl" className="text-white">
            How it works
          </Text>
        </div>
        <Text variant="lg" className="mx-auto max-w-2xl text-center text-[#AAACA6]">
          Create your next YouTube video in 3 simple steps.
        </Text>
      </Col>

      {/* Steps */}
      <div className="relative flex flex-col items-center justify-between gap-10 lg:flex-row lg:items-start">
        {/* Step 1 */}
        <div className="mt-5 flex h-auto w-[330px] flex-col items-center rounded-2xl border-[1px] border-[var(--Stroke-Surface,#BAFF381F)] bg-[#171a16] p-8 text-center shadow-lg lg:h-[250px]">
          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-[#20BF0E] to-[#26E611] text-lg font-bold text-black">
            1
          </div>
          <h3 className="mb-3 text-xl font-semibold">Enter your topic</h3>
          <p className="text-sm leading-relaxed text-gray-400">
            Just type the idea of your future video or niche — we’ll take it from there.
          </p>
        </div>
        <div className="absolute left-[28%] top-[43%] hidden justify-center lg:flex">
          <Image src="/images/Vector1.svg" alt="step1" width={90} height={100} />
        </div>
        {/* Step 2 */}
        <div className="mt-5 flex h-auto w-[330px] flex-col items-center rounded-2xl border-[1px] border-[var(--Stroke-Surface,#BAFF381F)] bg-[#171a16] p-8 text-center shadow-lg lg:h-[300px]">
          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-[#20BF0E] to-[#26E611] text-lg font-bold text-black">
            2
          </div>
          <h3 className="mb-3 text-xl font-semibold">Pick your style</h3>
          <p className="text-sm leading-relaxed text-gray-400">
            Choose a channel template (e.g. travel, commentary, lifestyle…) to match tone and
            structure.
          </p>
        </div>
        <div className="absolute right-[28%] top-[43%] hidden justify-center lg:flex">
          <Image src="/images/Vector1.svg" alt="step1" width={90} height={100} />
        </div>
        {/* Step 3 */}
        <div className="flex h-auto w-[330px] flex-col items-center rounded-2xl border-[1px] border-[var(--Stroke-Surface,#BAFF381F)] bg-[#171a16] p-8 text-center shadow-lg lg:h-[300px]">
          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-[#20BF0E] to-[#26E611] text-lg font-bold text-black">
            3
          </div>
          <h3 className="mb-3 text-xl font-semibold">Get your video script</h3>
          <p className="text-sm leading-relaxed text-gray-400">
            Receive a complete, ready-to-use script with title, outline, and niche-tailored
            suggestions.
          </p>
        </div>
      </div>
    </section>
  );
}
