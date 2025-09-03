import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';

import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';
import LogoutIcon from 'components/icons/LogoutIcon';

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
        <Row className="group cursor-pointer justify-normal gap-2.5 whitespace-nowrap [font-feature-settings:'liga'_off,'clig'_off]">
          <LogoutIcon />
          <Text variant="lg" className="text-[#AAACA6] group-hover:text-[#20BF0E]/40">
            Logout
          </Text>
        </Row>
      }
      title="Log out of your account?"
      description="You’ll be signed out from TubeGenius on this device. You can log in again anytime."
      footer={
        <Row className="w-full gap-6">
          <Button variant="gray" onClick={() => setOpen(false)}>
            Go back
          </Button>
          <Button type="button" onClick={handleLogout}>
            Log out
          </Button>
        </Row>
      }
    ></Dialog>
  );
}
