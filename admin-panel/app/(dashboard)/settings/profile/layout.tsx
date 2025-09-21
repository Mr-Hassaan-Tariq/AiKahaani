import React from 'react';

import SettingTabs from '../SettingTabs';

export default function Layout({ children }: { children: React.ReactNode }) {
  return <SettingTabs>{children}</SettingTabs>;
}
