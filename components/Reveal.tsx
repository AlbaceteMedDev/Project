"use client";

import { useEffect, useRef, type ReactNode, type CSSProperties } from "react";

interface RevealProps {
  children: ReactNode;
  /** Stagger delay in seconds. */
  delay?: number;
  as?: "div" | "section" | "li" | "span";
  className?: string;
}

/** Fades content up on first scroll into view. Respects prefers-reduced-motion. */
export default function Reveal({ children, delay = 0, as = "div", className = "" }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const Tag = as as "div";
  const style = delay ? ({ "--reveal-delay": `${delay}s` } as CSSProperties) : undefined;
  return (
    <Tag ref={ref} className={`reveal ${className}`} style={style}>
      {children}
    </Tag>
  );
}
