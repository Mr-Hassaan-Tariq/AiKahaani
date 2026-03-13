export function Marquee() {
  const logos = ['VidIQ', 'TubeBuddy', 'Canva', 'Veed.io', 'Descript', 'CapCut'];
  return (
    <div className="overflow-hidden border-y border-gray-200 bg-gray-100 py-12 dark:border-white/5 dark:bg-white/5">
      <div className="animate-marquee flex items-center justify-center gap-20 whitespace-nowrap">
        {logos.map((logo) => (
          <span
            key={logo}
            className="text-2xl font-black uppercase tracking-tighter text-gray-400 dark:text-gray-500"
          >
            {logo}
          </span>
        ))}
        {logos.map((logo) => (
          <span
            key={`${logo}-dup`}
            className="text-2xl font-black uppercase tracking-tighter text-gray-400 dark:text-gray-500"
          >
            {logo}
          </span>
        ))}
      </div>
    </div>
  );
}
