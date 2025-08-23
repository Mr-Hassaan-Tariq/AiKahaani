import { ArrowRight } from "lucide-react";

export default function OfferSection() {
  return (
    <div className="bg-black px-6 md:px-20 pb-20">
      <div
        className="w-full text-center p-16 bg-cover bg-center flex flex-col items-center "
        style={{
          backgroundImage: "url('/images/offer-bg.png')",
          backgroundSize: "100% 100%",
          backgroundPosition: "center",
        }}
      >
        <p className="w-fit gap-2 rounded-full bg-[#292A27] px-3 py-1 text-sm text-white">
          Cancel anytime — no commitments
        </p>

        <h2 className="relative text-2xl md:text-4xl text-white mt-8">
          Limited-Time Launch Offer
        </h2>

        <p className="relative z-10 text-[#a9ada5] text-[14px] mt-4 mb-6">
          Try TubeGenius free for 7 days. No credit card required.
        </p>

        <button
          className="flex items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black mt-2"
          style={{ fontWeight: "600" }}
        >
          Get Started
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
            <ArrowRight size={20} />
          </span>
        </button>
      </div>
    </div>
  );
}
