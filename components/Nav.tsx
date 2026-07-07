"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Logo from "./Logo";
import { site } from "@/lib/site";

const links = [
  { href: "/services", label: "Services" },
  { href: "/service-areas", label: "Service Areas" },
  { href: "/about", label: "About Tim" },
  { href: "/faq", label: "FAQ" },
];

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      <header className={`nav ${scrolled ? "nav-scrolled" : ""}`}>
        <div className="container-wide nav-inner">
          <Logo casing={scrolled ? "#FFFDF8" : "#F7F4EC"} />
          <nav className="nav-links" aria-label="Primary">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={`nav-link ${pathname.startsWith(l.href) ? "is-active" : ""}`}
              >
                {l.label}
              </Link>
            ))}
          </nav>
          <div className="nav-cta">
            <a href={`tel:${site.phoneHref}`} className="nav-phone">
              <PhoneIcon />
              <span>{site.phone}</span>
            </a>
            <Link href="/contact" className="btn btn-primary nav-btn">
              Request a Visit
            </Link>
          </div>
          <button
            className={`nav-burger ${open ? "is-open" : ""}`}
            onClick={() => setOpen(!open)}
            aria-expanded={open}
            aria-controls="mobile-menu"
            aria-label={open ? "Close menu" : "Open menu"}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </header>

      <div id="mobile-menu" className={`mobile-menu ${open ? "is-open" : ""}`}>
        <nav aria-label="Mobile">
          {links.map((l, i) => (
            <Link
              key={l.href}
              href={l.href}
              className="mobile-link"
              style={{ transitionDelay: open ? `${0.08 + i * 0.05}s` : "0s" }}
            >
              {l.label}
            </Link>
          ))}
          <Link
            href="/contact"
            className="mobile-link"
            style={{ transitionDelay: open ? "0.28s" : "0s" }}
          >
            Request a Visit
          </Link>
        </nav>
        <a href={`tel:${site.phoneHref}`} className="btn btn-primary btn-lg mobile-call">
          <PhoneIcon /> Call {site.phone}
        </a>
      </div>

      {/* Sticky call bar — mobile only */}
      <div className="callbar">
        <a href={`tel:${site.phoneHref}`} className="callbar-phone">
          <PhoneIcon /> Call Now
        </a>
        <Link href="/contact" className="callbar-visit">
          Request a Visit
        </Link>
      </div>
    </>
  );
}

function PhoneIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92Z"
        fill="currentColor"
      />
    </svg>
  );
}
