const steps = [
  {
    number: '1',
    title: 'Describe your next video',
    description:
      'Briefly explain what you want your video to be about. The more detail, the better.',
  },
  {
    number: '2',
    title: 'Pick structure and tone',
    description:
      'Choose from proven YouTube structures (Educational, Storytelling, Hype) and set your voice.',
  },
  {
    number: '3',
    title: 'Generate and refine',
    description:
      'Get a full script in seconds. Use our editor to tweak and finalize your masterpiece.',
  },
];

export function Steps() {
  return (
    <section
      id="how-it-works"
      className="relative bg-gray-50 px-6 py-24 transition-colors duration-300 dark:bg-[#0a0a0a]"
    >
      <div className="absolute bottom-0 left-1/2 h-[1px] w-full -translate-x-1/2 bg-gradient-to-r from-transparent via-gray-200 to-transparent dark:via-white/10" />

      <div className="container mx-auto max-w-7xl space-y-16 text-center">
        <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-6xl">
          From idea to upload plan in 3 steps
        </h2>

        <div className="relative grid grid-cols-1 gap-12 pt-8 md:grid-cols-3">
          <div className="absolute left-1/4 right-1/4 top-[70px] z-0 hidden h-[2px] bg-gray-200 dark:bg-white/5 md:block" />

          {steps.map((step) => (
            <div
              key={step.number}
              className="group relative z-10 flex flex-col items-center space-y-8"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-600 font-sans text-2xl font-black text-white shadow-xl shadow-red-600/20 transition-all duration-500 group-hover:rotate-3 group-hover:scale-110">
                {step.number}
              </div>
              <div className="space-y-3">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{step.title}</h3>
                <p className="max-w-xs text-lg font-medium text-gray-500 dark:text-gray-400">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
