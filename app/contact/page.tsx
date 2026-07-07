import type { Metadata } from "next";
import Link from "next/link";
import Reveal from "@/components/Reveal";
import ContactForm from "@/components/ContactForm";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Request a Visit — Mobile Wound Care Anywhere in NYC",
  description: `Request an in-home wound care visit from ${site.provider.fullTitle}. Serving Manhattan, Brooklyn, Queens, The Bronx and Staten Island. Call ${site.phone} or send a request online.`,
  alternates: { canonical: "/contact" },
};

export default function ContactPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ContactPage",
    name: `Contact ${site.name}`,
    url: `${site.url}/contact`,
    about: { "@id": `${site.url}/#organization` },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <section className="page-hero">
        <div className="container">
          <nav className="breadcrumbs" aria-label="Breadcrumb">
            <Link href="/">Home</Link>
            <span aria-hidden="true">/</span>
            <span>Request a Visit</span>
          </nav>
          <span className="eyebrow">Request a visit</span>
          <h1>Let's get a specialist to your door.</h1>
          <p className="section-lede">
            Tell us a little about the wound and where you are — we'll handle the rest,
            including insurance verification and coordination with your doctors.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container contact-grid">
          <Reveal>
            <span className="eyebrow">Fastest ways to reach us</span>
            <h2 className="section-title">A person answers.</h2>
            <div className="contact-channels">
              <a href={`tel:${site.phoneHref}`} className="channel">
                <span className="channel-icon" aria-hidden="true">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92Z"
                      fill="currentColor"
                    />
                  </svg>
                </span>
                <span>
                  <strong>{site.phone}</strong>
                  <small>Call or text · {site.hours}</small>
                </span>
              </a>
              <a href={`mailto:${site.email}`} className="channel">
                <span className="channel-icon" aria-hidden="true">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <rect x="2" y="4" width="20" height="16" rx="3" stroke="currentColor" strokeWidth="2" />
                    <path d="m3 7 9 6 9-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                </span>
                <span>
                  <strong>{site.email}</strong>
                  <small>For referrals &amp; records too</small>
                </span>
              </a>
            </div>
            <p
              style={{
                marginTop: "2rem",
                fontSize: "var(--text-sm)",
                color: "rgba(15,32,25,0.65)",
              }}
            >
              <strong>Referring providers &amp; agencies:</strong> we accept referrals by
              phone or email and report back after every visit. Include the patient's
              borough and wound type and we'll respond with availability.
            </p>
          </Reveal>

          <Reveal delay={0.12}>
            <ContactForm />
          </Reveal>
        </div>
      </section>
    </>
  );
}
