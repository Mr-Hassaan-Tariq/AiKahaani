'use client';

import Image, { ImageProps } from 'next/image';
import brokenImage from 'public/broken-image.png';

export default function ClientImage(props: ImageProps) {
  const { src, alt, className, ...rest } = props;
  return (
    <Image
      src={src || brokenImage}
      alt={alt || 'image'}
      className={className}
      onError={(e) => {
        e.currentTarget.src = '/broken-image.png';
      }}
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...rest}
    />
  );
}
