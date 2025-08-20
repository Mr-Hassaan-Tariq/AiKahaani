import { FaGoogle } from 'react-icons/fa';

import Button from 'components/common/Button';

export default function Signup() {
  return (
    <div>
      <Button className="">
        <div className="flex items-center gap-2">
          <FaGoogle />
          <span>Continue with Google</span>
        </div>
      </Button>
    </div>
  );
}
