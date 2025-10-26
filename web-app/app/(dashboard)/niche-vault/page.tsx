'use client';

import { useState } from 'react';
import Image1 from 'public/images/card1.png';
import Image2 from 'public/images/card2.png';
import Image3 from 'public/images/card3.png';
import Image4 from 'public/images/card4.png';
import Image5 from 'public/images/card5.png';
import Image6 from 'public/images/card6.png';

import NicheCard from './_components/NicheCard';
import SearchHeader from './_components/SearchHeader';

const data = [
  {
    image: Image1,
    title: 'Storytelling',
    description: 'Narrative-driven scripts built around tension, reveals, and emotion.',
    tags: ['Engaging', 'Emotional', 'Suspenseful'],
    examples: ['MrBeast', 'Yes Theory', 'Nas Daily'],
  },
  {
    image: Image2,
    title: 'Elon Musk-style',
    description: 'Concise, bold, future-focused scripts that spark curiosity and debate.',
    tags: ['Bold', 'Futuristic', 'Concise'],
    examples: ['ColdFusion', 'Tech Vision', 'Moon'],
  },
  {
    image: Image3,
    title: 'Donald Trump-style',
    description: 'Confrontational, polarizing, and direct — perfect for viral commentary.',
    tags: ['Direct', 'Viral', 'Polarizing'],
    examples: ['The Quartering', 'Tim Pool', 'Valuetainment'],
  },
  {
    image: Image4,
    title: 'Product Review',
    description: 'Persuasive structure with pros, cons, and clear verdict.',
    tags: ['Clear', 'Helpful', 'Persuasive'],
    examples: ['Marques Brownlee', 'iJustine'],
  },
  {
    image: Image5,
    title: 'Travel Vlog',
    description: 'Scripts built for immersive visuals and cinematic storytelling.',
    tags: ['Immersive', 'Cinematic', 'Warm'],
    examples: ['Kara and Nate', 'Lost LeBlanc', 'Indigo Traveller'],
  },
  {
    image: Image6,
    title: 'Listicle / Top 10',
    description: 'Perfect for countdowns and compilations, with structured delivery.',
    tags: ['Structured', 'Snappy', 'Fun'],
    examples: ['WatchMojo', 'TopTenZ', 'Bright Side'],
  },
];

export default function NicheVault() {
  const [searchInput, setSearchInput] = useState('');

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  return (
    <main>
      <SearchHeader searchInput={searchInput} handleSearchChange={handleSearchChange} />
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {data.map((style, i) => (
          <NicheCard key={i} {...style} />
        ))}
      </div>
    </main>
  );
}
