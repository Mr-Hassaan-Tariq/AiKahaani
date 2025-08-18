import Image from "next/image";

export default function Hero() {
    return (
        <section className="flex flex-col md:flex-row justify-between items-center px-6 md:px-16 py-12 bg-black text-white">
            {/* Left Side */}
            <div className="max-w-lg space-y-6">
                <span className="bg-[#292A27] px-3 py-1 flex items-center gap-2 rounded-full text-sm w-fit">
                    <Image src="/images/magicpen.svg" alt="idea" width={20} height={20} />
                    No sign-up hassle. Just your YouTube idea.
                </span>
                <h1 className="text-4xl font-bold leading-tight">
                    Your Genius AI <br /> Assistant for YouTube
                </h1>
                <p className="text-[#AAACA6]">
                    Turn your video ideas into ready-to-use scripts,<br/> titles, and niche insights — in seconds.
                </p>
                <button className="flex items-center gap-2 bg-[#2BFF13] pl-4 rounded-full text-black text-sm" style={{ fontWeight: "600" }}>
                    Get Started
                    <span className="bg-white rounded-full w-10 h-10 flex items-center justify-center"><Image src="/images/arrow_right.svg" alt="arrow_right" width={20} height={20} /></span>
                </button>
            </div>

            {/* Right Side */}
            <div className="mt-10 md:mt-0 bg-[#181916] p-6 rounded-xl w-full md:w-[461px] shadow-lg hover:shadow-green-500/30 transition duration-300 text-center relative">
                <h2 className="text-lg ">Create Your Script</h2>
                <p className="text-[#9E9E9E] text-[11px]">Fill out the details below to generate your YouTube script</p>
                <div className="space-y-3 mt-6">
                    <div className="h-10 rounded-lg animate-pulse bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
                    <div className="h-10 rounded-lg animate-pulse bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
                    <div className="h-10 rounded-lg animate-pulse bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
                    <div className="h-10 rounded-lg animate-pulse bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
                    <div className="h-10 rounded-lg animate-pulse bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
                    <div className="h-10 rounded-lg animate-pulse bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"></div>
                </div>
                <span className="flex items-center gap-2 text-[11px] absolute top-[48%] left-[5%] lg:left-[20%] md:left-[20%] sm:left-[20%]">
                    <Image src="/images/star.svg" alt="idea" width={20} height={20} />
                    Analyzing your topic and outlining key points...
                </span>
                <button className="mt-4 w-full bg-green-500 py-3 rounded-full text-sm font-medium bg-gradient-to-r from-[#20BF0E] to-[#26E611] hover:scale-105 transition duration-300 text-black flex items-center justify-center gap-2">
                    <Image src="/images/vector.svg" alt="arrow_right" width={20} height={20} />
                    Generating your script outline...
                </button>
            </div>
        </section>
    );
}
