import Image from "next/image";

export default function HowItWorks() {
    return (
        <section className="bg-black text-white py-20 px-6 md:px-16 text-center">
            {/* Heading */}
            <div className="mb-16">
                <h2 className="text-3xl md:text-4xl font-bold">How it works</h2>
                <p className="text-[#AAACA6] mt-3">
                    Create your next YouTube video in 3 simple steps.
                </p>
            </div>

            {/* Steps */}
            <div className="flex flex-col lg:flex-row justify-between items-center lg:items-start gap-10 relative">
                {/* Step 1 */}
                <div className="bg-[#171a16] rounded-2xl p-8 shadow-lg flex flex-col items-center text-center w-[330px] h-auto lg:h-[250px] mt-5 border-[1px] border-[var(--Stroke-Surface,#BAFF381F)]">
                    <div className="bg-gradient-to-r from-[#20BF0E] to-[#26E611] w-12 h-12 flex items-center justify-center rounded-full text-black font-bold text-lg mb-6">
                        1
                    </div>
                    <h3 className="text-xl font-semibold mb-3">Enter your topic</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Just type the idea of your future video or niche — we’ll take it from there.
                    </p>
                </div>
                <div className="hidden lg:flex justify-center absolute top-[43%] left-[28%]">
                    <Image src="/images/Vector1.svg" alt="step1" width={90} height={100} />
                </div>
                {/* Step 2 */}
                <div className="bg-[#171a16] rounded-2xl p-8 shadow-lg flex flex-col items-center text-center w-[330px] h-auto lg:h-[300px] mt-5 border-[1px] border-[var(--Stroke-Surface,#BAFF381F)]">
                    <div className="bg-gradient-to-r from-[#20BF0E] to-[#26E611] w-12 h-12 flex items-center justify-center rounded-full text-black font-bold text-lg mb-6">
                        2
                    </div>
                    <h3 className="text-xl font-semibold mb-3">Pick your style</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Choose a channel template (e.g. travel, commentary, lifestyle…) to match tone and structure.
                    </p>
                </div>
                <div className="hidden lg:flex justify-center absolute top-[43%] right-[28%]">
                    <Image src="/images/Vector1.svg" alt="step1" width={90} height={100} />
                </div>
                {/* Step 3 */}
                <div className="bg-[#171a16] rounded-2xl p-8 shadow-lg flex flex-col items-center text-center w-[330px] h-auto lg:h-[300px] border-[1px] border-[var(--Stroke-Surface,#BAFF381F)]">
                    <div className="bg-gradient-to-r from-[#20BF0E] to-[#26E611] w-12 h-12 flex items-center justify-center rounded-full text-black font-bold text-lg mb-6">
                        3
                    </div>
                    <h3 className="text-xl font-semibold mb-3">Get your video script</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Receive a complete, ready-to-use script with title, outline, and niche-tailored suggestions.
                    </p>
                </div>
            </div>
        </section>
    );
}
