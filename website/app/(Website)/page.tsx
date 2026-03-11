'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  FileText,
  FolderOpen,
  Layers,
  LayoutGrid,
  Menu,
  Mic,
  PenLine,
  Sparkles,
  Target,
  X,
  Zap,
} from 'lucide-react';

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../../components/shadcn_ui/accordion';
import { cn } from 'lib/utils';
import { Button } from 'components/shadcn_ui/button';
import { ThemeToggle } from 'components/ThemeToggle';

// --- Shared Components ---

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed left-0 right-0 top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md transition-colors duration-300 dark:border-white/5 dark:bg-[#0a0a0a]/80">
      <div className="container mx-auto flex h-20 items-center justify-between px-6 md:grid md:grid-cols-3 md:gap-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-600 shadow-lg shadow-red-600/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            videoScript
          </span>
        </div>

        <div className="hidden items-center justify-center gap-8 text-gray-600 dark:text-gray-400 md:flex">
          <Link
            href="#features"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            Features
          </Link>
          <Link
            href="#how-it-works"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            How it works
          </Link>
          <Link
            href="#pricing"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            Pricing
          </Link>
          <Link
            href="#faq"
            className="text-sm font-medium transition-colors hover:text-red-500 dark:hover:text-white"
          >
            FAQ
          </Link>
        </div>

        <div className="hidden items-center justify-end gap-3 md:flex">
          <ThemeToggle className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-white/10 dark:hover:text-white" />
          <Link
            href="/login"
            className="text-sm font-medium text-gray-700 transition-colors hover:text-red-500 dark:text-gray-300"
          >
            Login
          </Link>
          <Button className="rounded-full bg-red-600 px-6 font-semibold text-white transition-all hover:translate-y-[-2px] hover:bg-red-700 hover:shadow-lg hover:shadow-red-600/30 active:translate-y-0">
            Try Free
          </Button>
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle className="rounded-lg p-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white" />
          <button className="text-gray-900 dark:text-white" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="flex flex-col gap-6 border-b border-gray-200 bg-white px-6 py-8 duration-300 animate-in slide-in-from-top dark:border-white/5 dark:bg-[#0a0a0a] md:hidden">
          <Link
            href="#features"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            Features
          </Link>
          <Link
            href="#how-it-works"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            How it works
          </Link>
          <Link
            href="#pricing"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            Pricing
          </Link>
          <Link
            href="#faq"
            className="text-lg font-medium text-gray-600 dark:text-gray-400"
            onClick={() => setIsOpen(false)}
          >
            FAQ
          </Link>
          <div className="flex flex-col gap-4 pt-4">
            <Link
              href="/login"
              className="text-center text-lg font-medium text-gray-900 dark:text-white"
            >
              Login
            </Link>
            <Button className="rounded-full bg-red-600 py-6 text-lg font-semibold text-white hover:bg-red-700">
              Try Free
            </Button>
          </div>
        </div>
      )}
    </nav>
  );
};

const Hero = () => {
  return (
    <section className="relative overflow-hidden px-6 pb-20 pt-32">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-pink-50/80 via-white to-white dark:from-gray-900/50 dark:via-[#0a0a0a] dark:to-[#0a0a0a]" />

      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col items-center gap-16 lg:flex-row">
          <div className="z-10 flex-1 space-y-8 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 rounded-lg border border-pink-200/60 bg-pink-100 px-4 py-2 text-sm font-medium text-gray-700 dark:border-pink-800/30 dark:bg-pink-900/20 dark:text-gray-300">
              <Sparkles className="h-4 w-4 text-red-500" />
              <span>YouTube-style creative engine for script generation</span>
            </div>

            <h1 className="text-5xl font-extrabold leading-[1.1] tracking-tight text-gray-900 dark:text-white md:text-7xl">
              Turn video ideas <br />
              into <span className="text-red-600">high-retention</span>{' '}
              <span className="text-red-600">YouTube scripts</span> in minutes.
            </h1>

            <p className="mx-auto max-w-2xl text-lg font-medium leading-relaxed text-gray-600 dark:text-gray-400 md:text-xl lg:mx-0">
              videoScript helps creators generate hooks, story beats, title angles, scene prompts,
              and full talking scripts with a bright, creator-first workflow inspired by modern
              video platforms.
            </p>

            <div className="flex flex-col items-center justify-center gap-4 pt-4 sm:flex-row lg:justify-start">
              <Button className="group h-14 rounded-full bg-red-600 px-8 text-lg font-bold text-white transition-all hover:translate-y-[-2px] hover:bg-red-700 hover:shadow-xl hover:shadow-red-600/30 active:translate-y-0">
                Generate a script
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
              <Button className="h-14 rounded-full border-0 bg-gray-100 px-8 text-lg font-semibold text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700">
                See sample workflow
              </Button>
            </div>

            <div className="flex flex-col items-center justify-center gap-x-6 gap-y-2 pt-8 text-sm font-medium text-gray-600 dark:text-gray-400 sm:flex-row sm:flex-wrap lg:justify-start">
              <span>Hooks that sound natural</span>
              <span className="hidden sm:inline">·</span>
              <span>Built for Shorts & long-form</span>
              <span className="hidden sm:inline">·</span>
              <span>Titles + outline + CTA included</span>
            </div>
          </div>

          <div className="relative w-full max-w-2xl flex-1 lg:max-w-none">
            <div className="group relative z-10 overflow-visible rounded-2xl border border-gray-200/80 bg-white p-4 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.08)] transition-colors duration-300 dark:border-gray-700/60 dark:bg-[#1C1C1E] dark:shadow-[0_25px_50px_-12px_rgba(0,0,0,0.4)]">
              <div className="mb-3 flex items-center justify-between px-2">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <div className="h-3 w-3 rounded-full bg-amber-400" />
                  <div className="h-3 w-3 rounded-full bg-emerald-500" />
                </div>
                <div className="rounded-full bg-gray-100 px-4 py-1.5 text-[11px] font-medium text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                  videoscript.app/editor/viral-script
                </div>
              </div>

              <div className="flex min-h-[420px] gap-0 overflow-hidden rounded-xl bg-[#FDFDFD] dark:bg-[#1C1C1E]">
                {/* Left Sidebar - Script Studio */}
                <div className="hidden w-44 flex-col rounded-l-xl border-r border-gray-100 bg-white p-4 dark:border-gray-700/50 dark:bg-[#28282A] sm:flex">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2.5 rounded-lg bg-red-50 px-3 py-2 text-red-600 dark:bg-red-900/80 dark:text-white">
                      <PenLine className="h-4 w-4 flex-shrink-0" />
                      <span className="text-sm font-semibold">Script Studio</span>
                    </div>
                    {[
                      { icon: Zap, label: 'Hook Builder' },
                      { icon: LayoutGrid, label: 'Title Ideas' },
                      { icon: BarChart3, label: 'Retention Map' },
                      { icon: FolderOpen, label: 'Content Queue' },
                    ].map(({ icon: Icon, label }) => (
                      <div
                        key={label}
                        className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-gray-500 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-700/50"
                      >
                        <Icon className="h-4 w-4 flex-shrink-0" />
                        <span className="text-sm font-medium">{label}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-auto pt-4">
                    <div className="rounded-xl border border-gray-100 bg-gray-50 p-3 dark:border-gray-700/50 dark:bg-gray-800/80">
                      <div className="mb-1.5 text-[10px] font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                        Live generation
                      </div>
                      <div className="text-sm font-bold text-gray-900 dark:text-white">
                        Creating 3 intro variations
                      </div>
                      <div className="mt-2 space-y-1.5">
                        <div className="h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-600" />
                        <div className="h-1.5 w-3/4 rounded-full bg-gray-200 dark:bg-gray-600" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Content */}
                <div className="relative flex-1 space-y-5 overflow-hidden rounded-r-xl bg-white p-6 dark:bg-[#28282A]">
                  {/* Video Project Header */}
                  <div className="space-y-2">
                    <h3 className="text-base font-bold leading-tight text-gray-900 dark:text-white">
                      How to grow a faceless YouTube channel in 2025
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Long-form explainer · 8 min target · educational tone.
                    </p>
                    <div className="inline-block rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                      Script ready
                    </div>
                  </div>

                  {/* Two Content Cards */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-3 rounded-xl border border-gray-100 bg-gray-50/50 p-4 dark:border-gray-700/50 dark:bg-gray-800/50">
                      <div className="flex flex-wrap gap-1.5">
                        <span className="rounded-lg bg-gray-200/80 px-2.5 py-1 text-xs font-bold text-gray-900 dark:bg-gray-700 dark:text-gray-300">
                          Hook
                        </span>
                        <span className="rounded-lg bg-gray-200/80 px-2.5 py-1 text-xs font-bold text-gray-900 dark:bg-gray-700 dark:text-gray-300">
                          Audience pain
                        </span>
                        <span className="rounded-lg bg-gray-200/80 px-2.5 py-1 text-xs font-bold text-gray-900 dark:bg-gray-700 dark:text-gray-300">
                          Payoff
                        </span>
                      </div>
                      <div className="space-y-1.5 pt-2">
                        <div className="h-2 w-full rounded bg-gray-200 dark:bg-gray-600" />
                        <div className="h-2 w-4/5 rounded bg-gray-200 dark:bg-gray-600" />
                        <div className="h-2 w-2/3 rounded bg-gray-200 dark:bg-gray-600" />
                        <div className="mt-2 h-4 w-[92%] rounded-lg bg-gray-200/80 dark:bg-gray-600/80" />
                      </div>
                    </div>
                    <div className="space-y-3 rounded-xl border border-gray-100 bg-gray-50/50 p-4 dark:border-gray-700/50 dark:bg-gray-800/50">
                      <div className="text-xs font-bold text-gray-900 dark:text-gray-300">
                        Predicted retention curve
                      </div>
                      <div className="h-24 rounded-lg bg-pink-100 dark:bg-red-900/40" />
                      <div className="space-y-1.5">
                        <div className="h-2 w-full rounded bg-gray-200 dark:bg-gray-600" />
                        <div className="h-2 w-3/4 rounded bg-gray-200 dark:bg-gray-600" />
                        <div className="h-2 w-1/2 rounded bg-gray-200 dark:bg-gray-600" />
                      </div>
                    </div>
                  </div>

                  {/* Viral Score Overlay */}
                  <div className="absolute -bottom-4 -right-4 w-36 rotate-3 transform rounded-xl border-2 border-white bg-red-600 p-3.5 shadow-lg dark:border-gray-800">
                    <div className="mb-1.5 text-[10px] font-bold uppercase tracking-wide text-white">
                      Viral Score
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-white/25">
                      <div className="h-full w-[85%] rounded-full bg-white" />
                    </div>
                    <div className="mt-1.5 text-[9px] font-bold uppercase tracking-wider text-white">
                      HIGH RETENTION
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const Marquee = () => {
  const logos = ['VidIQ', 'TubeBuddy', 'Canva', 'Veed.io', 'Descript', 'CapCut'];
  return (
    <div className="overflow-hidden border-y border-gray-200 bg-gray-100 py-12 dark:border-white/5 dark:bg-white/5">
      <div className="animate-marquee flex items-center justify-center gap-20 whitespace-nowrap">
        {logos.map((logo) => (
          <span
            key={logo}
            className="text-2xl font-black uppercase tracking-tighter text-gray-400 dark:text-gray-500"
          >
            {logo}
          </span>
        ))}
        {logos.map((logo) => (
          <span
            key={`${logo}-dup`}
            className="text-2xl font-black uppercase tracking-tighter text-gray-400 dark:text-gray-500"
          >
            {logo}
          </span>
        ))}
      </div>
    </div>
  );
};

const Features = () => {
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
};

const Steps = () => {
  const steps = [
    {
      number: '1',
      title: 'Describe your next video',
      description:
        'Briefly explain what you want your video to be about. The more detail, the better.',
    },
    {
      number: '2',
      title: 'Pick structure and tone',
      description:
        'Choose from proven YouTube structures (Educational, Storytelling, Hype) and set your voice.',
    },
    {
      number: '3',
      title: 'Generate and refine',
      description:
        'Get a full script in seconds. Use our editor to tweak and finalize your masterpiece.',
    },
  ];

  return (
    <section
      id="how-it-works"
      className="relative bg-gray-50 px-6 py-24 transition-colors duration-300 dark:bg-[#0a0a0a]"
    >
      <div className="absolute bottom-0 left-1/2 h-[1px] w-full -translate-x-1/2 bg-gradient-to-r from-transparent via-gray-200 to-transparent dark:via-white/10" />

      <div className="container mx-auto max-w-7xl space-y-16 text-center">
        <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-6xl">
          From idea to upload plan in 3 steps
        </h2>

        <div className="relative grid grid-cols-1 gap-12 pt-8 md:grid-cols-3">
          <div className="absolute left-1/4 right-1/4 top-[70px] z-0 hidden h-[2px] bg-gray-200 dark:bg-white/5 md:block" />

          {steps.map((step) => (
            <div
              key={step.number}
              className="group relative z-10 flex flex-col items-center space-y-8"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-600 font-sans text-2xl font-black text-white shadow-xl shadow-red-600/20 transition-all duration-500 group-hover:rotate-3 group-hover:scale-110">
                {step.number}
              </div>
              <div className="space-y-3">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{step.title}</h3>
                <p className="max-w-xs text-lg font-medium text-gray-500 dark:text-gray-400">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const PricingAndIdentity = () => {
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
              We built videoScript with focus in mind. A clean, modern interface that stays out of
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
};

const FAQSection = () => {
  const faqs = [
    {
      q: 'Can I generate scripts for different languages?',
      a: 'Yes! videoScript supports over 50 languages. Our AI is trained on global YouTube data, so it understands local context and slang as well.',
    },
    {
      q: 'How does the pacing engine work?',
      a: 'Our engine analyzes retention patterns from millions of successful videos. It inserts pattern interrupts, transitions, and calls-to-action at the exact moments viewers typically drop off.',
    },
    {
      q: 'Is it really different from using ChatGPT?',
      a: 'Absolutely. While ChatGPT is generic, videoScript is fine-tuned specifically for YouTube. It includes niche topic discovery, viral hook frameworks, and storyboard generation that generic LLMs fail at.',
    },
    {
      q: 'Can I save my custom voice/style?',
      a: 'Yes, you can upload your previous successful scripts to train your personalized style profile, ensuring every generated script sounds exactly like you.',
    },
  ];

  return (
    <section
      id="faq"
      className="bg-white px-6 py-24 transition-colors duration-300 dark:bg-[#0a0a0a]"
    >
      <div className="container mx-auto max-w-4xl space-y-20 text-center">
        <div className="space-y-4">
          <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-5xl">
            Frequently asked questions
          </h2>
          <p className="text-lg font-medium text-gray-500 dark:text-gray-400">
            Everything you need to know about videoScript
          </p>
        </div>

        <div className="text-left">
          <Accordion type="single" collapsible className="w-full space-y-6">
            {faqs.map((faq, i) => (
              <AccordionItem
                key={i}
                value={`item-${i}`}
                className="rounded-[2rem] border border-gray-200 bg-gray-50 px-8 shadow-sm transition-all hover:bg-gray-100 dark:border-white/5 dark:bg-white/[0.02] dark:hover:bg-white/[0.04]"
              >
                <AccordionTrigger className="py-8 text-gray-900 hover:no-underline dark:text-white">
                  <span className="text-left text-xl font-bold">{faq.q}</span>
                </AccordionTrigger>
                <AccordionContent className="pb-8 text-lg font-medium leading-relaxed text-gray-500 dark:text-gray-400">
                  {faq.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer className="border-t border-gray-100 bg-gray-50 px-6 py-16 transition-colors duration-300 dark:border-white/5 dark:bg-[#0a0a0a]">
      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col items-center justify-between gap-10 md:flex-row">
          <div className="flex flex-col items-center gap-4 md:items-start">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-600 shadow-lg shadow-red-600/20">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-2xl font-black tracking-tighter text-gray-900 dark:text-white">
                videoScript
              </span>
            </div>
            <p className="font-bold text-gray-400">Empowering the next generation of creators.</p>
          </div>

          <div className="flex flex-wrap justify-center gap-10 text-[10px] font-bold uppercase tracking-widest text-gray-500">
            <Link href="#" className="transition-colors hover:text-red-500">
              Product
            </Link>
            <Link href="#" className="transition-colors hover:text-red-500">
              Resources
            </Link>
            <Link href="#" className="transition-colors hover:text-red-500">
              Company
            </Link>
            <Link href="#" className="transition-colors hover:text-red-500">
              Social
            </Link>
          </div>
        </div>

        <div className="mt-16 flex flex-col items-center justify-between gap-6 border-t border-gray-200 pt-8 dark:border-white/5 md:flex-row">
          <div className="text-sm font-bold text-gray-400">
            © 2025 videoScript Inc. All rights reserved.
          </div>

          <div className="flex gap-8">
            <Link
              href="#"
              className="text-sm font-bold text-gray-400 transition-colors hover:text-red-500"
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              className="text-sm font-bold text-gray-400 transition-colors hover:text-red-500"
            >
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

// --- Main Page Component ---

export default function main() {
  return (
    <div className="min-h-screen bg-white font-sans transition-colors duration-300 selection:bg-red-500 selection:text-white dark:bg-[#0a0a0a] dark:text-white">
      <style jsx global>{`
        @keyframes marquee {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .animate-marquee {
            animation: none;
          }
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
          width: 8px;
        }
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        ::-webkit-scrollbar-thumb {
          background: #333;
          border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: #444;
        }
      `}</style>

      <div className="relative">
        <Navbar />
        <main>
          <Hero />
          <Marquee />
          <Features />
          <Steps />
          <PricingAndIdentity />
          <FAQSection />
        </main>
        <Footer />
      </div>
    </div>
  );
}
