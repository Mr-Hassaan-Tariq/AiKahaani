const WhatsInside = () => {
  return (
    <section className="bg-black px-6 pt-20 text-white md:px-16">
      {/* Heading */}
      <div className="mb-16 text-center">
        <h2 className="text-3xl font-bold md:text-4xl">What’s inside</h2>
        <p className="mt-3 text-[#AAACA6]">
          A quick look at the tools that help you go from idea to ready-to-post script.
        </p>
      </div>

      <div className="flex min-h-screen items-center justify-center bg-black px-6 py-12">
        <div className="grid w-full max-w-6xl grid-cols-1 gap-6 md:grid-cols-2">
          {/* Script Generator */}
          <div className="flex flex-col justify-between rounded-2xl bg-[#0f0f0f] p-6 shadow-lg">
            <div>
              <h2 className="mb-4 text-lg font-semibold text-gray-300">Choose a template style</h2>
              <div className="mb-6 grid grid-cols-2 gap-3">
                <button className="rounded-xl border border-gray-700 bg-black p-4 text-sm text-gray-200 hover:border-gray-500">
                  <p className="font-medium">Short</p>
                  <p className="text-xs text-gray-400">60s – 2:45s ≈ 85 words</p>
                </button>
                <button className="rounded-xl border border-gray-700 bg-black p-4 text-sm text-gray-200 hover:border-gray-500">
                  <p className="font-medium">Medium</p>
                  <p className="text-xs text-gray-400">40s – 5:30s ≈ 95–120 words</p>
                </button>
                <button className="rounded-xl border border-gray-700 bg-black p-4 text-sm text-gray-200 hover:border-gray-500">
                  <p className="font-medium">Long</p>
                  <p className="text-xs text-gray-400">Ideal for tutorials ≈ 140+ words</p>
                </button>
                <button className="rounded-xl border border-gray-700 bg-black p-4 text-sm text-gray-200 hover:border-gray-500">
                  <p className="font-medium">Flexible Outline</p>
                  <p className="text-xs text-gray-400">Flexible 100–200 words</p>
                </button>
              </div>

              <div className="mb-6 flex items-center justify-between">
                <p className="text-sm text-gray-300">Script length & duration</p>
                <div className="relative h-6 w-12 rounded-full bg-green-500">
                  <div className="absolute right-0.5 top-0.5 h-5 w-5 rounded-full bg-white"></div>
                </div>
              </div>

              <h3 className="mb-2 text-xl font-bold text-white">Script Generator</h3>
              <p className="mb-6 text-sm text-gray-400">
                AI writes full YouTube scripts based on your idea.
              </p>
            </div>
            <button className="rounded-lg bg-white/10 px-5 py-2 text-sm text-white transition hover:bg-white/20">
              Try now →
            </button>
          </div>

          {/* Title Optimizer */}
          <div className="flex flex-col justify-between rounded-2xl bg-[#0f0f0f] p-6 shadow-lg">
            <div>
              <ul className="mb-6 space-y-2 text-sm text-gray-300">
                <li>
                  🏆 <span className="text-white">Milestone unlocked:</span> $500 in commissions!
                </li>
                <li>
                  💰 <span className="text-white">New commission earned!</span> You just earned $25
                  from a new referral.
                </li>
              </ul>

              <h3 className="mb-2 text-xl font-bold text-white">Title Optimizer</h3>
              <p className="mb-6 text-sm text-gray-400">
                Get viral, high-CTR titles — created or improved by AI.
              </p>
            </div>
            <button className="rounded-lg bg-white/10 px-5 py-2 text-sm text-white transition hover:bg-white/20">
              Try now →
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhatsInside;
