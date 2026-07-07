"use client";

import { useState } from "react";
import Link from "next/link";
import { boroughs, type Borough } from "@/lib/boroughs";

/**
 * A stylized, interactive map of New York City's five boroughs.
 * Deliberately abstract — organic shapes in the brand palette rather than a
 * cartographic tracing — but arranged true to geography.
 */
const shapes: Record<
  string,
  { d: string; labelX: number; labelY: number; anchor?: "middle" | "end" }
> = {
  "the-bronx": {
    d: "M226 92 C226 64 262 44 302 44 C346 44 382 66 382 96 C382 122 346 140 302 140 C262 140 226 120 226 92 Z",
    labelX: 302,
    labelY: 96,
  },
  manhattan: {
    d: "M232 122 C242 125 244 140 241 158 L228 226 C226 238 213 238 211 227 C209 210 216 152 220 134 C223 123 226 120 232 122 Z",
    labelX: 196,
    labelY: 184,
    anchor: "end",
  },
  queens: {
    d: "M264 200 C264 170 302 148 354 148 C406 148 446 170 446 202 C446 234 404 258 352 258 C302 258 264 230 264 200 Z",
    labelX: 356,
    labelY: 204,
  },
  brooklyn: {
    d: "M202 310 C202 282 238 258 282 258 C328 258 360 282 360 312 C360 342 324 366 280 366 C236 366 202 340 202 310 Z",
    labelX: 282,
    labelY: 314,
  },
  "staten-island": {
    d: "M54 352 C54 326 86 304 122 304 C160 304 190 326 190 356 C190 384 158 402 122 402 C84 402 54 380 54 352 Z",
    labelX: 122,
    labelY: 356,
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
                  className={`map-label ${isActive && s.anchor !== "end" ? "is-active" : ""}`}
                  textAnchor={s.anchor ?? "middle"}
                  aria-hidden="true"
                >
                  {b.name}
                </text>
                {isActive && (
                  <circle
                    cx={s.anchor === "end" ? s.labelX - 4 : s.labelX}
                    cy={s.labelY + 15}
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
