import type { Metadata } from "next";
import Link from "next/link";
import Reveal from "@/components/Reveal";
import ServiceIcon from "@/components/ServiceIcon";
import CTABand from "@/components/CTABand";
import { services } from "@/lib/services";

export const metadata: Metadata = {
  title: "Mobile Wound Care Services — Debridement, Ulcer Care, NPWT at Home",
  description:
    "Every wound center service, delivered at home across NYC: diabetic foot ulcer care, pressure injury treatment, venous ulcer compression, sharp debridement, wound VAC management and more.",
  alternates: { canonical: "/services" },
};

export default function ServicesPage() {
  return (
    <>
      <section className="page-hero">
        <div className="container">
          <nav className="breadcrumbs" aria-label="Breadcrumb">
            <Link href="/">Home</Link>
            <span aria-hidden="true">/</span>
            <span>Services</span>
          </nav>
          <span className="eyebrow">Services</span>
          <h1>A complete wound center, in a house-call kit.</h1>
          <p className="section-lede">
            Apollo Wound Care delivers the full scope of specialist wound treatment in
            the home — the same procedures, products and documentation you'd receive at
            a hospital outpatient wound center, without the trip.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="grid-cards" style={{ marginTop: 0 }}>
            {services.map((s, i) => (
              <Reveal key={s.slug} delay={Math.min(i * 0.05, 0.25)}>
                <Link href={`/services/${s.slug}`} className="card service-card">
                  <ServiceIcon icon={s.icon} />
                  <h3>{s.name}</h3>
                  <p>{s.teaser}</p>
                  <span className="card-link">
                    Explore this service <span aria-hidden="true">→</span>
                  </span>
                </Link>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <CTABand
        title="Not sure which service fits?"
        copy="Describe the wound over the phone and we'll tell you honestly what it needs — and whether a house call is the right setting for it."
      />
    </>
  );
}
