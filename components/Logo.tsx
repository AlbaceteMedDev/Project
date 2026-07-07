import Link from "next/link";
import Emblem from "./Emblem";

interface LogoProps {
  /** "light" for cream backgrounds, "dark" for pine-night sections. */
  tone?: "light" | "dark";
  /** Background color behind the logo — passed to the emblem's weave casing. */
  casing?: string;
  size?: number;
}

export default function Logo({ tone = "light", casing, size = 44 }: LogoProps) {
  const dark = tone === "dark";
  return (
    <Link href="/" className="logo" aria-label="Apollo Wound Care — home">
      <Emblem
        size={size}
        strand={dark ? "#F7F4EC" : "#14452F"}
        accent={dark ? "#D8B96E" : "#B9944A"}
        casing={casing ?? (dark ? "#0B2E1F" : "#F7F4EC")}
      />
      <span className="logo-word" data-tone={tone}>
        <span className="logo-name">Apollo</span>
        <span className="logo-sub">Wound Care</span>
      </span>
    </Link>
  );
}
