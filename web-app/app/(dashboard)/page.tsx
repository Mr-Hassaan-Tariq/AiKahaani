'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });

  useEffect(() => {
    // Set a target date (30 days from now as an example)
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + 30);

    const timer = setInterval(() => {
      const now = new Date().getTime();
      const distance = targetDate.getTime() - now;

      if (distance > 0) {
        setTimeLeft({
          days: Math.floor(distance / (1000 * 60 * 60 * 24)),
          hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((distance % (1000 * 60)) / 1000),
        });
      }
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0a0a0a] px-3">
      {/* Background grid effect */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1a2e1d,transparent_40%)] opacity-50" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,#1a2e1d,transparent_40%)] opacity-50" />

      {/* Main content */}
      <div className="relative z-10 w-full max-w-4xl text-center">
        {/* Logo/Brand */}
        <div className="mb-8">
          <div className="mb-6 inline-flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] shadow-lg">
            <span className="text-black text-2xl font-bold">TG</span>
          </div>
        </div>

        {/* Main heading */}
        <h1 className="mb-6 text-5xl font-bold md:text-7xl lg:text-8xl">
          <span className="bg-gradient-to-r from-[#2BFF13] via-[#20BF0E] to-[#2BFF13] bg-clip-text text-transparent">
            TubeGenius
          </span>
        </h1>

        {/* Description */}
        <p className="mx-auto mb-12 max-w-2xl text-lg leading-relaxed text-gray-400 md:text-xl">
          TubeGenius is envisioned as an AI-powered script writing platform specifically designed to
          automate and enhance the YouTube content creation process. The platform&apos;s overarching
          goal is to function as &quot;Your Genius AI Assistant for YouTube Automation,&quot;
          empowering content creators to effortlessly transform nascent video ideas into
          professionally structured and engaging scripts with minimal manual intervention.
        </p>

        {/* Countdown Timer */}
        <div className="mb-12">
          <h3 className="mb-6 text-lg font-medium text-white">Launching Soon</h3>
          <div className="flex justify-center space-x-4 md:space-x-8">
            {Object.entries(timeLeft).map(([unit, value]) => (
              <div key={unit} className="text-center">
                <div className="min-w-[80px] rounded-lg border border-gray-700 bg-[#161616] p-4 shadow-lg md:min-w-[100px]">
                  <div className="text-2xl font-bold text-white md:text-3xl">
                    {value.toString().padStart(2, '0')}
                  </div>
                  <div className="text-sm capitalize text-gray-400">{unit}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-400">© 2024 TubeGenius. Built for creators.</p>
        </div>
      </div>
    </div>
  );
}
