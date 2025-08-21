'use client';

interface ButtonProps {
  children: React.ReactNode;
  className?: string;
}

export function Button(props: ButtonProps) {
  const { children, className } = props;
  return (
    <button className={`w-full rounded-full bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] hover:opacity-90 p-3 font-semibold text-black ${className} `}>
      {children}
    </button>
  );
}

export default Button;
