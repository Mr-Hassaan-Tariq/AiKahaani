"use client"
import React, { useState } from "react";
import { Clock, Users, Info, ExternalLink } from 'lucide-react';
import Image from "next/image";


const WhatsInside = () => {
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
            img: "https://placehold.co/600x400/png",
            title: "Product Review",
            tags: ["Tech", "Helpful", "Persuasive"],
            desc: "Presuasive structure with pros, cons, and clear verdicts.",
            example: "Marques Brownlee, ijustine"
        },
        {
            img: "https://placehold.co/600x400/png",
            title: "Travel Vlog",
            tags: ["Immersive", "Emotional", "Scenic"],
            desc: "Show local fun or international visuals and recommendations.",
            example: "kara and Nate, Lost Leblanc, Indig..."
        },
        // {
        //     img: "https://placehold.co/600x400/png",
        //     title: "Listicle / Top 10",
        //     tags: ["Structured", "Snappy", "Fun"],
        //     desc: "Examples: Workflows, Tips, Tutorials.",
        // },
    ];

    return (
        <section className="bg-black text-white py-20 px-6 md:px-16">
            {/* Heading */}
            <div className="text-center mb-10">
                <h2 className="text-3xl md:text-4xl font-bold">What’s inside</h2>
                <p className="text-[#AAACA6] mt-3">
                    A quick look at the tools that help you go from idea to ready-to-post script.
                </p>
            </div>

            <div className="bg-black flex items-center justify-center p-6">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 w-full">

                    <div className="col-span-12 md:col-span-7 bg-[#161616] rounded-2xl shadow-lg p-8 border border-[#BAFF381F]">
                        <div>
                            <h2 className="text-lg font-semibold text-gray-300 mb-4">Choose a template style</h2>
                            <div className="grid grid-cols-2 gap-3 mb-6">
                                <div className="bg-[#2d2e2d] rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                                    <div className="flex items-center justify-between">
                                        <p className="font-medium">Short</p>
                                        <p className="text-xs text-white flex items-center gap-2"><Clock className="w-4 h-4 text-gray-400" /> ~20m,2.6k-3k words</p>
                                    </div>
                                    <p className="text-[#aaaca5] text-[10px] mt-2">Great for content creation and presentations</p>
                                </div>
                                <div className="bg-[#2d2e2d] rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                                    <div className="flex items-center justify-between">
                                        <p className="font-medium">Medium</p>
                                        <p className="text-xs text-white flex items-center gap-2"><Clock className="w-4 h-4 text-gray-400" /> ~40m,5.2k-6k words</p>
                                    </div>
                                    <p className="text-[#aaaca5] text-[10px] mt-2">Ideal for in-depth videos, product demos, interviews</p>
                                </div>
                                <div className="bg-[#2d2e2d] rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                                    <div className="flex items-center justify-between">
                                        <p className="font-medium">Long</p>
                                        <p className="text-xs text-white flex items-center gap-2"><Clock className="w-4 h-4 text-gray-400" /> ~60m,7.8k-9k words</p>
                                    </div>
                                    <p className="text-[#aaaca5] text-[10px] mt-2">Best for comprehensive tutorials, Webinars, lectures</p>
                                </div>
                                <div className="bg-[#2d2e2d] rounded-xl p-4 text-gray-200 text-sm hover:border-gray-500">
                                    <div className="flex items-center justify-between">
                                        <p className="font-medium">Flexible Outline</p>
                                        <p className="text-xs text-white flex items-center gap-2"><Clock className="w-4 h-4 text-gray-400" /> Flexible,100-300 words</p>
                                    </div>
                                    <p className="text-[#aaaca5] text-[10px] mt-2">High-level structure without full script</p>
                                </div>
                            </div>

                            <div className=" mb-6">
                                <p className="text-gray-300 text-sm">Script length & duration</p>
                                <input
                                    type="range"
                                    min={0}
                                    max={10000}
                                    value={value}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                        setValue(Number(e.target.value))
                                    }
                                    className="w-full mb-2 accent-[#20BF0E] h-2"
                                    id="progressSlider"
                                />
                            </div>

                            <h3 className="text-xl font-bold text-white mb-2">Script Generator</h3>
                            <p className="text-gray-400 text-sm mb-6">
                                AI writes full YouTube scripts based on your idea.
                            </p>
                        </div>
                        <button className="text-sm text-white py-2 flex items-center gap-2">
                            Try now <span ><Image src="/images/right.svg" alt="arrow-right" width={20} height={20} /></span>
                        </button>
                    </div>

                    <div className="col-span-12 md:col-span-5 bg-[#161616] rounded-2xl shadow-lg p-10 border border-[#BAFF381F]">
                        <ul className="relative space-y-4 text-sm text-gray-300 mb-8 h-[220px] overflow-hidden">
                            <li className="p-3 rounded-xl border border-[#BAFF381F]">
                                <p className="text-white text-[14px] flex items-center gap-2 font-medium mt-1"><Users className="w-4 h-4" /> Milestone unlocked: $500 in commissions!</p>
                                <p className="text-[#aaaca5] text-[10px] my-1">Congrats on hitting this major affiliate milestone</p>
                            </li>
                            <li className="p-3 rounded-xl border border-[#BAFF381F]">
                                <p className="text-white text-[14px] flex items-center gap-2 font-medium mt-1"><Users className="w-4 h-4" /> New commission earned!</p>
                                <p className="text-[#aaaca5] text-[10px] my-1">You’ve just earned $25 from a new referral</p>
                            </li>
                            <li className="p-3 rounded-xl border border-[#BAFF381F]">
                                <p className="text-white text-[14px] flex items-center gap-2 font-medium mt-1"><Users className="w-4 h-4" /> You aot your first referral</p>
                            </li>
                            <div className="absolute bottom-0 left-0 w-full h-14 bg-gradient-to-t from-[#161616] to-transparent pointer-events-none" />
                        </ul>

                        {/* Content */}
                        <div className="mb-7">
                            <h3 className="text-xl font-medium text-white my-2">Title Optimizer</h3>
                            <p className="text-[#AAACA6] text-[17px] my-4">
                                Get viral, high-CTR titles — created or improved by AI.
                            </p>
                        </div>

                        {/* Button */}
                        <button className="text-sm text-white py-2 flex items-center gap-2">
                            Try now <span ><Image src="/images/right.svg" alt="arrow-right" width={20} height={20} /></span>
                        </button>
                    </div>

                </div>
            </div>
            <div className=" bg-black flex items-center justify-center px-6">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 w-full">
                    {/* Left Card */}
                    <div className="col-span-12 md:col-span-5 bg-[#161616] rounded-2xl px-7 pt-14 border border-[#BAFF381F]">
                      
                        <div className="">
                            <p className="text-sm text-gray-400 flex items-center gap-2">
                                What’s your video about? <Info className="w-4 h-4" />
                            </p>
                            <div className="mt-3 bg-[#2d2e2d] text-gray-300 text-[12px] p-3 pb-10 rounded-xl">
                                A short video sharing 5 science-backed productivity hacks that help
                                better, and get more done with less effort.
                            </div>

                            <p className="text-sm text-white flex items-center gap-2 mt-7">
                                Tone / Style <Info className="w-4 h-4" />
                            </p>
                            <div className="flex gap-2 flex-wrap mt-4">
                                {["Controversial", "Shocking", "Persuasive", "Mysterious", "Dramatic"].map(
                                    (tone) => (
                                        <span
                                            key={tone}
                                            className="bg-[#232423] text-gray-300 text-[10px] px-3 py-1 rounded-full border border-[#323927]"
                                        >
                                            {tone}
                                        </span>
                                    )
                                )}
                            </div>
                        </div>
                        <div className="mt-8">
                            <h2 className="text-lg font-semibold text-white">
                                Affiliate Program
                            </h2>
                            <p className="text-[#a8aea4] text-[16px] mt-4">
                                Earn 50% lifetime revenue for every referred <br/>creator.
                            </p>
                            <button className="text-sm text-white mt-3 flex items-center gap-2">
                                Try now <span ><Image src="/images/right.svg" alt="arrow-right" width={20} height={20} /></span>
                            </button>
                        </div>
                    </div>

                    {/* Right Card */}
                    <div className="col-span-12 md:col-span-7 bg-[#161616] rounded-2xl p-6 flex flex-col justify-between border border-[#BAFF381F]">
                        <div className="w-full max-w-5xl rounded-2xl shadow-lg">
                            <div className="grid grid-cols-12 gap-5 mb-8">
                                {cards.map((card, idx) => (
                                    <div
                                        key={idx}
                                        className="rounded-xl col-span-12 md:col-span-6 overflow-hidden bg-[#1a1a1a] hover:bg-[#222] transition p-3 flex flex-col border border-[#BAFF381F]"
                                    >
                                        <div className="relative w-full h-40 rounded-lg overflow-hidden mb-3">
                                            <img
                                                src={card.img}
                                                alt={card.title}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>

                                        {/* Tags */}
                                        <div className="flex flex-wrap justify-between items-center text-xs text-gray-300 mb-2">
                                            <div className="bg-[#2a2a2a] p-2 rounded-md border border-[#BAFF381F]">
                                                {card.tags.map((tag, i) => (
                                                    <span
                                                        key={i}
                                                        className="rounded-md text-white"
                                                    >
                                                        {tag}
                                                        {i < card.tags.length - 1 && ", "}
                                                    </span>
                                                ))}
                                            </div>
                                            <ExternalLink className="w-5 h-5 cursor-pointer text-white" />
                                        </div>

                                        {/* Title */}
                                        <h3 className="text-white font-medium mb-1">{card.title}</h3>

                                        {/* Description */}
                                        <p className="text-[#959792] text-[12px] leading-snug">
                                            {card.desc}
                                        </p>
                                        <p className="text-[#959792] text-[12px] leading-snug mt-1">
                                            Examples: {card.example}
                                        </p>
                                    </div>
                                ))}
                            </div>
                            {/* Bottom Section */}
                            <div>
                                <h2 className="text-white text-xl font-semibold mb-1">
                                    Viral Niches Vault
                                </h2>
                                <p className="text-[#a8aea4] text-[16px] mt-4">
                                    Discover 300+ proven YouTube niches and grow faster.
                                </p>
                            </div>
                            <button className="text-sm text-white py-2 flex items-center gap-2">
                                Try now <span ><Image src="/images/right.svg" alt="arrow-right" width={20} height={20} /></span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default WhatsInside;
