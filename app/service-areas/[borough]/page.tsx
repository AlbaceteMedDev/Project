import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Reveal from "@/components/Reveal";
import ServiceIcon from "@/components/ServiceIcon";
import CTABand from "@/components/CTABand";
import StitchDivider from "@/components/StitchDivider";
import { boroughs, getBorough } from "@/lib/boroughs";
import { services } from "@/lib/services";
import { site } from "@/lib/site";

interface Props {
  params: Promise<{ borough: string }>;
}

export function generateStaticParams() {
  return boroughs.map((b) => ({ borough: b.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { borough: slug } = await params;
  const borough = getBorough(slug);
  if (!borough) return {};
  return {
    title: `${borough.headline} — House Calls by a Wound Specialist`,
    description: `${borough.intro.slice(0, 155)}…`,
    alternates: { canonical: `/service-areas/${borough.slug}` },
  };
}

export default async function BoroughPage({ params }: Props) {
  const { borough: slug } = await params;
  const borough = getBorough(slug);
  if (!borough) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalBusiness",
    name: `${site.name} — ${borough.name}`,
    url: `${site.url}/service-areas/${borough.slug}`,
    telephone: site.phone,
    parentOrganization: { "@id": `${site.url}/#organization` },
    areaServed: { "@type": "AdministrativeArea", name: borough.geoName },
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
            <Link href="/service-areas">Service Areas</Link>
            <span aria-hidden="true">/</span>
            <span>{borough.name}</span>
          </nav>
          <span className="eyebrow">Service area</span>
          <h1>{borough.headline}</h1>
          <p className="section-lede">{borough.intro}</p>
          <div className="hood-chips">
            {borough.neighborhoods.map((n) => (
              <span key={n} className="hood-chip">
                {n}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container grid-2">
          <Reveal>
            <span className="eyebrow">Why house calls here</span>
            <h2 className="section-title">Built for how {borough.name} actually lives.</h2>
            <p className="section-lede">{borough.whyHouseCalls}</p>
            <div className="hero-actions">
              <a href={`tel:${site.phoneHref}`} className="btn btn-primary">
                Call {site.phone}
              </a>
              <Link href="/contact" className="btn btn-ghost">
                Request a {borough.name} Visit
              </Link>
            </div>
          </Reveal>
          <Reveal delay={0.12}>
            <aside className="aside-card" style={{ position: "static" }}>
              <h3>Every service, available in {borough.name}</h3>
              <div className="aside-links">
                {services.map((s) => (
                  <Link key={s.slug} href={`/services/${s.slug}`}>
                    {s.shortName} →
                  </Link>
                ))}
              </div>
            </aside>
          </Reveal>
        </div>
      </section>

      <section className="section section-tint">
        <div className="container">
          <Reveal>
            <span className="eyebrow">Most requested in {borough.name}</span>
            <h2 className="section-title">Common reasons neighbors call us.</h2>
          </Reveal>
          <div className="grid-cards">
            {services.slice(0, 4).map((s, i) => (
              <Reveal key={s.slug} delay={i * 0.06}>
                <Link href={`/services/${s.slug}`} className="card service-card">
                  <ServiceIcon icon={s.icon} />
                  <h3>{s.shortName}</h3>
                  <p>{s.teaser}</p>
                  <span className="card-link">
                    Learn more <span aria-hidden="true">→</span>
                  </span>
                </Link>
              </Reveal>
            ))}
          </div>
          <div style={{ marginTop: "4rem" }}>
            <StitchDivider />
          </div>
        </div>
      </section>

      <CTABand
        title={`Need wound care in ${borough.name} this week?`}
        copy="Call now and we'll find the earliest visit that fits your schedule — urgent wounds are prioritized."
      />
    </>
  );
}
