'use client';

import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { LogOut } from 'lucide-react';

import { Button } from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';

export default function LogoutModal() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  const handleLogout = useCallback(() => {
    Cookies.remove('access_token');
    router.push('/signup');
  }, [router]);

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={
        <button className="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground">
          <LogOut className="h-[18px] w-[18px] shrink-0" />
          Logout
        </button>
      }
      title="Log out of your account?"
      description="You'll be signed out from AiKahani on this device. You can log in again anytime."
      footer={
        <div className="flex w-full gap-3">
          <Button variant="outline" className="flex-1" onClick={() => setOpen(false)}>
            Go back
          </Button>
          <Button variant="destructive" className="flex-1" onClick={handleLogout}>
            Log out
          </Button>
        </div>
      }
    />
  );
}
