"use client";

import { useState } from "react";
import Link from "next/link";
import { boroughs, type Borough } from "@/lib/boroughs";
import { boroughShapes } from "@/lib/nyc-map";

/**
 * An interactive map of New York City's five boroughs, traced from real
 * boundary data and simplified into the brand's line language.
 */
export default function BoroughMap() {
  const [active, setActive] = useState<Borough>(boroughs[1]); // Brooklyn default

  return (
    <div className="map-wrap">
      <div className="map-figure">
        <svg
          viewBox="0 0 470 430"
          role="group"
          aria-label="Map of New York City's five boroughs — all served by Apollo Wound Care"
        >
          {/* cartographic flourish: north arrow */}
          <g className="map-compass" aria-hidden="true" transform="translate(38 44)">
            <line x1="0" y1="14" x2="0" y2="-12" />
            <path d="M0 -16 L-4.5 -7 L0 -9.5 L4.5 -7 Z" />
            <text x="0" y="28" textAnchor="middle">
              N
            </text>
          </g>

          {boroughs.map((b) => {
            const s = boroughShapes[b.slug];
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
                {isActive && s.anchor !== "end" && (
                  <circle
                    cx={s.labelX}
                    cy={s.labelY + 14}
                    r="3"
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
