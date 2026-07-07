/**
 * Central site configuration.
 *
 * ── EDIT ME BEFORE LAUNCH ─────────────────────────────────────────────
 * The phone number and email below are placeholders. Replace them with
 * the practice's real contact details, and set `url` to the production
 * domain once it is purchased and connected in Vercel.
 * ──────────────────────────────────────────────────────────────────────
 */
export const site = {
  name: "Apollo Wound Care",
  legalName: "Apollo Wound Care",
  tagline: "Expert wound care, delivered to your door.",
  description:
    "Apollo Wound Care brings specialist-level wound treatment to patients at home across all five boroughs of New York City. Led by Timothy Donoho, PA — diabetic ulcers, pressure injuries, venous ulcers, surgical wounds and more, treated where you live.",
  // Canonical origin for metadata, sitemap and JSON-LD. Override per-deploy
  // with NEXT_PUBLIC_SITE_URL; defaults to the future production domain.
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.apollowoundcare.com",
  phone: "(929) 555-0134", // TODO: replace with the practice's real number
  phoneHref: "+19295550134", // TODO: replace with the practice's real number
  email: "care@apollowoundcare.com", // TODO: replace with the practice's real inbox
  hours: "Mon–Sat, 8am–6pm",
  provider: {
    name: "Timothy Donoho",
    credential: "PA-C",
    fullTitle: "Timothy Donoho, PA",
    npi: "1407323421",
  },
  serviceArea: "New York City — Manhattan, Brooklyn, Queens, The Bronx & Staten Island",
} as const;

export type Site = typeof site;
