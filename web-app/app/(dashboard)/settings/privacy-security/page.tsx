'use client';

import { useEffect, useState } from 'react';
import Card from '@/components/ui/Card';

import { privacyService, PrivacySettings } from 'lib/api';
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

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Load privacy settings on component mount
  useEffect(() => {
    const loadPrivacySettings = async () => {
      try {
        setLoading(true);
        const settings = await privacyService.getPrivacySettings();

        // Map API response to local state
        setPreferences({
          dataPreferences: {
            allowProductUpdates: settings.allow_product_update_emails || false,
            allowAnonymizedData: settings.allow_anonymized_data_usage || false,
          },
        });
      } catch (error) {
        console.log('Failed to load privacy settings:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPrivacySettings();
  }, []);

  const handleDataPreferenceToggle = async (
    key: keyof PrivacySecurityPreferences['dataPreferences'],
    checked: boolean,
  ) => {
    const newPreferences = {
      ...preferences,
      dataPreferences: {
        ...preferences.dataPreferences,
        [key]: checked,
      },
    };
    setPreferences(newPreferences);
    await savePrivacySettings(newPreferences);
  };

  const savePrivacySettings = async (newPreferences: PrivacySecurityPreferences) => {
    try {
      setSaving(true);

      // Convert local state to API format
      const settings: PrivacySettings = {
        allow_product_update_emails: newPreferences.dataPreferences.allowProductUpdates,
        allow_anonymized_data_usage: newPreferences.dataPreferences.allowAnonymizedData,
      };

      await privacyService.updatePrivacySettings(settings);
      console.log('Privacy settings updated successfully');
    } catch (error) {
      console.log('Failed to save privacy settings:', error);

      // Revert the change on error
      setPreferences(preferences);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto space-y-6">
        <div className="flex items-center justify-center py-8">
          <div className="text-gray-400">Loading privacy settings...</div>
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
          defaultChecked={preferences.dataPreferences.allowProductUpdates}
          onToggle={(checked) => handleDataPreferenceToggle('allowProductUpdates', checked)}
          disabled={saving}
        />
        <Switch
          label="Allow use of anonymized data for improving TubeGenius"
          description="Help us improve by sharing anonymous usage data"
          defaultChecked={preferences.dataPreferences.allowAnonymizedData}
          onToggle={(checked) => handleDataPreferenceToggle('allowAnonymizedData', checked)}
          disabled={saving}
        />
      </Card>

      {saving && (
        <div className="flex items-center justify-center py-2">
          <div className="text-sm text-gray-400">Saving changes...</div>
        </div>
      )}
    </div>
  );
}
