import Image from 'next/image';

export default function Hero() {
  return (
    <section className="flex flex-col items-center justify-between bg-black px-6 py-12 text-white md:flex-row md:px-16">
      {/* Left Side */}
      <div className="max-w-lg space-y-6">
        <span className="flex w-fit items-center gap-2 rounded-full bg-[#292A27] px-3 py-1 text-sm">
          <Image src="/images/magicpen.svg" alt="idea" width={20} height={20} />
          No sign-up hassle. Just your YouTube idea.
        </span>
        <h1 className="text-4xl font-bold leading-tight">
          Your Genius AI <br /> Assistant for YouTube
        </h1>
        <p className="text-[#AAACA6]">
          Turn your video ideas into ready-to-use scripts,
          <br /> titles, and niche insights — in seconds.
        </p>
        <button
          className="flex items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black"
          style={{ fontWeight: '600' }}
        >
          Get Started
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
            <Image src="/images/arrow_right.svg" alt="arrow_right" width={20} height={20} />
          </span>
        </button>
      </div>

      {/* Right Side */}
      <div className="relative mt-10 w-full rounded-xl bg-[#181916] p-6 text-center shadow-lg transition duration-300 hover:shadow-green-500/30 md:mt-0 md:w-[461px]">
        <h2 className="text-lg">Create Your Script</h2>
        <p className="text-[11px] text-[#9E9E9E]">
          Fill out the details below to generate your YouTube script
        </p>
        <div className="mt-6 space-y-3">
          <div className="h-10 animate-pulse rounded-lg bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
          <div className="h-10 animate-pulse rounded-lg bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
          <div className="h-10 animate-pulse rounded-lg bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
          <div className="h-10 animate-pulse rounded-lg bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
          <div className="h-10 animate-pulse rounded-lg bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
          <div className="h-10 animate-pulse rounded-lg bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
        </div>
        <span className="absolute left-[5%] top-[48%] flex items-center gap-2 text-[11px] sm:left-[20%] md:left-[20%] lg:left-[20%]">
          <Image src="/images/star.svg" alt="idea" width={20} height={20} />
          Analyzing your topic and outlining key points...
        </span>
        <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-full bg-green-500 bg-gradient-to-r from-[#20BF0E] to-[#26E611] py-3 text-sm font-medium text-black transition duration-300 hover:scale-105">
          <Image src="/images/vector.svg" alt="arrow_right" width={20} height={20} />
          Generating your script outline...
        </button>
      </div>
    </section>
  );
}
