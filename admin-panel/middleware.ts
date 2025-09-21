import { NextRequest, NextResponse } from 'next/server';

// const publicPaths = ['/signup', '/magic-link'];

export async function middleware(request: NextRequest) {
  // const path = request.nextUrl.pathname;
  // const token = request.cookies.get('access_token')?.value; // Read token from cookies

  // // Pages that don't need authentication (e.g., signup, login)

  // // If no token and trying to access a protected route → redirect to signup
  // if (!token && !publicPaths.includes(path)) {
  //   const redirectUrl = `/signup${request.nextUrl.search || ''}`;
  //   return NextResponse.redirect(new URL(redirectUrl, request.url));
  // }

  // // If token exists and user is trying to go to signup/login → redirect to home
  // if (token && publicPaths.includes(path)) {
  //   const url = request.nextUrl.clone();
  //   url.pathname = '/';
  //   return NextResponse.redirect(url);
  // }

  // Pass headers forward if needed
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('current_page', request.nextUrl.pathname);

  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

export const config = {
  matcher: '/((?!api|_next/static|_next/image|favicon.ico).*)', // Run on all pages except APIs and assets
};
