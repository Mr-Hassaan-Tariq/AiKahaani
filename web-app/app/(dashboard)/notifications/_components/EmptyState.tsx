import Image from 'next/image';

type EmptyStateProps = {
  icon: string;
  title: string;
  description: string;
};

export default function EmptyState({ icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center py-20 text-center text-white">
      {/* Bell Icon */}
      <Image src={icon} alt={title} width={100} height={100} className="mb-6" />

      {/* Heading */}
      <h2 className="mb-2 text-xl font-semibold">{title}</h2>

      {/* Description */}
      <p className="max-w-md text-sm text-[#AAACA6]">{description}</p>
    </div>
  );
}
