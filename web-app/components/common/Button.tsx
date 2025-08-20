'use client';

interface ButtonProps {
  children: React.ReactNode;
  className?: string;
}

export function Button(props: ButtonProps) {
  const { children, className } = props;
  return (
    <button className={`w-full rounded-full bg-green-200 p-2 text-white ${className} `}>
      {children}
    </button>
  );
}

export default Button;
