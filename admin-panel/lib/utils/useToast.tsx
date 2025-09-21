import { CheckCircleIcon, XCircleIcon } from 'lucide-react';
import { toast } from 'sonner';

export default function useToast() {
  const success = (title: string, description?: string, duration?: number) => {
    toast.success(title, {
      icon: <CheckCircleIcon />,
      description,
      duration: duration || 5000,
      classNames: {
        icon: 'text-green-500',
      },
      style: {
        '--normal-bg': '[rgba(186,255,56,0.12)]',
        '--normal-border': '#b9ff3869',
      } as React.CSSProperties,
    });
  };
  const error = (title: string, description?: string, duration?: number) => {
    toast.error(title, {
      icon: <XCircleIcon />,
      description,
      duration: duration || 5000,
      classNames: {
        icon: 'text-red-500',
      },
      style: {
        '--normal-bg': '[rgba(255,56,56,0.12)]',
        '--normal-border': '#ff383869',
      } as React.CSSProperties,
    });
  };

  return { error, success };
}
