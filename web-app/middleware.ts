import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const token = request.cookies.get('access_token')?.value; // Read token from cookies

  // Pages that don't need authentication (e.g., signup, login)
  const publicPaths = ['/signup', '/login', '/magic-link'];

  // If no token and trying to access a protected route → redirect to signup
  // if (!token && !publicPaths.includes(path)) {
  //   const url = request.nextUrl.clone();
  //   url.pathname = '/signup';
  //   return NextResponse.redirect(url);
  // }

  // If token exists and user is trying to go to signup/login → redirect to home
  if (token && publicPaths.includes(path)) {
    const url = request.nextUrl.clone();
    url.pathname = '/';
    return NextResponse.redirect(url);
  }

  // Pass headers forward if needed
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('current_page', path);

  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

export const config = {
  matcher: '/((?!api|_next/static|_next/image|favicon.ico).*)', // Run on all pages except APIs and assets
};
