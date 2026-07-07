import type { Service } from "@/lib/services";

/** Hand-drawn line icons, one per service, in the brand's stroke style. */
export default function ServiceIcon({ icon }: { icon: Service["icon"] }) {
  return (
    <span className="service-icon" aria-hidden="true">
      <svg
        viewBox="0 0 48 48"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
        width="30"
        height="30"
      >
        {paths[icon]}
      </svg>
    </span>
  );
}

const paths: Record<Service["icon"], React.ReactNode> = {
  // footprint with pulse — diabetic foot ulcers
  foot: (
    <>
      <path d="M18 6c6 0 9 5 9 11 0 5-2 7-2 11h-11c-1-4-3-6-3-11 0-6 2-11 7-11Z" />
      <path d="M14 33h11l-.6 5a5 5 0 0 1-9.8 0L14 33Z" />
      <path d="M31 15h4l2-4 3 8 2-4h3" opacity="0.9" />
    </>
  ),
  // bed with patient — pressure injuries
  bed: (
    <>
      <path d="M4 14v20M4 28h40v6M4 24h40" />
      <circle cx="11" cy="19" r="3.4" />
      <path d="M17 24c0-3 2.5-5 6-5h13a8 8 0 0 1 8 5" />
    </>
  ),
  // leg with compression bands — venous ulcers
  vein: (
    <>
      <path d="M20 4c0 10 2 14 2 22 0 6-1 9-1 14h10c0-5 2-9 2-16 0-8-3-11-3-20" />
      <path d="M20 15h11M20.5 21h11M21 27h11M20 33h11" opacity="0.9" />
    </>
  ),
  // heart with flow line — arterial wounds
  artery: (
    <>
      <path d="M24 40S8 30 8 18a8.5 8.5 0 0 1 16-4 8.5 8.5 0 0 1 16 4c0 12-16 22-16 22Z" />
      <path d="M13 21h6l2.5-5 4 9 2.5-4h7" />
    </>
  ),
  // sutured incision — surgical wounds
  suture: (
    <>
      <path d="M8 30C16 20 32 20 40 30" />
      <path d="M13 21.5 17 29M20 19.5l2.5 8M28 19.5 25.5 28M35 21.5 31 29" />
    </>
  ),
  // shield with cross — trauma protection
  shield: (
    <>
      <path d="M24 4 40 10v12c0 10-6.5 17.5-16 22C14.5 39.5 8 32 8 22V10L24 4Z" />
      <path d="M24 16v14M17 23h14" />
    </>
  ),
  // scalpel over healing curve — debridement
  scalpel: (
    <>
      <path d="M38 6 18 26l-8 4 4-8L34 2c2-1 5 2 4 4Z" />
      <path d="M10 40c8 4 20 4 28 0" />
      <path d="M14 34l4 4M30 38l2-4" opacity="0" />
    </>
  ),
  // NPWT pump with tubing — advanced therapies
  pump: (
    <>
      <rect x="6" y="18" width="22" height="18" rx="3" />
      <path d="M12 26h4l2-4 3 8 2-4h3" />
      <path d="M28 24h6c4 0 6-3 6-7V8" />
      <circle cx="40" cy="6" r="2.4" />
    </>
  ),
};
