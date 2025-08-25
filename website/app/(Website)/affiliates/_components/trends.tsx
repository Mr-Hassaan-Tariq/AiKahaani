'use client';

const audience = [
  'YouTube Creators',
  'Marketing Experts',
  'Tech influencers',
  'Niche bloggers',
  'Tool review channels',
  'SaaS Partners',
];

export default function Trends({ id }: { id?: string }) {
  return (
    <div id={id} className="rotated-bg relative py-10 pb-60">
      <div className="relative flex items-center justify-center overflow-hidden bg-black pb-40 pt-10 text-white">
        <img src="/svg/top-right-gid.svg" alt="grid" className="absolute right-0 top-0" />

        <div className="absolute bottom-10 left-0 h-32 w-full rotate-180 bg-gradient-to-t from-black to-transparent" />
        <div className="relative z-10 w-full max-w-4xl px-4 text-center">
          {/* Heading */}
          <h2 className="mb-3 text-3xl font-semibold md:text-4xl">Is it for you?</h2>
          <p className="mx-auto mb-10 max-w-2xl text-gray-400">
            Whether you create content, review tools, or influence trends — you can earn recurring
            income with TubeGenius.
          </p>

          {/* Grid */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3">
            {audience.map((item, index) => (
              <div
                key={index}
                className="flex items-center justify-center rounded-xl border border-[#1f1f1f] bg-[#101310] px-6 py-4"
              >
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
