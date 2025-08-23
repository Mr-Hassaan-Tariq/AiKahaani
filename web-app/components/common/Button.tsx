'use client';

interface ButtonProps {
  children: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
  onClick?: () => void;
}

export function Button(props: ButtonProps) {
  const { children, className, type = 'button', disabled = false, onClick } = props;
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`text-black w-full rounded-full bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] p-3 font-semibold hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 ${className} `}
    >
      {children}
    </button>
  );
}

export default Button;
