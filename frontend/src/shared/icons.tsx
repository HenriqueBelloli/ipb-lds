import { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

export function UserIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path
        d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"
        fill="currentColor"
      />
      <path
        d="M4.5 20c.8-4 3.4-6 7.5-6s6.7 2 7.5 6H4.5Z"
        fill="currentColor"
      />
    </svg>
  );
}

export function LockIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path
        d="M7 10V8a5 5 0 0 1 10 0v2h-2V8a3 3 0 1 0-6 0v2H7Z"
        fill="currentColor"
      />
      <path
        d="M6 10h12v10H6V10Zm5 4v3h2v-3h-2Z"
        fill="currentColor"
      />
    </svg>
  );
}

export function EyeIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path
        d="M2.1 12s3.7-6.5 9.9-6.5S21.9 12 21.9 12s-3.7 6.5-9.9 6.5S2.1 12 2.1 12Z"
      />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

export function SearchIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-4.5-4.5" />
    </svg>
  );
}

export function PencilIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path
        d="M17 3a2.8 2.8 0 0 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3Z"
      />
      <path d="m15 5 4 4" />
    </svg>
  );
}

export function TrashIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="M19 6 18 20H6L5 6" />
      <path d="M10 11v5" />
      <path d="M14 11v5" />
    </svg>
  );
}

export function AlertIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M12 3 2.5 20h19L12 3Z" fill="currentColor" />
      <path d="M11 9h2v5h-2V9Zm0 7h2v2h-2v-2Z" fill="#fff" />
    </svg>
  );
}

export function CheckIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z" fill="currentColor" />
      <path d="m7.5 12.2 2.7 2.7 6.3-6.5 1.4 1.4-7.7 7.9-4.1-4.1 1.4-1.4Z" fill="#fff" />
    </svg>
  );
}

export function SpinnerIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path
        d="M12 3a9 9 0 1 0 9 9h-2a7 7 0 1 1-7-7V3Z"
        fill="currentColor"
      />
    </svg>
  );
}

export function HomeIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="m3 11 9-8 9 8v10h-6v-6H9v6H3V11Z" fill="currentColor" />
    </svg>
  );
}

export function ClipboardIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M9 3h6l1 2h3v16H5V5h3l1-2Zm0 6h6V7H9v2Zm0 4h7v-2H9v2Zm0 4h5v-2H9v2Z" fill="currentColor" />
    </svg>
  );
}

export function MoneyIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path
        d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm1 15.9V20h-2v-2.1c-1.8-.3-3-1.3-3.6-2.8l1.8-.8c.5 1.2 1.4 1.8 2.8 1.8 1.3 0 2-.5 2-1.3 0-.9-.8-1.2-2.5-1.6-1.9-.5-3.7-1.2-3.7-3.4 0-1.7 1.3-3 3.2-3.4V4h2v2.3c1.4.3 2.5 1.1 3.1 2.4l-1.7.9c-.5-.9-1.3-1.4-2.4-1.4-1.2 0-1.9.5-1.9 1.3 0 .8.7 1.1 2.3 1.5 2 .5 3.9 1.2 3.9 3.6 0 1.8-1.3 3-3.3 3.3Z"
        fill="currentColor"
      />
    </svg>
  );
}

export function UsersIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm6.8.3A3.5 3.5 0 1 0 15 4.4a5.8 5.8 0 0 1 .8 6.9ZM2 20c.7-4.4 3-6.6 7-6.6s6.3 2.2 7 6.6H2Zm14.8 0h5.1c-.4-3.4-2.1-5.2-5.1-5.6.8 1.3 1.5 3.1 2 5.6Z" fill="currentColor" />
    </svg>
  );
}

export function FileIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M5 3h10l4 4v14H5V3Zm9 1.8V8h3.2L14 4.8ZM8 12h8v-2H8v2Zm0 4h8v-2H8v2Z" fill="currentColor" />
    </svg>
  );
}

export function BellIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M12 22a2.5 2.5 0 0 0 2.4-2h-4.8a2.5 2.5 0 0 0 2.4 2Zm7-5-2-2.4V10a5 5 0 0 0-4-4.9V3h-2v2.1A5 5 0 0 0 7 10v4.6L5 17v1h14v-1Z" fill="currentColor" />
    </svg>
  );
}

export function LogoutIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M4 3h9v2H6v14h7v2H4V3Zm12.6 5.4L20.2 12l-3.6 3.6-1.4-1.4 1.2-1.2H10v-2h6.4l-1.2-1.2 1.4-1.4Z" fill="currentColor" />
    </svg>
  );
}
