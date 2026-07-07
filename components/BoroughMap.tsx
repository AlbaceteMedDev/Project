"use client";

import { useState } from "react";
import Link from "next/link";
import { boroughs, type Borough } from "@/lib/boroughs";

/**
 * A stylized, interactive map of New York City's five boroughs.
 * Deliberately abstract — organic shapes in the brand palette rather than a
 * cartographic tracing — but arranged true to geography.
 */
const shapes: Record<string, { d: string; labelX: number; labelY: number }> = {
  "the-bronx": {
    d: "M236 96c8-18 26-30 48-33 24-3 47 3 61 17 12 12 16 30 9 45-6 14-20 22-36 24-9 1-18 4-27 3-16-2-35-9-46-22-8-10-13-22-9-34Z",
    labelX: 297,
    labelY: 122,
  },
  manhattan: {
    d: "M223 112c5-8 15-8 18 1 4 12 2 25-1 38l-13 51c-3 12-6 25-12 34-4 6-13 5-15-2-3-11 1-23 4-35l12-52c3-12 3-25 7-35Z",
    labelX: 214,
    labelY: 176,
  },
  queens: {
    d: "M268 168c18-12 42-16 65-12 26 5 51 12 66 30 12 15 15 37 5 53-9 15-27 21-45 23-22 3-45 2-66-6-17-7-33-19-38-36-5-19 0-41 13-52Z",
    labelX: 340,
    labelY: 216,
  },
  brooklyn: {
    d: "M232 262c12-9 29-9 44-5 18 5 36 12 46 27 9 14 10 33 1 47-9 15-27 20-44 20-16 0-33-4-44-15-10-10-14-25-13-40 1-13 1-26 10-34Z",
    labelX: 288,
    labelY: 306,
  },
  "staten-island": {
    d: "M96 338c12-13 31-18 49-15 17 3 33 13 40 29 7 15 4 33-5 46-10 14-26 22-43 21-16-1-31-10-39-24-9-16-13-42-2-57Z",
    labelX: 141,
    labelY: 373,
  },
};

export default function BoroughMap() {
  const [active, setActive] = useState<Borough>(boroughs[1]); // Brooklyn default

  return (
    <div className="map-wrap">
      <div className="map-figure">
        <svg
          viewBox="0 0 470 440"
          role="group"
          aria-label="Map of New York City's five boroughs — all served by Apollo Wound Care"
        >
          {/* subtle water lines */}
          <g stroke="rgba(64,107,80,0.25)" strokeWidth="1.2" fill="none" aria-hidden="true">
            <path d="M196 260c14 6 28 6 40 14" />
            <path d="M244 130c-6 14-6 26-12 38" />
            <path d="M60 320c18-10 38-14 56-10" />
          </g>
          {boroughs.map((b) => {
            const s = shapes[b.slug];
            const isActive = active.slug === b.slug;
            return (
              <g key={b.slug}>
                <path
                  d={s.d}
                  className={`map-borough ${isActive ? "is-active" : ""}`}
                  onMouseEnter={() => setActive(b)}
                  onFocus={() => setActive(b)}
                  onClick={() => setActive(b)}
                  tabIndex={0}
                  role="button"
                  aria-pressed={isActive}
                  aria-label={`${b.name} — view coverage details`}
                />
                <text
                  x={s.labelX}
                  y={s.labelY}
                  className={`map-label ${isActive ? "is-active" : ""}`}
                  textAnchor="middle"
                  aria-hidden="true"
                >
                  {b.name}
                </text>
                {isActive && (
                  <circle
                    cx={s.labelX}
                    cy={s.labelY + 16}
                    r="3.2"
                    className="map-pin"
                    aria-hidden="true"
                  />
                )}
              </g>
            );
          })}
        </svg>
      </div>

      <aside className="map-panel" aria-live="polite">
        <p className="eyebrow">Now viewing</p>
        <h3 className="map-panel-title">{active.name}</h3>
        <p className="map-panel-copy">{active.intro}</p>
        <p className="map-panel-hoods">
          <strong>Including:</strong> {active.neighborhoods.slice(0, 6).join(", ")} &amp; more
        </p>
        <Link href={`/service-areas/${active.slug}`} className="btn btn-ghost">
          Wound care in {active.name} →
        </Link>
      </aside>
    </div>
  );
}
