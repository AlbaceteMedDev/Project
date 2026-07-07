interface EmblemProps {
  /** Strand color of the knot, ring and center leaf. */
  strand?: string;
  /** Accent color: cross of care + side leaves. */
  accent?: string;
  /**
   * Casing color — must match the background the emblem sits on.
   * It carves the over/under gaps that make the knot read as woven.
   */
  casing?: string;
  size?: number | string;
  className?: string;
}

/**
 * The Apollo Wound Care emblem: a woven "healing knot" (continuity of care,
 * the closed wound) inside a tree-of-life ring with a sprouting crown
 * (healing, growth) and a gold cross of care at its heart.
 */
export default function Emblem({
  strand = "#14452F",
  accent = "#B9944A",
  casing = "#F7F4EC",
  size = 48,
  className,
}: EmblemProps) {
  const loop = (deg: number, stroke: string, width: number) => (
    <rect
      x="38"
      y="90"
      width="164"
      height="60"
      rx="30"
      stroke={stroke}
      strokeWidth={width}
      transform={`rotate(${deg} 120 120)`}
    />
  );
  const patches = (stroke: string, width: number) => (
    <>
      <line x1="72" y1="90" x2="106" y2="90" stroke={stroke} strokeWidth={width} />
      <line x1="134" y1="150" x2="168" y2="150" stroke={stroke} strokeWidth={width} />
    </>
  );

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 240 240"
      fill="none"
      width={size}
      height={size}
      className={className}
      aria-hidden="true"
      focusable="false"
    >
      <path
        d="M156.94 18.51A108 108 0 1 1 83.06 18.51"
        stroke={strand}
        strokeWidth="5"
        strokeLinecap="round"
      />
      <path
        d="M0 0Q7 -10.1 0 -24Q-7 -10.1 0 0Z"
        fill={strand}
        transform="translate(120 26)"
      />
      <path
        d="M0 0Q5.5 -8 0 -19Q-5.5 -8 0 0Z"
        fill={accent}
        transform="translate(112.5 27) rotate(-35)"
      />
      <path
        d="M0 0Q5.5 -8 0 -19Q-5.5 -8 0 0Z"
        fill={accent}
        transform="translate(127.5 27) rotate(35)"
      />
      {loop(45, strand, 13)}
      {loop(-45, casing, 23)}
      {loop(-45, strand, 13)}
      <g transform="rotate(45 120 120)">
        {patches(casing, 23)}
        {patches(strand, 13)}
      </g>
      <rect x="115" y="107" width="10" height="26" rx="5" fill={accent} />
      <rect x="107" y="115" width="26" height="10" rx="5" fill={accent} />
    </svg>
  );
}
