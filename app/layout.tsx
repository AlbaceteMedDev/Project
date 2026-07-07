import type { Metadata } from "next";
import { Bricolage_Grotesque, Hanken_Grotesk, IBM_Plex_Mono } from "next/font/google";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import { site } from "@/lib/site";
import { boroughs } from "@/lib/boroughs";
import { services } from "@/lib/services";
import "./globals.css";
import "./components.css";

// Display: a characterful grotesque — architectural, confident, editorial.
const display = Bricolage_Grotesque({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

// Body: warm humanist grotesque — deliberately not Inter.
const body = Hanken_Grotesk({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

// Mono: clinical precision for labels, indices, metadata.
const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: {
    default: `${site.name} — Mobile Wound Care Across NYC's Five Boroughs`,
    template: `%s | ${site.name}`,
  },
  description: site.description,
  keywords: [
    "mobile wound care NYC",
    "wound care at home New York",
    "house call wound specialist",
    "diabetic foot ulcer treatment NYC",
    "pressure injury treatment at home",
    "wound care Brooklyn",
    "wound care Queens",
    "wound care Manhattan",
    "wound care Bronx",
    "wound care Staten Island",
    "Timothy Donoho PA",
  ],
  authors: [{ name: site.provider.fullTitle }],
  creator: site.name,
  openGraph: {
    type: "website",
    locale: "en_US",
    url: site.url,
    siteName: site.name,
    title: `${site.name} — Mobile Wound Care Across NYC's Five Boroughs`,
    description: site.description,
  },
  twitter: {
    card: "summary_large_image",
    title: `${site.name} — Mobile Wound Care in NYC`,
    description: site.description,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: { canonical: "./" },
  formatDetection: { telephone: true },
};

/**
 * Practice-level structured data: a MedicalBusiness with its provider,
 * service catalog and full five-borough service area. Emitted on every page.
 */
function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": ["MedicalBusiness", "MedicalClinic"],
    "@id": `${site.url}/#organization`,
    name: site.name,
    description: site.description,
    url: site.url,
    telephone: site.phone,
    email: site.email,
    logo: `${site.url}/icon.svg`,
    image: `${site.url}/opengraph-image`,
    priceRange: "$$",
    medicalSpecialty: "https://schema.org/Dermatology",
    areaServed: boroughs.map((b) => ({
      "@type": "AdministrativeArea",
      name: b.geoName,
    })),
    availableService: services.map((s) => ({
      "@type": "MedicalProcedure",
      name: s.name,
      url: `${site.url}/services/${s.slug}`,
    })),
    founder: {
      "@type": "Person",
      "@id": `${site.url}/about#provider`,
      name: site.provider.name,
      honorificSuffix: "PA",
      jobTitle: "Physician Associate, Wound Care Specialist",
      identifier: {
        "@type": "PropertyValue",
        propertyID: "NPI",
        value: site.provider.npi,
      },
      worksFor: { "@id": `${site.url}/#organization` },
    },
  };
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body>
        <noscript>
          <style>{`.reveal{opacity:1 !important;transform:none !important}`}</style>
        </noscript>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd()) }}
        />
        <Nav />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
