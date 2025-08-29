'use client';

import { useState } from 'react';
import Card from '@/components/ui/Card';

import Switch from 'components/common/Switch';

interface PrivacySecurityPreferences {
  dataPreferences: {
    allowProductUpdates: boolean;
    allowAnonymizedData: boolean;
  };
}

export default function PrivacySecurityPage() {
  const [preferences, setPreferences] = useState<PrivacySecurityPreferences>(() => ({
    dataPreferences: {
      allowProductUpdates: false,
      allowAnonymizedData: false,
    },
  }));

  const handleDataPreferenceToggle = (
    key: keyof PrivacySecurityPreferences['dataPreferences'],
    checked: boolean,
  ) => {
    setPreferences((prev) => ({
      ...prev,
      dataPreferences: {
        ...prev.dataPreferences,
        [key]: checked,
      },
    }));
  };

  // Log preferences for debugging (remove in production)
  console.log('Privacy & Security Preferences:', preferences);

  return (
    <div className="mx-auto space-y-6">
      {/* Data Preferences */}
      <Card title="Data Preferences" className="space-y-6">
        <Switch
          label="Allow product update emails"
          description="Receive emails about new features and updates"
          defaultChecked={preferences.dataPreferences.allowProductUpdates}
          onToggle={(checked) => handleDataPreferenceToggle('allowProductUpdates', checked)}
        />
        <Switch
          label="Allow use of anonymized data for improving TubeGenius"
          description="Help us improve by sharing anonymous usage data"
          defaultChecked={preferences.dataPreferences.allowAnonymizedData}
          onToggle={(checked) => handleDataPreferenceToggle('allowAnonymizedData', checked)}
        />
      </Card>
    </div>
  );
}
