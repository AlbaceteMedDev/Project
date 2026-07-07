# Apollo Wound Care — Website

Marketing site for **Apollo Wound Care**, the mobile wound care practice of
**Timothy Donoho, PA** (NPI 1407323421), serving all five boroughs of New York City.

**Live now:** https://apollo-wound-care.higgsfield.app (static-export
deployment; canonical URLs point at this address via `NEXT_PUBLIC_SITE_URL`
until the production domain is connected on Vercel).

Built with Next.js (App Router) + hand-crafted CSS. No UI framework — the design
system, logo and every illustration are bespoke to this brand.

## Deploying to Vercel

1. Go to [vercel.com/new](https://vercel.com/new) and import this repository.
2. Vercel auto-detects Next.js — no configuration needed. Click **Deploy**.
3. Add the production domain under **Settings → Domains** once purchased
   (e.g. `apollowoundcare.com`).

## ⚠️ Before going live — replace the placeholders

All editable business facts live in **`lib/site.ts`**:

| Field | Current value | Action |
|---|---|---|
| `phone` / `phoneHref` | `(929) 555-0134` | **Placeholder — replace** with the real practice number |
| `email` | `care@apollowoundcare.com` | **Placeholder — replace** with the real inbox |
| `url` | `https://www.apollowoundcare.com` | Set to the real production domain (drives canonical URLs, sitemap and JSON-LD) |
| `hours` | Mon–Sat, 8am–6pm | Confirm with Tim |

Also review before launch:

- **Copy claims** — statements like "Medicare & major plans" and scheduling
  turnaround live in `lib/faqs.ts`, `app/page.tsx` and `lib/services.ts`.
  Have Tim confirm each one.
- **Provider portrait** — the About/home pages currently use a styled "TD"
  monogram. Swap in a professional photo of Tim when available
  (`.provider-portrait` in `app/about/page.tsx` and `app/page.tsx`).
- **Testimonials** — intentionally **not** included. Never publish patient
  reviews without written consent; when you have consented reviews, add a
  section to the home page.
- **Contact form** — submits via the visitor's email client (`mailto:`), so no
  PHI is stored anywhere. To capture requests server-side instead, replace
  `handleSubmit` in `components/ContactForm.tsx` with a POST to a form service
  or an API route wired to a HIPAA-appropriate inbox.

## SEO features included

- Unique metadata + canonical URL on every page
- JSON-LD structured data: `MedicalBusiness` (site-wide), `Person` w/ NPI,
  `MedicalProcedure` (each service), `FAQPage`, `BreadcrumbList`, `ContactPage`
- Dedicated, uniquely-written landing pages per borough (`/service-areas/*`)
  and per service (`/services/*`) — 19 indexable pages total
- `sitemap.xml`, `robots.txt`, web manifest, OG/Twitter cards with a generated
  Open Graph image
- Fully static output (every page pre-rendered), semantic HTML, accessible
  interactive components, `prefers-reduced-motion` support

## Development

```bash
npm install
npm run dev    # http://localhost:3000
npm run build  # production build
```
