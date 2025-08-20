import Image from 'next/image';
import { CheckCircle, CreditCard, DollarSign, Gift, Users } from 'lucide-react';

export default function Hero() {
  const notifications = [
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

  return (
    <section className="flex flex-col items-center justify-between bg-black px-6 py-12 text-white md:flex-row md:px-16">
      {/* Left Side */}
      <div className="max-w-lg space-y-6">
        <span className="flex w-fit items-center gap-2 rounded-full bg-[#292A27] px-3 py-1 text-sm">
          <Image src="/images/magicpen.svg" alt="idea" width={20} height={20} />
          Try TubeGenius for just $1 and start earning today
        </span>
        <h1 className="text-4xl font-bold leading-tight">
          Earn with TubeGenius. <br /> Share AI video creation
        </h1>
        <p className="text-[#AAACA6]">
          Join our affiliate program and get paid for helping
          <br /> creators script better videos with AI.
        </p>
        <button
          className="flex items-center gap-2 rounded-full bg-[#2BFF13] pl-4 text-sm text-black"
          style={{ fontWeight: '600' }}
        >
          Join with your email
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white">
            <Image src="/images/arrow_right.svg" alt="arrow_right" width={20} height={20} />
          </span>
        </button>
      </div>

      {/* Right Side */}
      <div className="">
        <div className="relative mt-10 w-full rounded-xl bg-[#181916] p-6 shadow-lg transition duration-300 hover:shadow-green-500/30 md:mt-0 md:w-[461px]">
          {notifications.map((note, index) => (
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
    </section>
  );
}
