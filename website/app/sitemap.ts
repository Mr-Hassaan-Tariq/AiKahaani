import { MetadataRoute } from 'next';

import { SITE_URL } from 'lib/seo';

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = ['/pricing', '/terms', '/privacy', '/refund', '/contact'];
  return [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1,
    },
    ...routes.map((route) => ({
      url: `${SITE_URL}${route}`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.7,
    })),
  ];
}
