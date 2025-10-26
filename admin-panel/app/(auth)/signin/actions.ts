'use server';

import { cookies } from 'next/headers';

export async function SetAccessToken(token: string) {
  const cookieStore = await cookies();
  cookieStore.set('access_token', token);
  return true;
}
