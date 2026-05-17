export function Logo({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <svg
        width="32"
        height="32"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <path
          d="M16 2l11 4v9c0 7-5 12-11 15-6-3-11-8-11-15V6l11-4z"
          fill="#0284C7"
        />
        <path
          d="M16 9v10M11 14h10"
          stroke="#fff"
          strokeWidth="2.4"
          strokeLinecap="round"
        />
      </svg>
      <span className="text-lg font-bold tracking-tight text-ink-900">
        MediSign <span className="text-brand">AI</span>
      </span>
    </span>
  );
}
