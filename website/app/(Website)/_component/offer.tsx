import { ArrowRight } from 'lucide-react';

export default function OfferSection() {
  return (
    <div className="container mx-auto bg-black px-8 py-8 pb-20 md:px-12">
      <div
        className="flex w-full flex-col items-center bg-cover bg-center p-16 text-center"
        style={{
          backgroundImage: "url('/images/offer-bg.png')",
          backgroundSize: '100% 100%',
          backgroundPosition: 'center',
        }}
      >
        <p className="w-fit gap-2 rounded-full bg-[#292A27] px-3 py-1 text-sm text-white">
          Cancel anytime — no commitments
        </p>

        <h2 className="relative mt-8 text-2xl text-white md:text-4xl">Limited-Time Launch Offer</h2>

        <p className="relative z-10 mb-6 mt-4 text-[14px] text-[#a9ada5]">
          Try TubeGenius free for 7 days. No credit card required.
        </p>

        <button
          className="mt-2 flex items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black"
          style={{ fontWeight: '600' }}
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
