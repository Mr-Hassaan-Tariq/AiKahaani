'use client';

import { useMemo } from 'react';
import { usePathname } from 'next/navigation';

import Text from './Text';
import { footerData, navItems } from 'lib/localData';

export default function FooterItems() {
  const pathname = usePathname();

  const itemList = useMemo(() => {
    if (['/', '/affiliates', '/about-partner'].includes(pathname)) {
      return navItems.filter((e) => e.ref?.includes(pathname));
    }
    return [];
  }, [pathname]);

  return [...itemList, ...footerData].map((item) => (
    <Text
      key={item.id}
      onClick={() => {
        const element = document.getElementById(item.id);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }}
      variant="base"
      className="cursor-pointer whitespace-nowrap text-[#EAECE5] hover:text-[#20BF0E]"
    >
      {item.label}
    </Text>
  ));
}
