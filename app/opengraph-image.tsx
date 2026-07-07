import { ImageResponse } from "next/og";

export const dynamic = "force-static";
import { site } from "@/lib/site";

export const alt = `${site.name} — Mobile Wound Care Across NYC's Five Boroughs`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const PINE_NIGHT = "#082218";
const PINE_DEEP = "#0B2E1F";
const CREAM = "#F7F4EC";
const GOLD = "#D8B96E";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          background: `linear-gradient(160deg, ${PINE_DEEP}, ${PINE_NIGHT})`,
          padding: "80px",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "14px",
              color: GOLD,
              fontSize: 26,
              letterSpacing: 8,
              textTransform: "uppercase",
            }}
          >
            <div style={{ width: 54, height: 2, background: GOLD, display: "flex" }} />
            Mobile Wound Care · NYC
          </div>
          <div
            style={{
              marginTop: 34,
              fontSize: 92,
              color: CREAM,
              fontWeight: 700,
              lineHeight: 1.05,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <span>Apollo</span>
            <span>Wound Care</span>
          </div>
          <div style={{ marginTop: 36, fontSize: 32, color: "rgba(247,244,236,0.75)" }}>
            Expert wound care, delivered to your door.
          </div>
          <div style={{ marginTop: 18, fontSize: 26, color: GOLD }}>
            Manhattan · Brooklyn · Queens · The Bronx · Staten Island
          </div>
        </div>

        <svg width="380" height="380" viewBox="0 0 240 240" fill="none">
          <path
            d="M156.94 18.51A108 108 0 1 1 83.06 18.51"
            stroke={CREAM}
            strokeWidth="5"
            strokeLinecap="round"
          />
          <path d="M0 0Q7 -10.1 0 -24Q-7 -10.1 0 0Z" fill={CREAM} transform="translate(120 26)" />
          <path
            d="M0 0Q5.5 -8 0 -19Q-5.5 -8 0 0Z"
            fill={GOLD}
            transform="translate(112.5 27) rotate(-35)"
          />
          <path
            d="M0 0Q5.5 -8 0 -19Q-5.5 -8 0 0Z"
            fill={GOLD}
            transform="translate(127.5 27) rotate(35)"
          />
          <rect
            x="38" y="90" width="164" height="60" rx="30"
            stroke={CREAM} strokeWidth="13" transform="rotate(45 120 120)"
          />
          <rect
            x="38" y="90" width="164" height="60" rx="30"
            stroke={PINE_NIGHT} strokeWidth="23" transform="rotate(-45 120 120)"
          />
          <rect
            x="38" y="90" width="164" height="60" rx="30"
            stroke={CREAM} strokeWidth="13" transform="rotate(-45 120 120)"
          />
          <g transform="rotate(45 120 120)">
            <line x1="72" y1="90" x2="106" y2="90" stroke={PINE_NIGHT} strokeWidth="23" />
            <line x1="134" y1="150" x2="168" y2="150" stroke={PINE_NIGHT} strokeWidth="23" />
            <line x1="72" y1="90" x2="106" y2="90" stroke={CREAM} strokeWidth="13" />
            <line x1="134" y1="150" x2="168" y2="150" stroke={CREAM} strokeWidth="13" />
          </g>
          <rect x="115" y="107" width="10" height="26" rx="5" fill={GOLD} />
          <rect x="107" y="115" width="26" height="10" rx="5" fill={GOLD} />
        </svg>
      </div>
    ),
    { ...size }
  );
}
