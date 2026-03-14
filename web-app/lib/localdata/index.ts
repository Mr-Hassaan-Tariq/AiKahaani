import Draft from '@assets/svg/draft.svg';
import Magicpan from '@assets/svg/magicpan.svg';

export const notificationTexts = {
  deliveryChannels: {
    title: 'Delivery channels',
    options: [
      {
        label: 'Email notifications',
        key: 'email_notifications',
        description:
          "You'll receive updates about your scripts, account, and new features via email.",
      },
      {
        label: 'In-app notifications',
        key: 'in_app_notifications',
        description: 'See notifications directly in your AiKahani.',
      },
      {
        label: 'Web push notifications (coming soon)',
        key: 'web_push_notifications',
        description: "Get real-time alerts even when you're not on the platform.",
      },
    ],
  },
  notificationTypes: {
    title: 'Notification types',
    options: [
      {
        label: 'New script generated',
        key: 'new_script_generated',
      },
      {
        label: 'Account or plan changes',
        key: 'account_or_plan_changes',
      },
      {
        label: 'Tips & content inspiration',
        key: 'tips_content_inspiration',
      },
      {
        label: 'Feature updates',
        key: 'feature_updates',
      },
    ],
  },
};

export const notificationData = [
  {
    title: "New niche added: 'Listicle with a Twist'",
    description: 'Perfect for countdown videos with a unique hook',
    time: '1d ago',
    actionText: 'Use this style',
    actionLink: '#',
    isNew: true,
    icon: Magicpan,
  },
  {
    title: '2 unfinished scripts waiting',
    description: 'Pick up where you left off',
    time: '1d ago',
    actionText: 'Go to drafts',
    actionLink: '#',
    icon: Draft,
  },
  {
    title: "Trending format: 'Conspiracy Shorts'",
    description: 'Optimized for short-form storytelling',
    time: '1d ago',
    actionText: 'Explore now',
    actionLink: '#',
    isNew: true,
    icon: Magicpan,
  },
  {
    title: 'Script Generator update',
    description: 'Now supports 12 new viral tones!',
    time: '2d ago',
    actionText: 'Explore in your next draft',
    actionLink: '#',
    icon: Magicpan,
  },
  {
    title: 'New: Title Generator',
    description: 'Generate viral titles in seconds',
    time: '3d ago',
    actionText: 'Try now',
    actionLink: '#',
    icon: Magicpan,
  },
  {
    title: 'Trial plan ends in 3 days',
    description: 'Make the most of your access',
    time: '4d ago',
    actionText: 'Upgrade plan',
    actionLink: '#',
    icon: Magicpan,
  },
];
