import Link from "next/link";
import Emblem from "@/components/Emblem";
import Reveal from "@/components/Reveal";
import Stat from "@/components/Stat";
import ServiceIcon from "@/components/ServiceIcon";
import BoroughMap from "@/components/BoroughMap";
import FaqAccordion from "@/components/FaqAccordion";
import CTABand from "@/components/CTABand";
import StitchDivider from "@/components/StitchDivider";
import { site } from "@/lib/site";
import { services } from "@/lib/services";
import { faqs } from "@/lib/faqs";

const conditions = [
  "Diabetic Foot Ulcers",
  "Pressure Injuries",
  "Venous Leg Ulcers",
  "Surgical Wounds",
  "Arterial Ulcers",
  "Skin Tears",
  "Wound VAC Management",
  "Sharp Debridement",
  "Non-Healing Wounds",
];

const pillars = [
  {
    title: "One clinician, every visit",
    copy: "You see Timothy Donoho, PA at every appointment — the same expert eyes tracking your wound week over week, catching millimeter-level changes a rotating cast of providers would miss.",
  },
  {
    title: "The clinic comes fully stocked",
    copy: "Advanced dressings, debridement instruments, compression systems and documentation tools travel in with us. Nothing about a home visit is a lighter version of clinic care.",
  },
  {
    title: "Your home is clinical data",
    copy: "Seeing your actual bed, chair, shower and footwear lets us fix the causes clinics never see. Wound care that ignores the environment treats half the problem.",
  },
  {
    title: "Your doctors stay in the loop",
    copy: "Every visit generates documentation shared with your PCP, specialists and home-care agency — one connected team instead of siloed appointments.",
  },
];

export default function HomePage() {
  return (
    <>
      {/* ============ HERO ============ */}
      <section className="hero">
        <div className="container hero-inner">
          <div>
            <Reveal>
              <span className="hero-kicker">Now serving all five boroughs</span>
              <h1 className="hero-title">
                Wound care that <em>comes to you.</em>
              </h1>
              <p className="hero-lede">
                Specialist-level treatment for chronic and complex wounds — delivered to
                your home, anywhere in New York City. No waiting rooms, no travel, no
                missed visits. Just healing, led personally by{" "}
                <strong>{site.provider.fullTitle}</strong>.
              </p>
              <div className="hero-actions">
                <a href={`tel:${site.phoneHref}`} className="btn btn-primary btn-lg">
                  Call {site.phone}
                </a>
                <Link href="/contact" className="btn btn-ghost btn-lg">
                  Request a Visit
                </Link>
              </div>
              <div className="hero-trust">
                <span className="hero-trust-item">
                  <Check /> Licensed PA · NPI {site.provider.npi}
                </span>
                <span className="hero-trust-item">
                  <Check /> Medicare &amp; major plans
                </span>
                <span className="hero-trust-item">
                  <Check /> Hospital-grade care at home
                </span>
              </div>
            </Reveal>
          </div>

          <Reveal delay={0.15} className="hero-figure">
            <div className="hero-figure-ring">
              <Emblem size="58%" strand="#F7F4EC" accent="#D8B96E" casing="#0B2E1F" />
              <div className="plate-row plate-row-top" aria-hidden="true">
                <span>Fig. 01 — The Healing Knot</span>
                <span>Est. NYC</span>
              </div>
              <div className="plate-row plate-row-bottom">
                <span>{site.provider.fullTitle}</span>
                <span>NPI {site.provider.npi}</span>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ============ CONDITIONS MARQUEE ============ */}
      <div className="marquee" aria-hidden="true">
        <div className="marquee-track">
          {[...conditions, ...conditions].map((c, i) => (
            <span key={i} className="marquee-item">
              {c}
            </span>
          ))}
        </div>
      </div>

      {/* ============ SERVICES ============ */}
      <section className="section" id="services">
        <div className="container">
          <Reveal>
            <span className="eyebrow">01 / What we treat</span>
            <h2 className="section-title">Complete wound care, without the wound center.</h2>
            <p className="section-lede">
              Every service an outpatient wound clinic offers — assessment, debridement,
              advanced dressings, compression, negative pressure therapy — performed at
              your bedside by a dedicated specialist.
            </p>
          </Reveal>
          <div className="grid-cards">
            {services.map((s, i) => (
              <Reveal key={s.slug} delay={Math.min(i * 0.06, 0.3)}>
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

      {/* ============ HOW IT WORKS + STATS ============ */}
      <section className="section section-night">
        <div className="container">
          <Reveal>
            <span className="eyebrow">02 / How it works</span>
            <h2 className="section-title">From first call to closed wound.</h2>
          </Reveal>
          <div className="steps">
            {[
              {
                t: "Reach out",
                c: "Call or send a visit request. Patients, family members, physicians and home-care agencies can all refer — no paperwork required to start.",
              },
              {
                t: "We come to you",
                c: "Timothy arrives at your home with a fully equipped mobile wound kit and performs a comprehensive evaluation — measurements, photos, circulation checks.",
              },
              {
                t: "Treatment begins day one",
                c: "Debridement, advanced dressings, compression or wound VAC setup happen at that first visit whenever clinically appropriate.",
              },
              {
                t: "Heal on schedule",
                c: "Recurring visits track progress objectively, adjust the plan, and keep your physicians informed — until the wound is closed, not just covered.",
              },
            ].map((step, i) => (
              <Reveal key={step.t} delay={i * 0.1} className="step">
                <h3>{step.t}</h3>
                <p>{step.c}</p>
                <svg className="step-connector" viewBox="0 0 36 12" fill="none" aria-hidden="true">
                  <path d="M0 6h32m0 0-5-5m5 5-5 5" stroke="currentColor" strokeWidth="1.5" />
                </svg>
              </Reveal>
            ))}
          </div>
          <Reveal>
            <div className="stats-band">
              <Stat value={5} label="Boroughs served" />
              <Stat value={8} label="Wound care services" />
              <Stat value={1} label="Dedicated specialist" />
              <Stat value={0} label="Waiting rooms" />
            </div>
          </Reveal>
        </div>
      </section>

      {/* ============ BOROUGH MAP ============ */}
      <section className="section" id="service-areas">
        <div className="container">
          <Reveal>
            <span className="eyebrow">03 / Where we go</span>
            <h2 className="section-title">If it's in the five boroughs, it's a house call.</h2>
            <p className="section-lede">
              Explore the map — Apollo Wound Care travels to every corner of New York
              City, from Riverdale to Tottenville and Inwood to Far Rockaway.
            </p>
          </Reveal>
          <Reveal delay={0.1}>
            <BoroughMap />
          </Reveal>
        </div>
      </section>

      {/* ============ PROVIDER ============ */}
      <section className="section section-tint">
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
          <Reveal delay={0.12}>
            <span className="eyebrow">04 / Your specialist</span>
            <h2 className="section-title">The same expert at your door, every time.</h2>
            <p className="section-lede">
              Apollo Wound Care was founded by Timothy Donoho, PA on a simple conviction:
              the patients who most need expert wound care are the ones least able to
              travel to it. So the practice was built in reverse — around the patient's
              kitchen table instead of a clinic's schedule.
            </p>
            <blockquote className="provider-quote">
              "A wound heals in the hours between visits. My job is to make sure every
              one of those hours is working for you."
            </blockquote>
            <div className="provider-creds">
              <span className="cred-chip">Physician Associate (PA)</span>
              <span className="cred-chip">NPI {site.provider.npi}</span>
              <span className="cred-chip">Wound Care Specialist</span>
              <span className="cred-chip">All 5 Boroughs</span>
            </div>
            <div className="hero-actions">
              <Link href="/about" className="btn btn-primary">
                Meet Tim
              </Link>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ============ DIFFERENCE ============ */}
      <section className="section">
        <div className="container">
          <Reveal>
            <span className="eyebrow">05 / The Apollo standard</span>
            <h2 className="section-title">Why house calls heal faster.</h2>
          </Reveal>
          <div className="pillars">
            {pillars.map((p, i) => (
              <Reveal key={p.title} delay={i * 0.07} className="pillar">
                <h3>
                  <span className="pillar-mark" aria-hidden="true" />
                  {p.title}
                </h3>
                <p>{p.copy}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ============ FAQ PREVIEW ============ */}
      <section className="section section-tint">
        <div className="container">
          <div className="faq-home">
            <Reveal className="faq-home-intro">
              <span className="eyebrow">06 / Questions, answered</span>
              <h2 className="section-title">Everything families ask us first.</h2>
              <p>
                Straight answers on insurance, referrals, and what actually happens at
                the first home visit. Still unsure? A real person picks up.
              </p>
              <div className="faq-home-actions">
                <a href={`tel:${site.phoneHref}`} className="btn btn-primary">
                  Call {site.phone}
                </a>
                <Link href="/faq" className="btn btn-ghost">
                  All questions →
                </Link>
              </div>
            </Reveal>
            <Reveal delay={0.1}>
              <FaqAccordion faqs={faqs.slice(0, 5)} />
            </Reveal>
          </div>
          <div style={{ marginTop: "4rem" }}>
            <StitchDivider />
          </div>
        </div>
      </section>

      <CTABand />
    </>
  );
}

function Check() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="11" fill="currentColor" opacity="0.15" />
      <path
        d="m7 12.5 3.2 3L17 8.5"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
