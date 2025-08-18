import React from "react";

const WhatsInside = () => {
  return (
    <section className="bg-black text-white py-20 px-6 md:px-16">
      {/* Heading */}
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold">What’s inside</h2>
        <p className="text-[#AAACA6] mt-3">
          A quick look at the tools that help you go from idea to ready-to-post script.
        </p>
      </div>

      <div className="min-h-screen bg-black flex items-center justify-center px-6 py-12">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl w-full">
        
        {/* Script Generator */}
        <div className="bg-[#0f0f0f] rounded-2xl shadow-lg p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-300 mb-4">Choose a template style</h2>
            <div className="grid grid-cols-2 gap-3 mb-6">
              <button className="bg-black border border-gray-700 rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                <p className="font-medium">Short</p>
                <p className="text-xs text-gray-400">60s – 2:45s ≈ 85 words</p>
              </button>
              <button className="bg-black border border-gray-700 rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                <p className="font-medium">Medium</p>
                <p className="text-xs text-gray-400">40s – 5:30s ≈ 95–120 words</p>
              </button>
              <button className="bg-black border border-gray-700 rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                <p className="font-medium">Long</p>
                <p className="text-xs text-gray-400">Ideal for tutorials ≈ 140+ words</p>
              </button>
              <button className="bg-black border border-gray-700 rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                <p className="font-medium">Flexible Outline</p>
                <p className="text-xs text-gray-400">Flexible 100–200 words</p>
              </button>
            </div>

            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-300 text-sm">Script length & duration</p>
              <div className="w-12 h-6 bg-green-500 rounded-full relative">
                <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5"></div>
              </div>
            </div>

            <h3 className="text-xl font-bold text-white mb-2">Script Generator</h3>
            <p className="text-gray-400 text-sm mb-6">
              AI writes full YouTube scripts based on your idea.
            </p>
          </div>
          <button className="text-sm text-white bg-white/10 px-5 py-2 rounded-lg hover:bg-white/20 transition">
            Try now →
          </button>
        </div>

        {/* Title Optimizer */}
        <div className="bg-[#0f0f0f] rounded-2xl shadow-lg p-6 flex flex-col justify-between">
          <div>
            <ul className="space-y-2 text-sm text-gray-300 mb-6">
              <li>🏆 <span className="text-white">Milestone unlocked:</span> $500 in commissions!</li>
              <li>💰 <span className="text-white">New commission earned!</span> You just earned $25 from a new referral.</li>
            </ul>

            <h3 className="text-xl font-bold text-white mb-2">Title Optimizer</h3>
            <p className="text-gray-400 text-sm mb-6">
              Get viral, high-CTR titles — created or improved by AI.
            </p>
          </div>
          <button className="text-sm text-white bg-white/10 px-5 py-2 rounded-lg hover:bg-white/20 transition">
            Try now →
          </button>
        </div>

      </div>
    </div>
    </section>
  );
};

export default WhatsInside;