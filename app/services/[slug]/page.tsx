import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Reveal from "@/components/Reveal";
import ServiceIcon from "@/components/ServiceIcon";
import CTABand from "@/components/CTABand";
import { services, getService } from "@/lib/services";
import { boroughs } from "@/lib/boroughs";
import { site } from "@/lib/site";

interface Props {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return services.map((s) => ({ slug: s.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const service = getService(slug);
  if (!service) return {};
  return {
    title: `${service.name} at Home in NYC`,
    description: `${service.teaser} House calls by ${site.provider.fullTitle} across all five NYC boroughs.`,
    alternates: { canonical: `/services/${service.slug}` },
  };
}

export default async function ServicePage({ params }: Props) {
  const { slug } = await params;
  const service = getService(slug);
  if (!service) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "MedicalProcedure",
    name: service.name,
    description: service.teaser,
    url: `${site.url}/services/${service.slug}`,
    provider: { "@id": `${site.url}/#organization` },
  };

  const breadcrumbLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: site.url },
      { "@type": "ListItem", position: 2, name: "Services", item: `${site.url}/services` },
      { "@type": "ListItem", position: 3, name: service.name },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify([jsonLd, breadcrumbLd]) }}
      />

      <section className="page-hero">
        <div className="container page-hero-grid">
          <div>
            <nav className="breadcrumbs" aria-label="Breadcrumb">
              <Link href="/">Home</Link>
              <span aria-hidden="true">/</span>
              <Link href="/services">Services</Link>
              <span aria-hidden="true">/</span>
              <span>{service.shortName}</span>
            </nav>
            <span className="eyebrow">Service</span>
            <h1>{service.name}</h1>
            <p className="section-lede">{service.intro}</p>
          </div>
          <dl className="facts" aria-label="Quick facts">
            <div className="fact">
              <dt>Setting</dt>
              <dd>Your home, borough-wide</dd>
            </div>
            <div className="fact">
              <dt>Coverage</dt>
              <dd>All five NYC boroughs</dd>
            </div>
            <div className="fact">
              <dt>Referral</dt>
              <dd>Not required to start</dd>
            </div>
            <div className="fact">
              <dt>Clinician</dt>
              <dd>{site.provider.fullTitle}</dd>
            </div>
            <div className="fact">
              <dt>Insurance</dt>
              <dd>Verified before visit one</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="section">
        <div className="container detail-grid">
          <div>
            <Reveal>
              <span className="eyebrow">What a visit includes</span>
              <h2 className="section-title">Delivered at your bedside.</h2>
              <ul className="detail-list">
                {service.visitIncludes.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </Reveal>

            <Reveal delay={0.1}>
              <div style={{ marginTop: "3.5rem" }}>
                <span className="eyebrow">Who this is for</span>
                <h2 className="section-title">You're in the right place if…</h2>
                <ul className="detail-list">
                  {service.bestFor.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </Reveal>
          </div>

          <Reveal delay={0.15}>
            <aside className="aside-card">
              <ServiceIcon icon={service.icon} />
              <h3>Request {service.shortName.toLowerCase()} care</h3>
              <p style={{ fontSize: "var(--text-sm)", color: "rgba(15,32,25,0.65)", marginTop: "0.6rem" }}>
                Available in every borough. Call for the earliest visit, or send a
                request online.
              </p>
              <a href={`tel:${site.phoneHref}`} className="btn btn-primary">
                Call {site.phone}
              </a>
              <Link href="/contact" className="btn btn-ghost">
                Request a Visit
              </Link>
              <div className="aside-links">
                <strong style={{ fontSize: "var(--text-xs)", letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--gold)" }}>
                  Serving
                </strong>
                {boroughs.map((b) => (
                  <Link key={b.slug} href={`/service-areas/${b.slug}`}>
                    {service.shortName} in {b.name} →
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
            <span className="eyebrow">Related services</span>
            <h2 className="section-title">Often paired with</h2>
          </Reveal>
          <div className="grid-cards">
            {services
              .filter((s) => s.slug !== service.slug)
              .slice(0, 3)
              .map((s, i) => (
                <Reveal key={s.slug} delay={i * 0.07}>
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
        </div>
      </section>

      <CTABand />
    </>
  );
}
