import type { Metadata } from "next";
import Link from "next/link";
import Reveal from "@/components/Reveal";
import FaqAccordion from "@/components/FaqAccordion";
import CTABand from "@/components/CTABand";
import { faqs } from "@/lib/faqs";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "FAQ — Mobile Wound Care Questions, Answered",
  description:
    "How mobile wound care works in NYC: insurance, referrals, what happens at the first home visit, which wounds we treat, and how fast you can be seen.",
  alternates: { canonical: "/faq" },
};

export default function FaqPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.question,
      acceptedAnswer: { "@type": "Answer", text: f.answer },
    })),
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
            <span>FAQ</span>
          </nav>
          <span className="eyebrow">FAQ</span>
          <h1>Answers before you even ask.</h1>
          <p className="section-lede">
            The questions patients, families and referring providers ask most. Anything
            missing? <a href={`tel:${site.phoneHref}`}>Call {site.phone}</a> — a person
            answers, not a portal.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <Reveal>
            <FaqAccordion faqs={faqs} />
          </Reveal>
        </div>
      </section>

      <CTABand
        title="Still have a question?"
        copy="The fastest answer is a phone call — we're happy to talk through your situation before you commit to anything."
      />
    </>
  );
}
