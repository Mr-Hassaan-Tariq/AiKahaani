import { env } from 'env.mjs';

export const COOKIE_NAME = 'user-token';
// export const WEB_APP_URL = 'https://web-app-production-495a.up.railway.app';
export const WEB_APP_URL = env.NEXT_PUBLIC_WEBSITE_URL;
