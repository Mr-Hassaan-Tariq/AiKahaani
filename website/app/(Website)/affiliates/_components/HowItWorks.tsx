import Image from 'next/image';

export default function HowItWorks({ id }: { id: string }) {
  return (
    <section id={id} className="bg-black py-20 text-center text-white">
      {/* Heading */}
      <div className="mb-16">
        <h2 className="text-3xl font-bold md:text-4xl">How it works</h2>
        <p className="mt-3 text-[#AAACA6]">
          Getting started takes minutes — earning starts right away.
        </p>
      </div>

      {/* Steps */}
      <div className="flex flex-col items-center gap-10 lg:flex-row lg:items-start">
        {/* Step 1 */}
        <div className="mt-5 flex h-auto w-[330px] flex-col items-center rounded-2xl border-[1px] border-[var(--Stroke-Surface,#BAFF381F)] bg-[#171a16] p-8 text-center shadow-lg lg:h-[250px]">
          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-[#20BF0E] to-[#26E611] text-lg font-bold text-black">
            1
          </div>
          <h3 className="mb-3 text-xl font-semibold">Apply</h3>
          <p className="text-sm leading-relaxed text-gray-400">
            Tell us about your channel, <br /> audience or platform
          </p>
        </div>
        {/* Vector 1 */}
        <div className="flex items-center justify-center self-center">
          <Image
            src="/images/Vector1.svg"
            alt="step1"
            width={90}
            height={100}
            className="rotate-90 lg:rotate-0"
          />
        </div>
        {/* Step 2 */}
        <div className="mt-5 flex h-auto w-[330px] flex-col items-center rounded-2xl border-[1px] border-[var(--Stroke-Surface,#BAFF381F)] bg-[#171a16] p-8 text-center shadow-lg lg:h-[240px]">
          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-[#20BF0E] to-[#26E611] text-lg font-bold text-black">
            2
          </div>
          <h3 className="mb-3 text-xl font-semibold">Promote</h3>
          <p className="text-sm leading-relaxed text-gray-400">
            Share your unique <br /> link or promo code
          </p>
        </div>
        {/* Vector 2 */}
        <div className="flex items-center justify-center self-center">
          <Image
            src="/images/Vector1.svg"
            alt="step2"
            width={90}
            height={100}
            className="rotate-90 lg:rotate-0"
          />
        </div>
        {/* Step 3 */}
        <div className="flex h-auto w-[330px] flex-col items-center rounded-2xl border-[1px] border-[var(--Stroke-Surface,#BAFF381F)] bg-[#171a16] p-8 text-center shadow-lg lg:h-[250px]">
          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-[#20BF0E] to-[#26E611] text-lg font-bold text-black">
            3
          </div>
          <h3 className="mb-3 text-xl font-semibold">Earn</h3>
          <p className="text-sm leading-relaxed text-gray-400">
            Get paid for every <br /> successful sign up
          </p>
        </div>
      </div>
    </section>
  );
}
