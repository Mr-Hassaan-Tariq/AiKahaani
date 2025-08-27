'use client';

interface TextFieldProps {
  label?: string;
  placeholder?: string;
  type?: string;
  className?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export default function TextField(props: TextFieldProps) {
  const { label, placeholder, type, value, onChange } = props;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(e.target.value);
    }
  };

  return (
    <div>
      <label className="mb-1 block text-sm text-white">{label}</label>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        className="w-full rounded-xl border border-transparent bg-[#2d2d2d] px-4 py-3 text-white placeholder-[#aaaca6] outline-none focus:border-green-500"
      />
    </div>
  );
}
