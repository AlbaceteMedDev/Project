/**
 * Signature motif: a suture line — the mark of a well-closed wound.
 * A gentle horizontal line crossed by small stitches.
 */
export default function StitchDivider({ tone = "light" }: { tone?: "light" | "dark" }) {
  const color = tone === "dark" ? "rgba(216,185,110,0.5)" : "rgba(185,148,74,0.65)";
  const stitches = Array.from({ length: 7 }, (_, i) => 90 + i * 70);
  return (
    <div className="stitch" aria-hidden="true">
      <svg viewBox="0 0 600 20" preserveAspectRatio="xMidYMid meet">
        <line x1="0" y1="10" x2="600" y2="10" stroke={color} strokeWidth="1" />
        {stitches.map((x) => (
          <line
            key={x}
            x1={x - 5}
            y1="3"
            x2={x + 5}
            y2="17"
            stroke={color}
            strokeWidth="1.4"
            strokeLinecap="round"
          />
        ))}
      </svg>
    </div>
  );
}
