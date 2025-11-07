'use client';

import Image, { ImageProps } from 'next/image';
import dummyProfilePic from 'public/images/avatar.png';

export default function ClientImage(props: ImageProps) {
  const { src, alt, className, ...rest } = props;
  return (
    <Image
      src={src || dummyProfilePic}
      alt={alt || 'image'}
      className={className}
      // onError={(e) => {
      //   e.currentTarget.src = '/images/avatar.png';
      // }}
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...rest}
    />
  );
}
