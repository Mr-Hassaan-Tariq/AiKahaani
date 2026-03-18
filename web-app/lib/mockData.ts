/**
 * Mock data for bypass mode (NEXT_PUBLIC_BYPASS_AUTH=true).
 * All API calls return data from here so UI can be reviewed without a backend.
 */

// ── User ─────────────────────────────────────────────────────────────────────
export const mockUser = {
  id: 1,
  email: 'demo@aikahani.com',
  username: 'demouser',
  fullname: 'Demo User',
  preferred_language: 'en',
  profile_picture: '',
  is_email_verified: true,
};

// ── Notifications ─────────────────────────────────────────────────────────────
export const mockNotifications = [
  {
    id: 1,
    title: 'Script generated successfully',
    message: 'Your script "Top 10 Productivity Hacks" has been generated and is ready to review.',
    read: false,
    created_at: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
    metadata: {},
  },
  {
    id: 2,
    title: 'New feature: Niche Vault',
    message: 'Explore hundreds of proven YouTube content styles in the all-new Niche Vault.',
    read: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    metadata: {},
  },
  {
    id: 3,
    title: 'Outline saved',
    message: 'Your outline "Morning Routine for Creators" was saved to My Scripts.',
    read: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    metadata: {},
  },
  {
    id: 4,
    title: 'Plan renewal reminder',
    message: 'Your Pro plan renews in 3 days. No action needed.',
    read: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    metadata: {},
  },
];

export const mockNotificationSettings = {
  in_app_notifications: true,
  email_notifications: true,
  web_push_notifications: false,
  new_script_generated: true,
  account_or_plan_changes: true,
  tips_content_inspiration: false,
  feature_updates: true,
};

export const mockPrivacySettings = {
  allow_product_update_emails: true,
  allow_anonymized_data_usage: false,
};

// ── Script config (tones + template styles + length range) ────────────────────
export const mockScriptConfig = {
  tones: [
    { id: 1, name: 'Casual' },
    { id: 2, name: 'Professional' },
    { id: 3, name: 'Educational' },
    { id: 4, name: 'Humorous' },
    { id: 5, name: 'Inspirational' },
    { id: 6, name: 'Storytelling' },
  ],
  template_styles: [
    {
      id: 1,
      name: 'Short-form',
      min_length: 300,
      max_length: 800,
      duration: 3,
      description: 'Concise scripts perfect for YouTube Shorts or quick tips.',
      word_range: '300–800 words',
    },
    {
      id: 2,
      name: 'Standard',
      min_length: 800,
      max_length: 1500,
      duration: 8,
      description: 'Balanced length for most YouTube videos.',
      word_range: '800–1500 words',
    },
    {
      id: 3,
      name: 'Long-form',
      min_length: 1500,
      max_length: 3000,
      duration: 15,
      description: 'In-depth scripts for tutorials, documentaries and deep-dives.',
      word_range: '1500–3000 words',
    },
  ],
  length_range: { min: 300, max: 3000, default: 1000 },
};

// ── Title styles ──────────────────────────────────────────────────────────────
export const mockTitleStyles = {
  results: [
    { id: 1, name: 'Clickbait' },
    { id: 2, name: 'How-To' },
    { id: 3, name: 'Listicle' },
    { id: 4, name: 'Question' },
    { id: 5, name: 'Emotional' },
    { id: 6, name: 'Contrarian' },
    { id: 7, name: 'Story' },
    { id: 8, name: 'Curiosity Gap' },
  ],
  template_styles: mockScriptConfig.template_styles,
  length_range: mockScriptConfig.length_range,
};

// ── Scripts (my-scripts) ──────────────────────────────────────────────────────
export const mockScripts = {
  results: [
    {
      uuid: 'mock-script-1',
      title: 'Top 10 Productivity Hacks for Creators',
      outline_title: null,
    },
    {
      uuid: 'mock-script-2',
      title: 'How to Build a Morning Routine That Sticks',
      outline_title: null,
    },
    {
      uuid: 'mock-script-3',
      title: 'Why Most YouTubers Fail in Their First Year',
      outline_title: null,
    },
  ],
  count: 3,
  next: null,
  previous: null,
};

export const mockScriptGenerations = [
  {
    uuid: 'mock-gen-1',
    title: 'Top 5 Productivity Hacks That Actually Work',
    type: 'script' as const,
    status: 'generated' as const,
    status_display: 'Generated',
    word_count: 1400,
    estimated_duration: 5,
    section_count: null,
    created: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    modified: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    is_published: false,
    version: 1,
  },
  {
    uuid: 'mock-gen-2',
    title: 'How AI is Changing Web Design in 2025',
    type: 'outline' as const,
    status: 'generated' as const,
    status_display: 'Generated',
    word_count: null,
    estimated_duration: null,
    section_count: 8,
    created: new Date(Date.now() - 1000 * 60 * 60 * 30).toISOString(),
    modified: new Date(Date.now() - 1000 * 60 * 60 * 30).toISOString(),
    is_published: null,
    version: 1,
  },
  {
    uuid: 'mock-gen-3',
    title: 'My Morning Routine as a Tech Creator',
    type: 'script' as const,
    status: 'generated' as const,
    status_display: 'Generated',
    word_count: 2800,
    estimated_duration: 10,
    section_count: null,
    created: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    modified: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    is_published: false,
    version: 1,
  },
  {
    uuid: 'mock-gen-4',
    title: "Beginner's Guide to Starting a YouTube Channel",
    type: 'outline' as const,
    status: 'generated' as const,
    status_display: 'Generated',
    word_count: null,
    estimated_duration: null,
    section_count: 12,
    created: new Date(Date.now() - 1000 * 60 * 60 * 24 * 6).toISOString(),
    modified: new Date(Date.now() - 1000 * 60 * 60 * 24 * 6).toISOString(),
    is_published: null,
    version: 1,
  },
  {
    uuid: 'mock-gen-5',
    title: 'Why Most YouTubers Quit After 6 Months',
    type: 'script' as const,
    status: 'generated' as const,
    status_display: 'Generated',
    word_count: 1950,
    estimated_duration: 7,
    section_count: null,
    created: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
    modified: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
    is_published: false,
    version: 2,
  },
  {
    uuid: 'mock-gen-6',
    title: 'The Ultimate Guide to YouTube SEO in 2025',
    type: 'outline' as const,
    status: 'generated' as const,
    status_display: 'Generated',
    word_count: null,
    estimated_duration: null,
    section_count: 10,
    created: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
    modified: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
    is_published: null,
    version: 1,
  },
];

// ── Niches ────────────────────────────────────────────────────────────────────
export const mockNiches = {
  count: 9,
  next: null,
  previous: null,
  results: [
    {
      id: 1,
      admin: 1,
      title: 'True Crime Storytelling',
      tagline: 'Engaging, anonymous, and binge-worthy. Narrate without showing your face.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'Hook with the most shocking moment, then zoom out.',
        body: 'Chronological retelling with dramatic reveals.',
        outro: 'Unresolved questions to drive comments and return views.',
      },
      tone: ['Mysterious', 'Dramatic'],
      pacing: ['Slow build', 'Cliff-hanger endings'],
      top_channels: [
        { name: 'CriminallyListed', link: 'https://youtube.com' },
        { name: 'Stephanie Harlowe', link: 'https://youtube.com' },
      ],
      best_for: ['Faceless channels', 'Voiceover creators', 'Storytellers'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      admin: 1,
      title: 'Personal Finance & Investing',
      tagline: 'Help everyday people build wealth and escape the 9-to-5.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'Relatable money problem or shocking stat.',
        body: 'Step-by-step actionable advice with real numbers.',
        outro: 'Call to action: subscribe for weekly money tips.',
      },
      tone: ['Educational', 'Conversational'],
      pacing: ['Steady', 'Data-driven'],
      top_channels: [
        { name: 'Andrei Jikh', link: 'https://youtube.com' },
        { name: 'Graham Stephan', link: 'https://youtube.com' },
      ],
      best_for: ['Finance educators', 'Side-hustle creators', 'Investment coaches'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 3,
      admin: 1,
      title: 'Tech Reviews & Comparisons',
      tagline: 'Cut through the noise — give viewers the real verdict on gadgets.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'State the product and bold claim upfront.',
        body: 'Hands-on breakdown: design, performance, value.',
        outro: 'Final verdict and who it is for.',
      },
      tone: ['Professional', 'Opinionated'],
      pacing: ['Fast-paced', 'Visual-heavy'],
      top_channels: [
        { name: 'Marques Brownlee', link: 'https://youtube.com' },
        { name: 'Linus Tech Tips', link: 'https://youtube.com' },
      ],
      best_for: ['Tech enthusiasts', 'Affiliate marketers', 'Gear reviewers'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 4,
      admin: 1,
      title: 'Self-Improvement & Mindset',
      tagline: 'Inspire audiences to become the best version of themselves.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'A personal story or provocative question.',
        body: 'Frameworks, habits, and research-backed insights.',
        outro: 'Challenge the viewer to take one action today.',
      },
      tone: ['Inspirational', 'Empathetic'],
      pacing: ['Reflective', 'Motivational peaks'],
      top_channels: [
        { name: 'Matt D\'Avella', link: 'https://youtube.com' },
        { name: 'Thomas Frank', link: 'https://youtube.com' },
      ],
      best_for: ['Life coaches', 'Minimalism creators', 'Wellness educators'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 5,
      admin: 1,
      title: 'AI & Future of Work',
      tagline: 'Decode AI trends for everyday people worried about their careers.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'Breaking news angle or bold prediction.',
        body: 'Explain the tech simply, then impact on jobs/life.',
        outro: 'How to stay ahead — practical next steps.',
      },
      tone: ['Educational', 'Forward-thinking'],
      pacing: ['Snappy', 'News-style'],
      top_channels: [
        { name: 'AI Explained', link: 'https://youtube.com' },
        { name: 'Two Minute Papers', link: 'https://youtube.com' },
      ],
      best_for: ['Tech writers', 'AI educators', 'Career coaches'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 6,
      admin: 1,
      title: 'Fitness & Health',
      tagline: 'Science-backed workouts and nutrition advice for real people.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'Myth-bust a common fitness belief.',
        body: 'Evidence-based tips with demonstration cues.',
        outro: 'Free plan or checklist as lead magnet.',
      },
      tone: ['Energetic', 'Encouraging'],
      pacing: ['High energy', 'Action-oriented'],
      top_channels: [
        { name: 'Jeff Nippard', link: 'https://youtube.com' },
        { name: 'AthleanX', link: 'https://youtube.com' },
      ],
      best_for: ['Personal trainers', 'Nutrition coaches', 'Gym creators'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 7,
      admin: 1,
      title: 'Travel & Experiences',
      tagline: 'Take viewers to places they\'ve never been — without leaving home.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'Cinematic scene-setting: drop them in the location.',
        body: 'Practical tips woven into the experience narrative.',
        outro: 'One thing viewers can do to plan their own trip.',
      },
      tone: ['Adventurous', 'Vivid'],
      pacing: ['Immersive', 'Episodic'],
      top_channels: [
        { name: 'Mark Wiens', link: 'https://youtube.com' },
        { name: 'Lost LeBlancs', link: 'https://youtube.com' },
      ],
      best_for: ['Digital nomads', 'Travel bloggers', 'Luxury travel reviewers'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 8,
      admin: 1,
      title: 'History & Documentaries',
      tagline: 'Make history feel urgent, relevant, and impossible to skip.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'Why this historical moment matters right now.',
        body: 'Character-driven narrative with vivid details.',
        outro: 'Lesson for today drawn from the past.',
      },
      tone: ['Authoritative', 'Storytelling'],
      pacing: ['Epic build', 'Deliberate'],
      top_channels: [
        { name: 'Overly Sarcastic Productions', link: 'https://youtube.com' },
        { name: 'Toldinstone', link: 'https://youtube.com' },
      ],
      best_for: ['History enthusiasts', 'Documentary makers', 'Educators'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
    {
      id: 9,
      admin: 1,
      title: 'Business & Entrepreneurship',
      tagline: 'Real strategies for building a business from zero to revenue.',
      thumbnail_url: null,
      thumbnail: null,
      script_structure: {
        intro: 'A failed business lesson or counterintuitive insight.',
        body: 'Step-by-step breakdown with real case studies.',
        outro: 'Free resource or invite to community.',
      },
      tone: ['Direct', 'Tactical'],
      pacing: ['No-fluff', 'Value-dense'],
      top_channels: [
        { name: 'Alex Hormozi', link: 'https://youtube.com' },
        { name: 'My First Million', link: 'https://youtube.com' },
      ],
      best_for: ['Founders', 'Side-hustle creators', 'Business coaches'],
      status: 'active',
      created: '2024-01-01T00:00:00Z',
      modified: '2024-01-01T00:00:00Z',
    },
  ],
};

// ── Mock outline ─────────────────────────────────────────────────────────────
export const mockOutline = {
  uuid: 'mock-outline-1',
  title: 'Top 10 Productivity Hacks for Creators',
  description: 'A fast-paced, actionable guide covering the top productivity habits that actually work for YouTube creators who struggle with focus and consistency.',
  tones: [{ id: 4, name: 'Fast-paced' }, { id: 1, name: 'Casual' }],
  template_style: undefined,
  min_length: 800,
  max_length: 1500,
  outline_text: '',
  section_order: [0, 1, 2, 3, 4, 5, 6],
  outline_data: {
    sections: [
      {
        title: 'Intro Hook',
        description: 'Open with a relatable frustration about wasted hours and tease a simple framework viewers can use immediately.',
        key_points: ['Relatable pain point', 'Bold promise', 'Tease the list'],
        timing: '0:00 – 0:45',
        transition: 'Cut to the first hack with energy.',
      },
      {
        title: 'Hack #1 — The 2-Minute Rule',
        description: 'Show how completing tiny tasks instantly creates momentum and reduces mental clutter early in the day.',
        key_points: ['Define the rule', 'Real creator examples', 'Quick win'],
        timing: '0:45 – 2:00',
        transition: 'Bridge to time blocking with a contrast.',
      },
      {
        title: 'Hack #2 — Time Blocking',
        description: 'Explain how assigning focused time windows stops constant task switching and protects deep work sessions.',
        key_points: ['Calendar blocking demo', 'Avoid context switching', 'Deep work zones'],
        timing: '2:00 – 3:30',
        transition: 'Lead into "eating the frog" concept.',
      },
      {
        title: 'Hack #3 — Eat the Frog',
        description: 'Frame the hardest task as the highest-leverage move of the day and connect it to confidence and consistency.',
        key_points: ['What is the frog?', 'First thing every morning', 'Confidence loop'],
        timing: '3:30 – 5:00',
        transition: 'Shift to batching for efficiency.',
      },
      {
        title: 'Hack #4 — Batch Similar Tasks',
        description: 'Group repetitive work together so the viewer sees a practical way to cut context switching and regain momentum.',
        key_points: ['Editing batches', 'Thumbnail day', 'Email sprints'],
        timing: '5:00 – 6:30',
        transition: 'Introduce Pomodoro as the time tool.',
      },
      {
        title: 'Hack #5 — Pomodoro Focus Sprint',
        description: 'Introduce work sprints with intentional breaks to help creators maintain intensity without burning out.',
        key_points: ['25/5 rule', 'Apps to try', 'Energy management'],
        timing: '6:30 – 8:00',
        transition: 'Wind down into the recap.',
      },
      {
        title: 'Recap & CTA',
        description: 'End with a quick summary, challenge viewers to try one habit today, and invite them to comment their favorite hack.',
        key_points: ['Summarize all 5 hacks', 'One-action challenge', 'Subscribe CTA'],
        timing: '8:00 – 9:00',
        transition: '',
      },
    ],
  },
  status: 'generated',
  version: 1,
  tokens_used: 420,
  generation_time: 3.2,
  created: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  modified: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
};

export const mockOutlineResponse = {
  outline: mockOutline,
  message: 'Outline generated successfully',
  status: 'success',
};

// ── Mock script ───────────────────────────────────────────────────────────────
export const mockScript = {
  uuid: 'mock-script-gen-1',
  title: 'Top 10 Productivity Hacks for Creators',
  outline_title: 'Top 10 Productivity Hacks for Creators',
  content: 'Full script content — see sections below.',
  sections: [
    {
      title: 'Intro Hook',
      timeRange: '0:00 \u2013 0:45',
      content: "Hey everyone, welcome back. If you're watching this, you've probably had at least one day where you sat down to work and somehow ended up doing nothing meaningful for hours. I've been there.\n\nToday I'm breaking down five productivity hacks that actually work for creators. No fluff. No productivity-guru jargon. Just the stuff that moved the needle.",
    },
    {
      title: 'Hack #1 \u2014 The 2-Minute Rule',
      timeRange: '0:45 \u2013 2:00',
      content: "Here's the deal: if a task takes less than two minutes, do it right now. Don't add it to a list. Don't schedule it. Just do it.\n\nReply to that DM. Rename that clip. Send that follow-up email. The backlog of tiny tasks is a silent productivity killer.\n\nClear the clutter, and your brain suddenly has space to go deep.",
    },
    {
      title: 'Hack #2 \u2014 Time Blocking',
      timeRange: '2:00 \u2013 3:30',
      content: 'Stop using a to-do list as your only system. A list tells you what to do but not when. Time blocking fixes that.\n\nBlock actual calendar time for deep work. When editing is on the calendar from 9 to 11, that slot is sacred. Context switching is the enemy of output.\n\nTime blocking is the shield that protects your deep work.',
    },
    {
      title: 'Hack #3 \u2014 Eat the Frog',
      timeRange: '3:30 \u2013 5:00',
      content: "Your frog is the task you've been dreading. The script you've been procrastinating. The thumbnail redesign you keep pushing back. Do it first.\n\nThe confidence you build by crushing the hardest thing before 10am is addictive. It proves to yourself that you're capable, and it resets the energy of your entire day.",
    },
    {
      title: 'Hack #4 \u2014 Batch Similar Tasks',
      timeRange: '5:00 \u2013 6:30',
      content: "Film all your B-roll in one session. Create all your thumbnails on Thursday. Answer all your comments in one 20-minute block.\n\nBatching works because every time you switch task types, you pay a cognitive tax.\n\nGroup similar work together and you'll get into a flow state faster, stay there longer, and produce higher quality output in less time.",
    },
    {
      title: 'Hack #5 \u2014 Pomodoro Focus Sprints',
      timeRange: '6:30 \u2013 8:00',
      content: "Work for 25 minutes. Break for 5. Repeat four times, then take a longer 20-minute break.\n\nIt sounds almost too simple, but the timer creates urgency, and urgency creates output. You're not sitting down to work on the script for hours. You're sitting down for exactly 25 minutes. That specificity is powerful.",
    },
    {
      title: 'Recap & CTA',
      timeRange: '8:00 \u2013 9:00',
      content: "That's five hacks. The 2-Minute Rule to clear mental clutter. Time Blocking to protect deep work. Eat the Frog to build morning momentum. Task Batching to stay in flow. And Pomodoro Sprints to create urgency.\n\nPick one. Try it this week. Drop a comment below telling me which one you're going to test.\n\nIf this helped, hit subscribe. I post practical creator systems every week. See you in the next one.",
    },
  ],
  word_count: 320,
  estimated_duration: 9,
  status: 'generated',
  version: 1,
  is_published: false,
  tokens_used: 780,
  generation_time: 6.4,
  created: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  modified: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
};

export const mockGenerateScriptResponse = {
  script: mockScript,
  message: 'Script generated successfully',
};

// ── Endpoint → mock data map ───────────────────────────────────────────────────
export function getMockDataForEndpoint(endpoint: string): unknown {
  if (endpoint.includes('users/details')) return mockUser;
  if (endpoint.includes('users/notifications')) return mockNotificationSettings;
  if (endpoint.includes('notifications/all-notifications')) {
    return { results: mockNotifications, count: mockNotifications.length, next: null, previous: null };
  }
  if (endpoint.includes('privacy')) return mockPrivacySettings;
  if (endpoint.includes('scripts/config')) return mockScriptConfig;
  if (endpoint.includes('scripts/titles/tones')) return mockTitleStyles;
  if (endpoint.includes('scripts/outlines/') && endpoint.includes('/script/')) return mockGenerateScriptResponse;
  if (endpoint.includes('scripts/outlines/')) return mockOutline;
  // Script generations list: v1/scripts/generations/
  if (endpoint.includes('scripts/generations')) {
    return { count: mockScriptGenerations.length, results: mockScriptGenerations, next: null, previous: null };
  }
  // Single script fetch by any mock uuid
  if (endpoint.includes('scripts/mock-script-gen-1') || endpoint.includes('scripts/mock-gen-')) return mockScript;
  if (endpoint.includes('scripts/') && !endpoint.includes('config') && !endpoint.includes('titles')) {
    return mockScripts;
  }
  if (endpoint.includes('niches')) return mockNiches;
  // fallback
  return null;
}

// ── Mock generated titles ─────────────────────────────────────────────────────
export const mockGeneratedTitles = {
  titles: [
    '7 Focus Habits That Made Me Finish Work Twice as Fast',
    "Can't Focus? These 7 Habits Fix Your Study Sessions",
    '7 Focus Habits Every Student Should Start This Week',
    'I Tried 7 Focus Habits for 30 Days — Here\'s What Worked',
    'Stop Wasting Time: 7 Focus Habits That Actually Stick',
    'The 7-Habit Focus System That Killed My Procrastination',
  ],
};

// ── POST endpoint → mock data map ─────────────────────────────────────────────
export function getMockPostDataForEndpoint(endpoint: string): unknown {
  if (endpoint.includes('scripts/outline/') && endpoint.includes('/script/')) {
    return mockGenerateScriptResponse;
  }
  if (endpoint.includes('scripts/outline/')) return mockOutlineResponse;
  if (endpoint.includes('titles/generate') || endpoint.includes('titles/optimize')) {
    return mockGeneratedTitles;
  }
  // For update/patch endpoints just return a success
  return { status: 'ok', message: 'Success' };
}
