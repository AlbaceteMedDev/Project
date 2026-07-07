"use client";

import { useEffect, useRef, useState } from "react";

interface StatProps {
  value: number;
  suffix?: string;
  prefix?: string;
  label: string;
}

/** Animated count-up stat, triggered on scroll into view. */
export default function Stat({ value, suffix = "", prefix = "", label }: StatProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        io.disconnect();
        if (reduced) {
          setDisplay(value);
          return;
        }
        const start = performance.now();
        const duration = 1400;
        const tick = (now: number) => {
          const t = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - t, 3);
          setDisplay(Math.round(eased * value));
          if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      },
      { threshold: 0.4 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [value]);

  return (
    <div className="stat" ref={ref}>
      <span className="stat-value">
        {prefix}
        {display}
        {suffix}
      </span>
      <span className="stat-label">{label}</span>
    </div>
  );
}
