'use server';

import { cookies } from 'next/headers';

const COOKIE_OPTS = {
  httpOnly: false, // must be readable by js-cookie on the client
  sameSite: 'lax' as const,
  path: '/',
  secure: process.env.NODE_ENV === 'production',
};

export async function SetAccessToken(token: string) {
  const cookieStore = await cookies();
  // Access tokens typically expire in 15 min; keep the cookie for 1 day so
  // the refresh flow can replace it before the cookie itself disappears.
  cookieStore.set('access_token', token, { ...COOKIE_OPTS, maxAge: 60 * 60 * 24 });
  return true;
}

export async function SetAuthTokens(accessToken: string, refreshToken: string) {
  const cookieStore = await cookies();
  cookieStore.set('access_token', accessToken, { ...COOKIE_OPTS, maxAge: 60 * 60 * 24 });
  cookieStore.set('refresh_token', refreshToken, { ...COOKIE_OPTS, maxAge: 60 * 60 * 24 * 30 });
  return true;
}
