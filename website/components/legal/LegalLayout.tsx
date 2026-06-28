import type { ReactNode } from 'react';

import { Footer, Navbar } from 'components/landing';

export interface LegalSection {
  id: string;
  heading: string;
  content: ReactNode;
}

/** Shared shell for the long legal pages (Terms, Privacy, Refund). */
export function LegalLayout({
  title,
  lastUpdated,
  intro,
  sections,
}: {
  title: string;
  lastUpdated: string;
  intro?: ReactNode;
  sections: LegalSection[];
}) {
  return (
    <div className="min-h-screen bg-white font-sans transition-colors duration-300 selection:bg-red-500 selection:text-white dark:bg-[#0a0a0a] dark:text-white">
      <Navbar />
      <main className="container mx-auto max-w-5xl px-6 pb-24 pt-32">
        <header className="space-y-4 border-b border-gray-200 pb-10 dark:border-white/10">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white md:text-5xl">
            {title}
          </h1>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Last updated: {lastUpdated}
          </p>
        </header>

        <div className="mt-12 gap-12 lg:grid lg:grid-cols-[16rem_1fr]">
          <aside className="mb-12 lg:mb-0">
            <nav aria-label="Table of contents" className="lg:sticky lg:top-28">
              <h2 className="mb-4 text-xs font-bold uppercase tracking-widest text-gray-400">
                On this page
              </h2>
              <ul className="space-y-2 text-sm">
                {sections.map((s) => (
                  <li key={s.id}>
                    <a
                      href={`#${s.id}`}
                      className="font-medium text-gray-500 transition-colors hover:text-red-500 dark:text-gray-400 dark:hover:text-white"
                    >
                      {s.heading}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </aside>

          <article className="max-w-none space-y-12 text-gray-600 dark:text-gray-300">
            {intro ? <div className="text-lg leading-relaxed">{intro}</div> : null}
            {sections.map((s) => (
              <section key={s.id} id={s.id} className="scroll-mt-28 space-y-4">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{s.heading}</h2>
                <div className="space-y-4 leading-relaxed">{s.content}</div>
              </section>
            ))}
          </article>
        </div>
      </main>
      <Footer />
    </div>
  );
}

/** Paragraph helper so the page data stays terse. */
export function P({ children }: { children: ReactNode }) {
  return <p className="leading-relaxed">{children}</p>;
}

/** Bulleted list helper. */
export function UL({ items }: { items: ReactNode[] }) {
  return (
    <ul className="list-disc space-y-2 pl-6 marker:text-red-500">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}
