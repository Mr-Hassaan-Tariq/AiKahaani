import { CheckCircleIcon, XCircleIcon } from 'lucide-react';
import { toast } from 'sonner';

export default function useToast() {
  const success = (title: string, description?: string, duration?: number) => {
    toast.success(title, {
      icon: <CheckCircleIcon />,
      description,
      duration: duration || 5000,
    });
  };
  const error = (title: string, description?: string, duration?: number) => {
    toast.error(title, {
      icon: <XCircleIcon />,
      description,
      duration: duration || 5000,
    });
  };

  return { error, success };
}
