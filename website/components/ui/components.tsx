import Image from 'next/image';
import { CheckCircle, CreditCard, DollarSign, Gift, Users } from 'lucide-react';

const affiliateNotifications = [
  {
    icon: <CheckCircle className="h-6 w-6 text-green-400" />,
    title: 'Payout processed',
    time: '1h ago',
    description: "We'll let you know the moment your payout is on its way.",
  },
  {
    icon: <DollarSign className="h-6 w-6 text-green-400" />,
    title: 'Minimum payout threshold reached',
    time: '1d ago',
    description: 'Get notified when you’re ready to cash out.',
  },
  {
    icon: <CreditCard className="h-6 w-6 text-green-400" />,
    title: 'Funds deposited to your account',
    time: '2d ago',
    description: 'Your payout has successfully landed in your bank or PayPal account.',
  },
  {
    icon: <Gift className="h-6 w-6 text-green-400" />,
    title: 'New commission earned',
    time: '2d ago',
    description: 'Be the first to know when you’ve made money from a referral.',
  },
  {
    icon: <Users className="h-6 w-6 text-green-400" />,
    title: 'You got your first referral!',
    time: '3d ago',
    description: 'Track your earnings in the Affiliate tab',
  },
];

export const partnerRightSide = (
  <div className="mt-10 flex h-[592.2px] w-full max-w-[546px] flex-shrink-0 flex-col items-center justify-center gap-8 rounded-[32px] border border-[rgba(186,255,56,0.12)] bg-[#181916] p-6 shadow-[inset_-22.09px_-6.18px_37.19px_0_rgba(32,34,31,0.25)] backdrop-blur-[11.2px] md:mt-0" />
);
export const homeRightSide = (
  <div className="relative mt-10 w-full rounded-xl bg-[#181916] p-6 text-center shadow-lg transition duration-300 hover:shadow-green-500/30 md:mt-0 md:w-[461px]">
    <h2 className="text-lg">Create Your Script</h2>
    <p className="text-[11px] text-[#9E9E9E]">
      Fill out the details below to generate your YouTube script
    </p>
    <div className="mt-6 space-y-3">
      {Array.from({ length: 6 }).map((_, ind) => (
        <div
          key={ind}
          className="h-10 animate-pulse rounded-lg bg-gradient-to-r from-[#181916] via-[#292929] to-[#333333]"
        />
      ))}
    </div>
    <span className="absolute left-[5%] top-[48%] flex items-center gap-2 text-[11px] sm:left-[20%] md:left-[20%] lg:left-[20%]">
      <Image src="/images/star.svg" alt="idea" width={20} height={20} className="animate-pulse" />
      Analyzing your topic and outlining key points...
    </span>
    <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-full bg-green-500 bg-gradient-to-r from-[#20BF0E] to-[#26E611] py-3 text-sm font-medium text-black transition duration-300 hover:scale-105">
      <div className="size-4 animate-spin rounded-full border border-black border-t-transparent" />
      Generating your script outline...
    </button>
  </div>
);

export const affiliatesRightSide = (
  <div className="">
    <div className="relative mt-10 w-full rounded-xl bg-[#181916] p-6 shadow-lg transition duration-300 hover:shadow-green-500/30 md:mt-0 md:w-[461px]">
      {affiliateNotifications.map((note, index) => (
        <div
          key={index}
          className="mb-2 flex gap-3 rounded-xl p-4 transition [background:linear-gradient(90deg,#181916_0%,#292929_50%,#333333_100%)] hover:opacity-90"
        >
          <div className="flex-shrink-0">{note.icon}</div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="font-medium text-white">{note.title}</h3>
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <span className="h-2 w-2 rounded-full bg-green-500"></span>
                {note.time}
              </span>
            </div>
            <p className="mt-1 text-[12px] text-gray-400">{note.description}</p>
          </div>
        </div>
      ))}
    </div>
  </div>
);
