import Link from "next/link";
import Logo from "./Logo";
import StitchDivider from "./StitchDivider";
import { site } from "@/lib/site";
import { services } from "@/lib/services";
import { boroughs } from "@/lib/boroughs";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          <Logo tone="dark" casing="#082218" size={52} />
          <p className="footer-tag">{site.tagline}</p>
          <p className="footer-meta">
            {site.provider.fullTitle} · NPI {site.provider.npi}
          </p>
          <a href={`tel:${site.phoneHref}`} className="btn btn-gold footer-call">
            Call {site.phone}
          </a>
        </div>

        <nav className="footer-col" aria-label="Services">
          <h3>Services</h3>
          {services.map((s) => (
            <Link key={s.slug} href={`/services/${s.slug}`}>
              {s.shortName}
            </Link>
          ))}
        </nav>

        <nav className="footer-col" aria-label="Service areas">
          <h3>Service Areas</h3>
          {boroughs.map((b) => (
            <Link key={b.slug} href={`/service-areas/${b.slug}`}>
              {b.name}
            </Link>
          ))}
        </nav>

        <nav className="footer-col" aria-label="Practice">
          <h3>Practice</h3>
          <Link href="/about">About Timothy Donoho, PA</Link>
          <Link href="/faq">Frequently Asked Questions</Link>
          <Link href="/contact">Request a Visit</Link>
          <a href={`mailto:${site.email}`}>{site.email}</a>
        </nav>
      </div>

      <div className="container">
        <StitchDivider tone="dark" />
        <div className="footer-legal">
          <p>
            © {new Date().getFullYear()} {site.legalName}. Serving Manhattan, Brooklyn,
            Queens, The Bronx &amp; Staten Island.
          </p>
          <p className="footer-disclaimer">
            This website provides general information and is not a substitute for
            professional medical advice. If you are experiencing a medical emergency,
            call 911.
          </p>
        </div>
      </div>
    </footer>
  );
}
