import Image from 'next/image';

type EmptyStateProps = {
  icon: string;
  title: string;
  description: string;
};

export default function EmptyState({ icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center py-20 text-center">
      <Image src={icon} alt={title} width={80} height={80} className="mb-6 opacity-70" />
      <h2 className="mb-2 text-base font-semibold text-foreground">{title}</h2>
      <p
        className="max-w-md text-sm text-muted-foreground"
        dangerouslySetInnerHTML={{ __html: description }}
      />
    </div>
  );
}
