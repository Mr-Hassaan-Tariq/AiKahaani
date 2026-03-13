'use client';

import { CheckCircle2 } from 'lucide-react';

import { Button } from 'components/shadcn_ui/button';

export function PricingAndIdentity() {
  return (
    <section id="pricing" className="px-6 py-32">
      <div className="container mx-auto max-w-7xl">
        <div className="grid grid-cols-1 items-center gap-20 lg:grid-cols-2">
          <div className="space-y-10">
            <div className="inline-block rounded-full border border-red-600/20 bg-red-600/10 px-5 py-2 text-xs font-bold uppercase tracking-widest text-red-600">
              A premium identity.
            </div>
            <h2 className="text-5xl font-extrabold leading-tight tracking-tight text-gray-900 dark:text-white md:text-7xl">
              Design that feels as premium as your content.
            </h2>
            <p className="max-w-lg text-xl font-medium leading-relaxed text-gray-600 dark:text-gray-400">
              We built AIKahaani with focus in mind. A clean, modern interface that stays out of
              your way so you can create your best work.
            </p>

            <ul className="space-y-6 text-gray-900 dark:text-white">
              {[
                'Minimalist workspace for deep focus',
                'Advanced AI tools for better retention',
                'Built by creators, for creators',
              ].map((item) => (
                <li key={item} className="group flex items-center gap-4 text-lg font-bold">
                  <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-red-600 shadow-lg shadow-red-600/20 transition-transform group-hover:scale-125">
                    <CheckCircle2 size={16} className="text-white" />
                  </div>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="group relative space-y-10 overflow-hidden rounded-[3.5rem] border border-gray-200 bg-gray-50 p-12 shadow-2xl transition-all duration-300 dark:border-white/5 dark:bg-[#121212]">
            <div className="absolute -right-32 -top-32 h-80 w-80 rounded-full bg-red-600/10 blur-[120px] transition-all duration-700 group-hover:bg-red-600/20" />

            <div className="space-y-4">
              <h3 className="text-2xl font-bold text-gray-500 dark:text-gray-400">Standard Plan</h3>
              <div className="flex items-baseline gap-3 text-gray-900 dark:text-white">
                <span className="font-sans text-7xl font-black tracking-tighter">$19</span>
                <span className="text-xl font-bold text-gray-400">/ month</span>
              </div>
            </div>

            <p className="text-lg font-medium leading-relaxed text-gray-500 dark:text-gray-400">
              Perfect for creators looking to systematize their content creation and scale their
              channel.
            </p>

            <div className="space-y-5 pt-4">
              <Button className="h-16 w-full rounded-2xl bg-red-600 text-xl font-bold text-white shadow-xl shadow-red-600/30 transition-all hover:translate-y-[-4px] hover:bg-red-700 active:translate-y-0">
                Get Started Now
              </Button>
              <Button
                variant="outline"
                className="h-16 w-full rounded-2xl border-gray-200 text-xl font-bold text-gray-900 transition-all hover:bg-white dark:border-white/10 dark:text-white dark:hover:bg-white/5"
              >
                Book a demo
              </Button>
            </div>

            <div className="flex items-center justify-center gap-3 border-t border-gray-200 pt-4 dark:border-white/5">
              <div className="flex -space-x-3">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="h-10 w-10 rounded-full border-4 border-gray-50 bg-gray-300 dark:border-[#121212] dark:bg-gray-700"
                  />
                ))}
              </div>
              <span className="text-sm font-bold text-gray-400">Joined by 10,000+ creators</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
