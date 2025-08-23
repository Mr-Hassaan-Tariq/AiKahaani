'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Clock, ExternalLink, Info, Users } from 'lucide-react';

import { WEB_APP_URL } from '../../../lib/constants';
import Carousel from 'components/ui/Carousel';

const WhatsInside = ({ id }: { id?: string }) => {
  const [value, setValue] = useState<number>(500);

  interface Card {
    img: string;
    title: string;
    tags: string[];
    desc: string;
    example: string;
  }
  const cards: Card[] = [
    {
      img: '/images/inside-card-img.png',
      title: 'Product Review',
      tags: ['Tech', 'Helpful', 'Persuasive'],
      desc: 'Presuasive structure with pros, cons, and clear verdicts.',
      example: 'Marques Brownlee, ijustine',
    },
    {
      img: '/images/inside-card-img.png',
      title: 'Travel Vlog',
      tags: ['Immersive', 'Emotional', 'Scenic'],
      desc: 'Show local fun or international visuals and recommendations.',
      example: 'kara and Nate, Lost Leblanc, Indig...',
    },
    // {
    //     img: "https://placehold.co/600x400/png",
    //     title: "Listicle / Top 10",
    //     tags: ["Structured", "Snappy", "Fun"],
    //     desc: "Examples: Workflows, Tips, Tutorials.",
    // },
  ];

  return (
    <section id={id} className="bg-black py-20 text-white">
      {/* Heading */}
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-bold md:text-4xl">What’s inside</h2>
        <p className="mt-3 text-[#AAACA6]">
          A quick look at the tools that help you go from idea to ready-to-post script.
        </p>
      </div>

      <div className="block md:hidden">
        <Carousel
          items={[
            <div
              key="1"
              className="col-span-12 h-[600px] rounded-2xl border border-[#BAFF381F] bg-gradient-to-br from-[#161616] via-[#161616] to-[#BAFF38]/[0.06] p-8 shadow-lg md:col-span-7"
            >
              <div>
                <h2 className="mb-4 text-lg font-semibold text-gray-300">
                  Choose a template style
                </h2>
                <div className="mb-6 grid grid-cols-1 gap-3 md:grid-cols-2">
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Short</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> ~20m,2.6k-3k words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      Great for content creation and presentations
                    </p>
                  </div>
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Medium</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> ~40m,5.2k-6k words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      Ideal for in-depth videos, product demos, interviews
                    </p>
                  </div>
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Long</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> ~60m,7.8k-9k words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      Best for comprehensive tutorials, Webinars, lectures
                    </p>
                  </div>
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Flexible Outline</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> Flexible,100-300 words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      High-level structure without full script
                    </p>
                  </div>
                </div>

                <div className="mb-6">
                  <p className="text-sm text-gray-300">Script length & duration</p>
                  <input
                    type="range"
                    min={0}
                    max={10000}
                    value={value}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setValue(Number(e.target.value))
                    }
                    className="mb-2 h-2 w-full accent-[#20BF0E]"
                    id="progressSlider"
                  />
                </div>

                <h3 className="mb-2 text-xl font-bold text-white">Script Generator</h3>
                <p className="mb-6 text-sm text-gray-400">
                  AI writes full YouTube scripts based on your idea.
                </p>
              </div>
              <Link href={`${WEB_APP_URL}/signup`} target="_blank">
                <button className="flex items-center gap-2 py-2 text-sm text-white">
                  Try now{' '}
                  <span>
                    <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                  </span>
                </button>
              </Link>
            </div>,
            <div
              key="2"
              className="col-span-12 h-[600px] rounded-2xl border border-[#BAFF381F] bg-[#161616] p-10 shadow-lg md:col-span-5"
            >
              <ul className="relative mb-8 h-[220px] space-y-4 overflow-hidden text-sm text-gray-300">
                <li className="rounded-xl border border-[#BAFF381F] p-3">
                  <p className="mt-1 flex items-center gap-2 text-[14px] font-medium text-white">
                    <Users className="h-4 w-4" /> Milestone unlocked: $500 in commissions!
                  </p>
                  <p className="my-1 text-[10px] text-[#aaaca5]">
                    Congrats on hitting this major affiliate milestone
                  </p>
                </li>
                <li className="rounded-xl border border-[#BAFF381F] p-3">
                  <p className="mt-1 flex items-center gap-2 text-[14px] font-medium text-white">
                    <Users className="h-4 w-4" /> New commission earned!
                  </p>
                  <p className="my-1 text-[10px] text-[#aaaca5]">
                    You&apos;ve just earned $25 from a new referral
                  </p>
                </li>
                <li className="rounded-xl border border-[#BAFF381F] p-3">
                  <p className="mt-1 flex items-center gap-2 text-[14px] font-medium text-white">
                    <Users className="h-4 w-4" /> You aot your first referral
                  </p>
                </li>
                <div className="pointer-events-none absolute bottom-0 left-0 h-14 w-full bg-gradient-to-t from-[#161616] to-transparent" />
              </ul>

              {/* Content */}
              <div className="mb-7">
                <h3 className="my-2 text-xl font-medium text-white">Title Optimizer</h3>
                <p className="my-4 text-[17px] text-[#AAACA6]">
                  Get viral, high-CTR titles — created or improved by AI.
                </p>
              </div>

              {/* Button */}
              <Link href={`${WEB_APP_URL}/signup`} target="_blank">
                <button className="flex items-center gap-2 py-2 text-sm text-white">
                  Try now{' '}
                  <span>
                    <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                  </span>
                </button>
              </Link>
            </div>,
            <div
              key="3"
              className="col-span-12 h-[600px] rounded-2xl border border-[#BAFF381F] bg-[#161616] px-7 pt-14 md:col-span-5"
            >
              <div className="">
                <p className="flex items-center gap-2 text-sm text-gray-400">
                  What&apos;s your video about? <Info className="h-4 w-4" />
                </p>
                <div className="mt-3 rounded-xl bg-[#2d2e2d] p-3 pb-10 text-[12px] text-gray-300">
                  A short video sharing 5 science-backed productivity hacks that help better, and
                  get more done with less effort.
                </div>

                <p className="mt-7 flex items-center gap-2 text-sm text-white">
                  Tone / Style <Info className="h-4 w-4" />
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {['Controversial', 'Shocking', 'Persuasive', 'Mysterious', 'Dramatic'].map(
                    (tone) => (
                      <span
                        key={tone}
                        className="rounded-full border border-[#323927] bg-[#232423] px-3 py-1 text-[10px] text-gray-300"
                      >
                        {tone}
                      </span>
                    )
                  )}
                </div>
              </div>
              <div className="mt-8">
                <h2 className="text-lg font-semibold text-white">Affiliate Program</h2>
                <p className="mt-4 text-[16px] text-[#a8aea4]">
                  Earn 50% lifetime revenue for every referred <br />
                  creator.
                </p>
                <Link href={`${WEB_APP_URL}/signup`} target="_blank">
                  <button className="mt-3 flex items-center gap-2 text-sm text-white">
                    Try now{' '}
                    <span>
                      <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                    </span>
                  </button>
                </Link>
              </div>
            </div>,
            <div
              key="4"
              className="col-span-12 flex h-[600px] flex-col justify-between rounded-2xl border border-[#BAFF381F] bg-[#161616] p-6 md:col-span-7"
            >
              <div className="w-full max-w-5xl rounded-2xl shadow-lg">
                <div className="mb-8 grid grid-cols-12 gap-5">
                  {cards.map((card, idx) => (
                    <div
                      key={idx}
                      className="col-span-12 flex flex-col overflow-hidden rounded-xl border border-[#BAFF381F] bg-[#1a1a1a] p-3 transition hover:bg-[#222] md:col-span-6"
                    >
                      <div className="relative mb-3 h-40 w-full overflow-hidden rounded-md">
                        <img
                          src={card.img}
                          alt={card.title}
                          className="h-full w-full rounded-md object-cover"
                        />
                      </div>

                      {/* Tags */}
                      <div className="mb-2 flex flex-wrap items-center justify-between text-xs text-gray-300">
                        <div className="rounded-md border border-[#BAFF381F] bg-[#2a2a2a] p-2">
                          {card.tags.map((tag, i) => (
                            <span key={i} className="rounded-md text-white">
                              {tag}
                              {i < card.tags.length - 1 && ', '}
                            </span>
                          ))}
                        </div>
                        <ExternalLink className="h-5 w-5 cursor-pointer text-white" />
                      </div>

                      {/* Title */}
                      <h3 className="mb-1 font-medium text-white">{card.title}</h3>

                      {/* Description */}
                      <p className="text-[12px] leading-snug text-[#959792]">{card.desc}</p>
                      <p className="mt-1 text-[12px] leading-snug text-[#959792]">
                        Examples: {card.example}
                      </p>
                    </div>
                  ))}
                </div>
                {/* Bottom Section */}
                <div>
                  <h2 className="mb-1 text-xl font-semibold text-white">Viral Niches Vault</h2>
                  <p className="mt-4 text-[16px] text-[#a8aea4]">
                    Discover 300+ proven YouTube niches and grow faster.
                  </p>
                </div>
                <button className="flex items-center gap-2 py-2 text-sm text-white">
                  Try now{' '}
                  <span>
                    <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                  </span>
                </button>
              </div>
            </div>,
          ]}
          className="w-full"
        />
      </div>
      <div className="hidden md:block">
        <div className="flex items-center justify-center bg-black p-6">
          <div className="grid w-full grid-cols-1 gap-6 md:grid-cols-12">
            <div className="col-span-12 rounded-2xl border border-[#BAFF381F] bg-gradient-to-br from-[#161616] via-[#161616] to-[#BAFF38]/[0.06] p-8 shadow-lg md:col-span-7">
              <div>
                <h2 className="mb-4 text-lg font-semibold text-gray-300">
                  Choose a template style
                </h2>
                <div className="mb-6 grid grid-cols-1 gap-3 md:grid-cols-2">
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Short</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> ~20m,2.6k-3k words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      Great for content creation and presentations
                    </p>
                  </div>
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Medium</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> ~40m,5.2k-6k words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      Ideal for in-depth videos, product demos, interviews
                    </p>
                  </div>
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Long</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> ~60m,7.8k-9k words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      Best for comprehensive tutorials, Webinars, lectures
                    </p>
                  </div>
                  <div className="rounded-xl bg-[#2d2e2d] p-4 text-sm text-gray-200 hover:border-gray-500">
                    <div className="flex items-center justify-between">
                      <p className="font-medium">Flexible Outline</p>
                      <p className="flex items-center gap-2 text-xs text-white">
                        <Clock className="h-4 w-4 text-gray-400" /> Flexible,100-300 words
                      </p>
                    </div>
                    <p className="mt-2 text-[10px] text-[#aaaca5]">
                      High-level structure without full script
                    </p>
                  </div>
                </div>

                <div className="mb-6">
                  <p className="text-sm text-gray-300">Script length & duration</p>
                  <input
                    type="range"
                    min={0}
                    max={10000}
                    value={value}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setValue(Number(e.target.value))
                    }
                    className="mb-2 h-2 w-full accent-[#20BF0E]"
                    id="progressSlider"
                  />
                </div>

                <h3 className="mb-2 text-xl font-bold text-white">Script Generator</h3>
                <p className="mb-6 text-sm text-gray-400">
                  AI writes full YouTube scripts based on your idea.
                </p>
              </div>
              <Link href={`${WEB_APP_URL}/signup`} target="_blank">
                <button className="flex items-center gap-2 py-2 text-sm text-white">
                  Try now{' '}
                  <span>
                    <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                  </span>
                </button>
              </Link>
            </div>

            <div className="col-span-12 rounded-2xl border border-[#BAFF381F] bg-[#161616] p-10 shadow-lg md:col-span-5">
              <ul className="relative mb-8 h-[220px] space-y-4 overflow-hidden text-sm text-gray-300">
                <li className="rounded-xl border border-[#BAFF381F] p-3">
                  <p className="mt-1 flex items-center gap-2 text-[14px] font-medium text-white">
                    <Users className="h-4 w-4" /> Milestone unlocked: $500 in commissions!
                  </p>
                  <p className="my-1 text-[10px] text-[#aaaca5]">
                    Congrats on hitting this major affiliate milestone
                  </p>
                </li>
                <li className="rounded-xl border border-[#BAFF381F] p-3">
                  <p className="mt-1 flex items-center gap-2 text-[14px] font-medium text-white">
                    <Users className="h-4 w-4" /> New commission earned!
                  </p>
                  <p className="my-1 text-[10px] text-[#aaaca5]">
                    You’ve just earned $25 from a new referral
                  </p>
                </li>
                <li className="rounded-xl border border-[#BAFF381F] p-3">
                  <p className="mt-1 flex items-center gap-2 text-[14px] font-medium text-white">
                    <Users className="h-4 w-4" /> You aot your first referral
                  </p>
                </li>
                <div className="pointer-events-none absolute bottom-0 left-0 h-14 w-full bg-gradient-to-t from-[#161616] to-transparent" />
              </ul>

              {/* Content */}
              <div className="mb-7">
                <h3 className="my-2 text-xl font-medium text-white">Title Optimizer</h3>
                <p className="my-4 text-[17px] text-[#AAACA6]">
                  Get viral, high-CTR titles — created or improved by AI.
                </p>
              </div>

              {/* Button */}
              <Link href={`${WEB_APP_URL}/signup`} target="_blank">
                <button className="flex items-center gap-2 py-2 text-sm text-white">
                  Try now{' '}
                  <span>
                    <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                  </span>
                </button>
              </Link>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-center bg-black px-6">
          <div className="grid w-full grid-cols-1 gap-6 md:grid-cols-12">
            {/* Left Card */}
            <div className="col-span-12 rounded-2xl border border-[#BAFF381F] bg-[#161616] px-7 pt-14 md:col-span-5">
              <div className="">
                <p className="flex items-center gap-2 text-sm text-gray-400">
                  What’s your video about? <Info className="h-4 w-4" />
                </p>
                <div className="mt-3 rounded-xl bg-[#2d2e2d] p-3 pb-10 text-[12px] text-gray-300">
                  A short video sharing 5 science-backed productivity hacks that help better, and
                  get more done with less effort.
                </div>

                <p className="mt-7 flex items-center gap-2 text-sm text-white">
                  Tone / Style <Info className="h-4 w-4" />
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {['Controversial', 'Shocking', 'Persuasive', 'Mysterious', 'Dramatic'].map(
                    (tone) => (
                      <span
                        key={tone}
                        className="rounded-full border border-[#323927] bg-[#232423] px-3 py-1 text-[10px] text-gray-300"
                      >
                        {tone}
                      </span>
                    )
                  )}
                </div>
              </div>
              <div className="mt-8">
                <h2 className="text-lg font-semibold text-white">Affiliate Program</h2>
                <p className="mt-4 text-[16px] text-[#a8aea4]">
                  Earn 50% lifetime revenue for every referred <br />
                  creator.
                </p>
                <Link href={`${WEB_APP_URL}/signup`} target="_blank">
                  <button className="mt-3 flex items-center gap-2 text-sm text-white">
                    Try now{' '}
                    <span>
                      <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                    </span>
                  </button>
                </Link>
              </div>
            </div>

            {/* Right Card */}
            <div className="col-span-12 flex flex-col justify-between rounded-2xl border border-[#BAFF381F] bg-[#161616] p-6 md:col-span-7">
              <div className="w-full max-w-5xl rounded-2xl shadow-lg">
                <div className="mb-8 grid grid-cols-12 gap-5">
                  {cards.map((card, idx) => (
                    <div
                      key={idx}
                      className="col-span-12 flex flex-col overflow-hidden rounded-xl border border-[#BAFF381F] bg-[#1a1a1a] p-3 transition hover:bg-[#222] md:col-span-6"
                    >
                      <div className="relative mb-3 h-40 w-full overflow-hidden rounded-md">
                        <img
                          src={card.img}
                          alt={card.title}
                          className="h-full w-full rounded-md object-cover"
                        />
                      </div>

                      {/* Tags */}
                      <div className="mb-2 flex flex-wrap items-center justify-between text-xs text-gray-300">
                        <div className="rounded-md border border-[#BAFF381F] bg-[#2a2a2a] p-2">
                          {card.tags.map((tag, i) => (
                            <span key={i} className="rounded-md text-white">
                              {tag}
                              {i < card.tags.length - 1 && ', '}
                            </span>
                          ))}
                        </div>
                        <ExternalLink className="h-5 w-5 cursor-pointer text-white" />
                      </div>

                      {/* Title */}
                      <h3 className="mb-1 font-medium text-white">{card.title}</h3>

                      {/* Description */}
                      <p className="text-[12px] leading-snug text-[#959792]">{card.desc}</p>
                      <p className="mt-1 text-[12px] leading-snug text-[#959792]">
                        Examples: {card.example}
                      </p>
                    </div>
                  ))}
                </div>
                {/* Bottom Section */}
                <div>
                  <h2 className="mb-1 text-xl font-semibold text-white">Viral Niches Vault</h2>
                  <p className="mt-4 text-[16px] text-[#a8aea4]">
                    Discover 300+ proven YouTube niches and grow faster.
                  </p>
                </div>
                <button className="flex items-center gap-2 py-2 text-sm text-white">
                  Try now{' '}
                  <span>
                    <Image src="/images/right.svg" alt="arrow-right" width={20} height={20} />
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhatsInside;
