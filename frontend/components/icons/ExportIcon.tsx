type ExportIconProps = {
  className?: string;
};

export default function ExportIcon({ className }: Readonly<ExportIconProps>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      className={className}
    >
      <path
        d="M10.8333 9.16671L17.6666 2.33337"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M18.3333 5.66663V1.66663H14.3333"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M9.16675 1.66663H7.50008C3.33341 1.66663 1.66675 3.33329 1.66675 7.49996V12.5C1.66675 16.6666 3.33341 18.3333 7.50008 18.3333H12.5001C16.6667 18.3333 18.3334 16.6666 18.3334 12.5V10.8333"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
