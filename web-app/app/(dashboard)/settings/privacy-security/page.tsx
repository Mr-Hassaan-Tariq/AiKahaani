'use client';

import { useState } from 'react';
import { Eye, EyeOff, KeyRound, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';

import { PrivacySettings, userService } from 'lib/api';
import { useGetPrivacySettings, useUpdatePrivacySettings } from 'lib/hooks/useprivacySecurity';
import { Button } from 'components/ui/Button';
import Switch from 'components/common/Switch';

export default function PrivacySecurityPage() {
  const { data: privacySettings, isLoading } = useGetPrivacySettings();
  const { mutate: updatePrivacySettings, isPending: isUpdating } = useUpdatePrivacySettings();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  const handleDataPreferenceToggle = (key: keyof PrivacySettings, checked: boolean) => {
    if (!privacySettings) return;
    updatePrivacySettings(
      { ...privacySettings, [key]: checked },
      {
        onError: () => toast.error('Failed to save privacy settings'),
      },
    );
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setIsChangingPassword(true);
    try {
      await userService.changePassword(currentPassword, newPassword, confirmPassword);
      toast.success('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      toast.error(err?.message || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto flex w-full max-w-[900px] items-center justify-center py-16">
        <p className="text-sm text-muted-foreground">Loading…</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Change Password */}
      <div className="rounded-xl border border-border bg-card p-8">
        <div className="mb-6 flex items-center gap-3 border-b border-border pb-6">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <KeyRound className="h-[18px] w-[18px] text-primary" />
          </div>
          <div>
            <h3 className="text-[18px] font-semibold leading-snug text-foreground">
              Change Password
            </h3>
            <p className="text-sm text-muted-foreground">
              Update your login password to keep your account secure.
            </p>
          </div>
        </div>

        <form onSubmit={handleChangePassword} className="flex flex-col gap-5">
          {/* Current password */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-semibold text-foreground">Current Password</label>
            <div className="relative">
              <input
                type={showCurrent ? 'text' : 'password'}
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter your current password"
                required
                className="h-10 w-full rounded-md border border-border bg-input px-3 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
              <button
                type="button"
                onClick={() => setShowCurrent(!showCurrent)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* New + Confirm in 2 cols */}
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-semibold text-foreground">New Password</label>
              <div className="relative">
                <input
                  type={showNew ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  required
                  className="h-10 w-full rounded-md border border-border bg-input px-3 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
                <button
                  type="button"
                  onClick={() => setShowNew(!showNew)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-semibold text-foreground">Confirm New Password</label>
              <div className="relative">
                <input
                  type={showConfirm ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat your new password"
                  required
                  className="h-10 w-full rounded-md border border-border bg-input px-3 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button
              type="submit"
              variant="primary"
              loading={isChangingPassword}
              disabled={isChangingPassword}
            >
              Update Password
            </Button>
          </div>
        </form>
      </div>

      {/* Data Preferences */}
      <div className="rounded-xl border border-border bg-card p-8">
        <div className="mb-6 flex items-center gap-3 border-b border-border pb-6">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <ShieldCheck className="h-[18px] w-[18px] text-primary" />
          </div>
          <div>
            <h3 className="text-[18px] font-semibold leading-snug text-foreground">
              Data Preferences
            </h3>
            <p className="text-sm text-muted-foreground">
              Control how your data is used to improve your experience.
            </p>
          </div>
        </div>

        <div className="flex flex-col divide-y divide-border">
          <div className="py-4 first:pt-0">
            <Switch
              label="Allow product update emails"
              description="Receive emails about new features and updates"
              defaultChecked={privacySettings?.allow_product_update_emails}
              onToggle={(checked) =>
                handleDataPreferenceToggle('allow_product_update_emails', checked)
              }
              disabled={isUpdating}
            />
          </div>
          <div className="py-4 last:pb-0">
            <Switch
              label="Allow anonymized data usage"
              description="Help us improve by sharing anonymous usage data"
              defaultChecked={privacySettings?.allow_anonymized_data_usage}
              onToggle={(checked) =>
                handleDataPreferenceToggle('allow_anonymized_data_usage', checked)
              }
              disabled={isUpdating}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
