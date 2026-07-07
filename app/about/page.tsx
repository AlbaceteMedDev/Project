import type { Metadata } from "next";
import Link from "next/link";
import Reveal from "@/components/Reveal";
import CTABand from "@/components/CTABand";
import StitchDivider from "@/components/StitchDivider";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: `About Timothy Donoho, PA — NYC Mobile Wound Care Specialist`,
  description: `Meet Timothy Donoho, PA (NPI ${site.provider.npi}), founder of Apollo Wound Care. A wound care specialist making house calls across Manhattan, Brooklyn, Queens, The Bronx and Staten Island.`,
  alternates: { canonical: "/about" },
};

const values = [
  {
    title: "Show up",
    copy: "Chronic wounds punish inconsistency. The foundation of this practice is reliability — scheduled visits that happen, on time, in your home, every time.",
  },
  {
    title: "Treat the person, not the hole in the skin",
    copy: "A wound is attached to a life: circulation, nutrition, mobility, medications, a bed, a pair of shoes. Every plan accounts for all of it.",
  },
  {
    title: "Measure honestly",
    copy: "Wounds are measured and photographed at every visit. Progress is demonstrated, not assumed — and if a plan isn't working, it changes.",
  },
  {
    title: "Be reachable",
    copy: "Patients and families get a direct line. Questions between visits get answers, not phone trees.",
  },
];

export default function AboutPage() {
  return (
    <>
      <section className="page-hero">
        <div className="container">
          <nav className="breadcrumbs" aria-label="Breadcrumb">
            <Link href="/">Home</Link>
            <span aria-hidden="true">/</span>
            <span>About</span>
          </nav>
          <span className="eyebrow">About the practice</span>
          <h1>The specialist who traded the clinic for the five boroughs.</h1>
          <p className="section-lede">
            Apollo Wound Care is the practice of {site.provider.fullTitle} — a wound care
            specialist who brings the full capability of an outpatient wound center into
            New York City homes.
          </p>
        </div>
      </section>

      <section className="section" id="provider">
        <div className="container provider-grid">
          <Reveal>
            <figure className="provider-portrait">
              <span className="provider-monogram" aria-hidden="true">
                TD
              </span>
              <figcaption>
                <strong>{site.provider.fullTitle}</strong>
                Founder · Wound Care Specialist
              </figcaption>
            </figure>
          </Reveal>
          <Reveal delay={0.1}>
            <span className="eyebrow">Timothy Donoho, PA</span>
            <h2 className="section-title">Why Apollo exists</h2>
            <p className="section-lede">
              Working in wound care, Tim kept seeing the same story: a patient does
              everything right, but the wound still deteriorates — because getting to the
              clinic every week is the hardest part of the prescription. Missed visits,
              worn-out caregivers, wounds dressed by whoever happened to be available.
            </p>
            <p className="section-lede">
              Apollo Wound Care is his answer: one dedicated specialist who comes to the
              patient, carries the clinic in a kit, and stays with the case from first
              evaluation to closed wound. The name is deliberate — Apollo, the classical
              god of healing, whose work was never confined to a single temple.
            </p>
            <div className="provider-creds">
              <span className="cred-chip">Physician Associate (PA)</span>
              <span className="cred-chip">NPI {site.provider.npi}</span>
              <span className="cred-chip">Sharp Debridement</span>
              <span className="cred-chip">NPWT / Wound VAC</span>
              <span className="cred-chip">Compression Therapy</span>
              <span className="cred-chip">Advanced Dressings</span>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="section section-night">
        <div className="container">
          <Reveal>
            <span className="eyebrow">The Apollo standard</span>
            <h2 className="section-title">Four promises, kept at every visit.</h2>
          </Reveal>
          <div className="steps">
            {values.map((v, i) => (
              <Reveal key={v.title} delay={i * 0.1} className="step">
                <h3>{v.title}</h3>
                <p>{v.copy}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <Reveal>
            <span className="eyebrow">Verify the credentials</span>
            <h2 className="section-title">Licensed, registered, accountable.</h2>
            <p className="section-lede">
              Timothy Donoho is a licensed Physician Associate registered with the
              National Plan &amp; Provider Enumeration System under NPI{" "}
              <strong>{site.provider.npi}</strong>. You can verify any provider's NPI
              record at the official{" "}
              <a
                href={`https://npiregistry.cms.hhs.gov/provider-view/${site.provider.npi}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                NPI Registry
              </a>
              .
            </p>
          </Reveal>
          <div style={{ marginTop: "3.5rem" }}>
            <StitchDivider />
          </div>
        </div>
      </section>

      <CTABand
        title="Put a specialist on your care team."
        copy="One call starts it: we'll talk through the wound, verify insurance, and schedule the first home visit."
      />
    </>
  );
}
