import { Script, ScriptStatus, TabConfig } from '../_types';

export const MOCK_SCRIPTS: Script[] = [
  {
    id: '1',
    title: 'Top 5 productivity hacks that actually work',
    status: 'Outline only' as ScriptStatus,
    lastEdited: 'July 17, 2025',
    duration: '20 min',
    wordCount: '2.6k words',
    mode: 'outline',
  },
  {
    id: '2',
    title: "Beginner's guide to video SEO",
    status: 'Completed' as ScriptStatus,
    lastEdited: 'July 10, 2025',
    duration: '35 min',
    wordCount: '4.2k words',
    mode: 'script',
  },
  {
    id: '3',
    title: 'How to grow your YouTube channel in 2025',
    status: 'Script in progress' as ScriptStatus,
    lastEdited: 'July 14, 2025',
    duration: '40 min',
    wordCount: '5.5k words',
    mode: 'script',
  },
];

export const TABS_CONFIG: TabConfig[] = [
  { label: 'All', path: '/my-scripts' },
  { label: 'Outlines', path: '/my-scripts?query=outlines', query: 'outlines' },
  { label: 'Scripts', path: '/my-scripts?query=scripts', query: 'scripts' },
] as const;

export const SEARCH_PLACEHOLDER = 'Search by title or topic';

export const EMPTY_STATES = {
  scripts: {
    title: 'No scripts yet.',
    description:
      'Already have an outline? <br/> Turn it into a full script and keep refining it here.',
  },
  outlines: {
    title: 'No outlines yet.',
    description: 'Ready to begin? <br/> Generate an outline and turn it into a full script later.',
  },
  all: {
    title: 'No scripts found',
    description: 'Start creating your first script or outline to get started.',
  },
} as const;
