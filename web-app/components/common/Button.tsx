'use client';

interface ButtonProps {
  children: React.ReactNode;
  className?: string;
}

export function Button(props: ButtonProps) {
  const { children, className } = props;
  return (
    <button
      className={`text-black w-full rounded-full bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] p-3 font-semibold hover:opacity-90 ${className} `}
    >
      {children}
    </button>
  );
}

export default Button;
