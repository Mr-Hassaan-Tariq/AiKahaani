import Button from 'components/ui/Button';
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
        <Icon className="h-16 w-16 text-muted-foreground" />
      </div>
      <h3 className="mb-2 text-xl font-semibold text-foreground">{title}</h3>
      <p className="mb-6 text-muted-foreground" dangerouslySetInnerHTML={{ __html: description }} />
      {actionLabel && onAction && (
        <Button onClick={onAction}>{actionLabel}</Button>
      )}
    </div>
  );
}
