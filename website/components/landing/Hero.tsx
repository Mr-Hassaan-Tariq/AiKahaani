'use client';

import { useRef } from 'react';
import {
  ArrowRight,
  BarChart3,
  FolderOpen,
  LayoutGrid,
  PenLine,
  Sparkles,
  Zap,
} from 'lucide-react';

import { VariableFontAndCursor } from 'components/ui/variable-font-and-cursor';
import { useMousePosition } from 'components/hooks/use-mouse-position';
import { Button } from 'components/shadcn_ui/button';

export function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { x, y } = useMousePosition(containerRef);

  return (
    <section ref={containerRef} className="relative cursor-none overflow-hidden px-6 pb-20 pt-32">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-pink-50/80 via-white to-white dark:from-gray-900/50 dark:via-[#0a0a0a] dark:to-[#0a0a0a]" />

      {/* Custom cursor overlay */}
      <div className="pointer-events-none absolute inset-0 z-20">
        <div
          className="absolute h-full w-px -translate-x-1/2 bg-gray-300/30 dark:bg-gray-600/30"
          style={{ left: `${x}px` }}
        />
        <div
          className="absolute h-px w-full -translate-y-1/2 bg-gray-300/30 dark:bg-gray-600/30"
          style={{ top: `${y}px` }}
        />
        <div
          className="absolute h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-sm bg-red-600"
          style={{ left: `${x}px`, top: `${y}px` }}
        />
      </div>

      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col items-center gap-16 lg:flex-row">
          <div className="z-10 flex-1 space-y-8 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 rounded-lg border border-pink-200/60 bg-pink-100 px-4 py-2 text-sm font-medium text-gray-700 dark:border-pink-800/30 dark:bg-pink-900/20 dark:text-gray-300">
              <Sparkles className="h-4 w-4 text-red-500" />
              <span>AIKahaani - AI-powered YouTube script & title generator</span>
            </div>

            <h1 className="text-5xl font-extrabold leading-[1.1] tracking-tight text-gray-900 dark:text-white md:text-7xl">
              Turn topics into <br />
              <VariableFontAndCursor
                label="YouTube-ready scripts"
                className="font-robotoFlex text-red-600 dark:text-red-500"
                fontVariationMapping={{
                  y: { name: 'wght', min: 400, max: 900 },
                  x: { name: 'slnt', min: 0, max: -10 },
                }}
                containerRef={containerRef}
              />{' '}
              in seconds.
            </h1>

            <p className="mx-auto max-w-2xl text-lg font-medium leading-relaxed text-gray-600 dark:text-gray-400 md:text-xl lg:mx-0">
              AIKahaani helps YouTube creators generate high-quality video scripts, engaging titles,
              and video outlines in seconds. Enter a topic or keyword—get a complete script with
              hooks, storytelling, and CTAs that improve retention. Built for beginners, faceless
              channels, and content marketers.
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
                  aikahaani.com/editor
                </div>
              </div>

              <div className="flex min-h-[420px] gap-0 overflow-hidden rounded-xl bg-[#FDFDFD] dark:bg-[#1C1C1E]">
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

                <div className="relative flex-1 space-y-5 overflow-hidden rounded-r-xl bg-white p-6 dark:bg-[#28282A]">
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
}
