import Link from 'next/link';

async function NotFound() {
  await new Promise((resolve) => setTimeout(resolve, 3000));

  return (
    <div className="flex h-[100dvh] flex-col items-center justify-center gap-10 px-4">
      <div className="text-5xl font-extrabold text-green-800">Not Found</div>
      <div className="text-center text-xl tracking-[8px] text-green-800">
        Sorry, This page does not exist
      </div>
      <Link href="/">
        <button className="rounded-full bg-green-800 px-4 py-2 text-white">Go to Home</button>
      </Link>
    </div>
  );
}

export default NotFound;
