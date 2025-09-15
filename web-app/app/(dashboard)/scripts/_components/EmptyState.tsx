import { EmptyStateProps } from '../_types';

export default function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  className = '',
}: EmptyStateProps) {
  return (
    <div className={`py-12 text-center ${className}`}>
      <div className="mb-4 flex justify-center">
        <Icon className="h-16 w-16 text-gray-400" />
      </div>
      <h3 className="mb-2 text-xl font-semibold text-white">{title}</h3>
      <p className="mb-6 text-gray-400" dangerouslySetInnerHTML={{ __html: description }} />
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="rounded-lg bg-green-500 px-6 py-2 font-semibold text-black transition-colors hover:bg-green-600"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
