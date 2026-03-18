'use client';

import Card from '@/components/ui/Card';

import { PrivacySettings } from 'lib/api';
import { useGetPrivacySettings, useUpdatePrivacySettings } from 'lib/hooks/useprivacySecurity';
import Switch from 'components/common/Switch';

export default function PrivacySecurityPage() {
  const { data: privacySettings, isLoading } = useGetPrivacySettings();
  const { mutate: updatePrivacySettings, isPending: isUpdating } = useUpdatePrivacySettings();

  const handleDataPreferenceToggle = (key: keyof PrivacySettings, checked: boolean) => {
    if (!privacySettings) return;

    const updatedSettings = {
      ...privacySettings,
      [key]: checked,
    };

    savePrivacySettings(updatedSettings);
  };

  const savePrivacySettings = (updatedSettings: PrivacySettings) => {
    updatePrivacySettings(updatedSettings, {
      onSuccess: () => {
        // eslint-disable-next-line no-console
        console.log('Privacy settings updated successfully');
      },
      onError: (error) => {
        // eslint-disable-next-line no-console
        console.error('Failed to save privacy settings:', error);
      },
    });
  };

  if (isLoading) {
    return (
      <div className="mx-auto space-y-6">
        <div className="flex items-center justify-center py-8">
          <div className="text-sm text-muted-foreground">Loading privacy settings…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto space-y-6">
      {/* Data Preferences */}
      <Card title="Data Preferences" className="space-y-6">
        <Switch
          label="Allow product update emails"
          description="Receive emails about new features and updates"
          defaultChecked={privacySettings?.allow_product_update_emails}
          onToggle={(checked) => handleDataPreferenceToggle('allow_product_update_emails', checked)}
          disabled={isUpdating}
        />
        <Switch
          label="Allow use of anonymized data for improving AiKahani"
          description="Help us improve by sharing anonymous usage data"
          defaultChecked={privacySettings?.allow_anonymized_data_usage}
          onToggle={(checked) => handleDataPreferenceToggle('allow_anonymized_data_usage', checked)}
          disabled={isUpdating}
        />
      </Card>

      {isUpdating && (
        <div className="flex items-center justify-center py-2">
          <div className="text-sm text-muted-foreground">Saving changes…</div>
        </div>
      )}
    </div>
  );
}
