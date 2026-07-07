import type { Metadata } from "next";
import Link from "next/link";
import Reveal from "@/components/Reveal";
import BoroughMap from "@/components/BoroughMap";
import CTABand from "@/components/CTABand";
import { boroughs } from "@/lib/boroughs";

export const metadata: Metadata = {
  title: "Service Areas — House-Call Wound Care in All 5 NYC Boroughs",
  description:
    "Apollo Wound Care makes wound care house calls throughout Manhattan, Brooklyn, Queens, The Bronx and Staten Island. Find your borough and request an in-home visit.",
  alternates: { canonical: "/service-areas" },
};

export default function ServiceAreasPage() {
  return (
    <>
      <section className="page-hero">
        <div className="container">
          <nav className="breadcrumbs" aria-label="Breadcrumb">
            <Link href="/">Home</Link>
            <span aria-hidden="true">/</span>
            <span>Service Areas</span>
          </nav>
          <span className="eyebrow">Service areas</span>
          <h1>Five boroughs. One standard of care.</h1>
          <p className="section-lede">
            Wherever you are in New York City, Apollo Wound Care comes to you — homes,
            apartments, brownstones, adult homes and assisted-living residences alike.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <Reveal>
            <BoroughMap />
          </Reveal>
        </div>
      </section>

      <section className="section section-tint">
        <div className="container">
          <Reveal>
            <span className="eyebrow">Choose your borough</span>
            <h2 className="section-title">Local pages, local details.</h2>
          </Reveal>
          <div className="grid-cards">
            {boroughs.map((b, i) => (
              <Reveal key={b.slug} delay={i * 0.06}>
                <Link href={`/service-areas/${b.slug}`} className="card service-card">
                  <h3>{b.name}</h3>
                  <p>{b.intro}</p>
                  <span className="card-link">
                    Wound care in {b.name} <span aria-hidden="true">→</span>
                  </span>
                </Link>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <CTABand />
    </>
  );
}
