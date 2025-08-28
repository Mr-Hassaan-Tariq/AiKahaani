import { ReactNode } from 'react';

interface CardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export default function Card({ title, children, className }: CardProps) {
  return (
    <div
      className={`mb-4 rounded-2xl border border-[var(--Stroke-Surface,#BAFF381F)] bg-[#161616] p-4 text-white ${className}`}
    >
      <h2 className="mb-3 text-lg font-semibold">{title}</h2>
      <div className="space-y-3">{children}</div>
    </div>
  );
}
