export interface LoaderModel {
  color?: 'sky-blue' | 'white' | 'red' | 'black' | 'alice-blue';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  title?: string;
}

export default function Loader({ color, size, title }: LoaderModel) {
  let classes: string = 'animate-spin mx-auto rounded-full border-solid border-t-transparent';

  // seting size of the loader
  classes += sizeClasses[size ?? 'md'];

  // setting color of the loader
  classes += colorClasses[color ?? 'black'];

  return <div className={classes} title={title || 'Loading...'} />;
}

const sizeClasses = {
  xs: ' border-2 w-4 h-4',
  sm: ' border-2 w-7 h-7',
  md: ' border-[3px] w-10 h-10',
  lg: ' border-4 w-16 h-16',
  xl: ' border-4 w-[72px] h-[72px]',
  '2xl': ' border-4 w-20 h-20',
};

const colorClasses = {
  'sky-blue': ' border-sky-blue',
  white: ' border-white',
  red: ' border-red-800',
  black: ' border-primary-eerie_black',
  'alice-blue': ' border-primary-alice_blue ',
};
