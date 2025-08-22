import { affiliatesRightSide, homeRightSide, partnerRightSide } from 'components/ui/components';

export const successStories = [
  {
    id: 1,
    name: '@FoodieTravels',
    subscribers: '673K subscribers',
    category: 'Food & Travel',
    title: 'My Secret to Consistent Uploads',
    description: 'Reduced content preparation time by 3x thanks to ready-to-use scripts.',
    image: '/images/tech-tinker.jpg',
  },
  {
    id: 2,
    name: '@TechTinker',
    subscribers: '482K subscribers',
    category: 'Tech, productivity',
    title: "How I 10x'd my YouTube growth in 3 months",
    description: 'Increased views by 320% after optimizing scripts with TubeGenius.',
    image: '/images/tech-tinker.jpg',
  },
  {
    id: 3,
    name: '@FitWithNina',
    subscribers: '1.2M subscribers',
    category: 'Fitness & Lifestyle',
    title: 'From Hobby to Full-Time Creator',
    description: 'Achieved 5 viral videos within the first 2 months using TubeGenius.',
    image: '/images/fit-with-nina.jpg',
  },
  {
    id: 4,
    name: '@CreativeStudio',
    subscribers: '890K subscribers',
    category: 'Creative & Design',
    title: 'Scaling Content Creation',
    description: 'Streamlined my creative process and doubled my upload frequency.',
    image: '/images/creative-studio.jpg',
  },
  {
    id: 5,
    name: '@GameMaster',
    subscribers: '1.5M subscribers',
    category: 'Gaming',
    title: 'Breaking Through the Algorithm',
    description: 'Optimized video scripts led to 500% increase in engagement rates.',
    image: '/images/game-master.jpg',
  },
];

export const questions = [
  {
    id: 1,
    question: 'Do I need any video editing or scripting experience?',
    answer:
      'Not at all. TubeGenius is beginner-friendly. You simply choose your format, answer a few prompts, and our AI delivers a ready-to-use script and title suggestions.',
  },
  {
    id: 2,
    question: 'Can I customize the AI-generated scripts?',
    answer:
      'Not at all. TubeGenius is beginner-friendly. You simply choose your format, answer a few prompts, and our AI delivers a ready-to-use script and title suggestions.',
  },
  {
    id: 3,
    question: 'How does the Affiliate Program work?',
    answer:
      'Not at all. TubeGenius is beginner-friendly. You simply choose your format, answer a few prompts, and our AI delivers a ready-to-use script and title suggestions.',
  },
  {
    id: 4,
    question: 'Can I cancel my subscription anytime?',
    answer:
      'Not at all. TubeGenius is beginner-friendly. You simply choose your format, answer a few prompts, and our AI delivers a ready-to-use script and title suggestions.',
  },
];

export const footerData = [
  {
    label: 'Privacy Policy',
    id: 'privacy-policy',
  },
  {
    label: 'Terms of Service',
    id: 'terms-of-service',
  },
  {
    label: 'Contact',
    id: 'contact',
  },
];

export const navItems = [
  {
    label: 'How it works',
    id: 'how-it-works',
    ref: ['/', '/affiliates'],
  },
  {
    label: 'About partner',
    id: 'about-partner',
    ref: ['/about-partner'],
  },
  {
    label: 'Platform',
    id: 'platform',
    ref: ['/about-partner'],
  },
  {
    label: 'Benefits',
    id: 'benefits',
    ref: ['/affiliates', '/about-partner'],
  },
  {
    label: 'Target audience',
    id: 'target-audience',
    ref: ['/affiliates'],
  },

  {
    label: 'Features',
    id: 'features',
    ref: ['/'],
  },
  {
    label: 'Success stories',
    id: 'success-stories',
    ref: ['/', '/about-partner'],
  },
  {
    label: 'Affiliates',
    id: 'affiliates',
    link: '/affiliates',
    ref: ['/', '/about-partner'],
  },
  {
    label: 'FAQ',
    id: 'faq',
    ref: ['/affiliates', '/about-partner'],
  },
];

export const heroSectionContent = {
  home: {
    rightSection: homeRightSide,
    btnLabel: 'Get Started',
    label: 'No sign-up hassle. Just your YouTube idea.',
    title: 'Your Genius AI Assistant for YouTube',
    description:
      'Turn your video ideas into ready-to-use scripts, titles, and niche insights — in seconds.',
  },
  partner: {
    rightSection: partnerRightSide,
    btnLabel: 'Start for $1',
    label: 'Official TubeGenius Partner',
    title: 'Unlock Your YouTube Potential with [Partner Name]',
    description:
      'Join TubeGenius through this exclusive partnership and start your journey for just $1.',
  },
  affiliates: {
    rightSection: affiliatesRightSide,
    btnLabel: 'Join with your email',
    label: 'Try TubeGenius for just $1 and start earning today',
    title: 'Earn with TubeGenius. Share AI video creation',
    description:
      'Join our affiliate program and get paid for helping creators script better videos with AI.',
  },
};
