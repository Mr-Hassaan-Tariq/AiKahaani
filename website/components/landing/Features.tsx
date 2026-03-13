'use client';

import { FileText, Layers, Mic, Target, Zap } from 'lucide-react';

import { cn } from 'lib/utils';

const features = [
  {
    id: 'script-gen',
    title: 'Full script generation with YouTube pacing built in',
    description:
      'Generate high-retention scripts that keep viewers watching. Our AI understands YouTube pacing and story structure.',
    icon: <FileText className="h-6 w-6" />,
    className: 'md:col-span-2 md:row-span-2',
    badge: 'Production Ready',
  },
  {
    id: 'hook',
    title: 'Hook engine',
    description: 'Easily craft magnetic hooks that stop the scroll and improve CTR.',
    icon: <Zap className="h-6 w-6" />,
    className: 'md:col-span-1',
  },
  {
    id: 'topic',
    title: 'Topic finder',
    description: 'Find trending topics in your niche that are proven to get views.',
    icon: <Target className="h-6 w-6" />,
    className: 'md:col-span-1',
  },
  {
    id: 'voice',
    title: 'Voice matching',
    description: 'Scripts that actually sound like you. Train the AI on your unique style.',
    icon: <Mic className="h-6 w-6" />,
    className: 'md:col-span-1',
  },
  {
    id: 'workflow',
    title: 'Outline, title, and CTA in one workflow',
    description:
      'Everything you need for a successful video, all generated in one cohesive process.',
    icon: <Layers className="h-6 w-6" />,
    className: 'md:col-span-2',
  },
];

export function Features() {
  return (
    <section
      id="features"
      className="bg-white px-6 py-24 transition-colors duration-300 dark:bg-[#0a0a0a]"
    >
      <div className="container mx-auto max-w-7xl space-y-16 text-center">
        <div className="space-y-4">
          <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-6xl">
            Tools made for serious YouTube creators.
          </h2>
          <p className="mx-auto max-w-2xl text-lg font-medium italic text-gray-500 dark:text-gray-400">
            Create high-quality content faster with specialized tools designed specifically for the
            modern YouTuber.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 text-left md:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.id}
              className={cn(
                'group relative overflow-hidden rounded-[2rem] border border-gray-200 bg-gray-50 p-10 transition-all duration-500 hover:border-red-500/20 hover:bg-white hover:shadow-2xl hover:shadow-red-600/5 dark:border-white/5 dark:bg-[#121212] hover:dark:bg-white/[0.03]',
                feature.className
              )}
            >
              {feature.badge && (
                <div className="absolute right-8 top-8 rounded-full border border-red-600/20 bg-red-600/10 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-red-600 dark:text-red-500">
                  {feature.badge}
                </div>
              )}
              <div className="mb-8 flex h-14 w-14 items-center justify-center rounded-2xl border border-red-600/20 bg-red-600/10 transition-transform duration-500 group-hover:scale-110">
                <div className="text-red-600">{feature.icon}</div>
              </div>
              <h3 className="mb-4 text-3xl font-bold leading-tight text-gray-900 transition-colors group-hover:text-red-600 dark:text-white">
                {feature.title}
              </h3>
              <p className="text-lg font-medium leading-relaxed text-gray-600 dark:text-gray-400">
                {feature.description}
              </p>
              <div className="absolute -bottom-10 -right-10 h-40 w-40 bg-red-600/[0.03] opacity-0 blur-3xl transition-opacity group-hover:opacity-100" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
