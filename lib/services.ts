export interface Service {
  slug: string;
  name: string;
  shortName: string;
  /** One-line teaser used on cards and in meta descriptions. */
  teaser: string;
  /** Longer intro paragraph for the service detail page. */
  intro: string;
  /** What a visit for this condition typically involves. */
  visitIncludes: string[];
  /** Who this service is for. */
  bestFor: string[];
  /** Icon key rendered by <ServiceIcon /> */
  icon: "foot" | "bed" | "vein" | "artery" | "suture" | "shield" | "scalpel" | "pump";
}

export const services: Service[] = [
  {
    slug: "diabetic-foot-ulcers",
    name: "Diabetic Foot Ulcer Care",
    shortName: "Diabetic Ulcers",
    teaser:
      "Specialized in-home treatment for diabetic foot ulcers — offloading, debridement and advanced dressings to protect the limb.",
    intro:
      "Diabetic foot ulcers are among the most serious wounds a person can develop — left untreated, they are a leading cause of hospitalization and amputation. Apollo Wound Care brings the full diabetic wound protocol to your home: thorough assessment, sharp debridement when indicated, advanced moisture-balanced dressings, offloading strategy, and close monitoring for infection, all coordinated with your podiatrist, endocrinologist and primary care physician.",
    visitIncludes: [
      "Comprehensive foot and wound assessment, including circulation and sensation checks",
      "Sharp debridement of nonviable tissue when clinically indicated",
      "Advanced dressing selection matched to your wound's stage and drainage",
      "Offloading and footwear guidance to take pressure off the ulcer",
      "Infection surveillance and rapid escalation if warning signs appear",
      "Progress documentation shared with your care team",
    ],
    bestFor: [
      "People with diabetes who have a new or non-healing foot wound",
      "Patients recently discharged after a foot infection or procedure",
      "Anyone who finds it difficult to travel to a wound center every week",
    ],
    icon: "foot",
  },
  {
    slug: "pressure-injuries",
    name: "Pressure Injury (Bedsore) Treatment",
    shortName: "Pressure Injuries",
    teaser:
      "Stage I–IV pressure injury care at the bedside — debridement, support-surface guidance and a plan the whole care team can follow.",
    intro:
      "Pressure injuries — bedsores — develop when patients spend long hours in a bed or chair, and they can deteriorate quickly without expert care. Because Apollo Wound Care treats you where you live, we can address the actual environment causing the wound: your mattress, your chair, your positioning routine. Visits combine staging and measurement, debridement when needed, and hands-on training for family members and aides so healing continues between visits.",
    visitIncludes: [
      "Accurate staging and measurement of the pressure injury",
      "Debridement of devitalized tissue when clinically indicated",
      "Dressing plans that caregivers can realistically maintain",
      "Support-surface and repositioning recommendations for your actual bed and chair",
      "Nutrition screening — healing requires protein and calories",
      "Caregiver coaching at the bedside",
    ],
    bestFor: [
      "Patients who are bed-bound or chair-bound",
      "Families caring for a loved one at home after hospitalization",
      "Residents of adult homes and assisted living who need a wound specialist on site",
    ],
    icon: "bed",
  },
  {
    slug: "venous-leg-ulcers",
    name: "Venous Leg Ulcer Care",
    shortName: "Venous Ulcers",
    teaser:
      "Compression-based healing for venous stasis ulcers — the gold standard, delivered in your living room.",
    intro:
      "Venous leg ulcers develop when weakened leg veins allow blood to pool, breaking down the skin near the ankle. The evidence is clear: these wounds heal with consistent compression therapy and disciplined wound care — two things that are hard to keep up when every treatment means a trip across town. Apollo Wound Care brings gold-standard compression, cleansing and dressing changes to you, on a schedule your legs can count on.",
    visitIncludes: [
      "Vascular screening to confirm compression is safe for you",
      "Multi-layer compression wrapping by a trained clinician",
      "Wound cleansing, debridement as indicated, and exudate management",
      "Skin care for the fragile tissue around the ulcer",
      "Elevation and activity guidance that fits your routine",
      "Coordination with vascular specialists when studies or procedures are needed",
    ],
    bestFor: [
      "Adults with swollen legs and a weeping or crusted ankle wound",
      "Patients whose ulcers keep returning after they 'heal'",
      "Anyone struggling to attend weekly compression appointments",
    ],
    icon: "vein",
  },
  {
    slug: "arterial-ulcers",
    name: "Arterial & Ischemic Wound Care",
    shortName: "Arterial Ulcers",
    teaser:
      "Careful, circulation-first management of arterial wounds, coordinated closely with vascular specialists.",
    intro:
      "Arterial ulcers are wounds starved of blood flow — and they demand a fundamentally different strategy than other wounds. Aggressive debridement or the wrong dressing can make an ischemic wound worse. Timothy Donoho, PA evaluates perfusion first, protects what is viable, keeps the wound stable and infection-free, and works hand-in-hand with vascular surgeons so revascularization happens at the right moment.",
    visitIncludes: [
      "Perfusion-focused assessment including pulse checks",
      "Conservative, circulation-appropriate wound management",
      "Dry, protective dressing strategies for ischemic tissue",
      "Pain management guidance",
      "Fast-track referrals to vascular specialists across NYC",
      "Close-interval monitoring so any deterioration is caught early",
    ],
    bestFor: [
      "Patients with known peripheral arterial disease and a new wound",
      "Painful, punched-out wounds on feet, toes or shins",
      "Patients awaiting or recovering from vascular procedures",
    ],
    icon: "artery",
  },
  {
    slug: "surgical-wounds",
    name: "Post-Surgical Wound Care",
    shortName: "Surgical Wounds",
    teaser:
      "Incision checks, dehiscence management and suture or staple removal — recover from surgery without leaving home.",
    intro:
      "The days after surgery are when wounds are won or lost. Apollo Wound Care manages healing incisions, treats surgical wounds that have opened (dehiscence), removes sutures and staples on schedule, and watches closely for infection — so a complication is caught on day one, not at your six-week follow-up. We report directly to your surgeon so everyone stays on the same page.",
    visitIncludes: [
      "Incision assessment and infection surveillance",
      "Management of dehisced (opened) surgical wounds",
      "Suture and staple removal",
      "Packing changes for wounds healing by secondary intention",
      "Drain site care and monitoring",
      "Direct communication with your surgical team",
    ],
    bestFor: [
      "Patients discharged home after abdominal, orthopedic, cardiac or plastic surgery",
      "Surgical wounds that have opened, drain, or look red and angry",
      "Anyone who can't easily get back to their surgeon's office",
    ],
    icon: "suture",
  },
  {
    slug: "traumatic-wounds",
    name: "Traumatic Wounds & Skin Tears",
    shortName: "Trauma & Skin Tears",
    teaser:
      "Lacerations, skin tears, burns and abrasions treated promptly at home — especially vital for older adults with fragile skin.",
    intro:
      "A skin tear from a fall or a laceration that won't close can spiral into a chronic wound, especially in older adults with thin, fragile skin or in anyone taking blood thinners. Apollo Wound Care treats traumatic wounds in the home promptly — thorough cleansing, closure strategies appropriate for fragile skin, tetanus review and follow-up until the wound is fully healed, not just covered.",
    visitIncludes: [
      "Wound cleansing and foreign-material removal",
      "Closure strategies appropriate for fragile or thin skin",
      "Minor burn assessment and dressing",
      "Hematoma and bruising evaluation for patients on blood thinners",
      "Fall-context review — treating the wound and flagging the cause",
      "Scheduled follow-up until full closure",
    ],
    bestFor: [
      "Older adults with skin tears after a fall or bump",
      "Patients on anticoagulants whose minor wounds keep bleeding or bruising",
      "Home-bound patients who would otherwise wait in an ER for hours",
    ],
    icon: "shield",
  },
  {
    slug: "wound-debridement",
    name: "Sharp Wound Debridement",
    shortName: "Debridement",
    teaser:
      "Bedside sharp debridement — removing dead tissue so healthy tissue can finally heal.",
    intro:
      "Dead, devitalized tissue is the single biggest roadblock to wound healing: it feeds bacteria and physically blocks new tissue from forming. Sharp debridement — the careful removal of that tissue with sterile instruments — is one of the most effective procedures in wound medicine, and Timothy Donoho, PA performs it safely at the bedside, with appropriate pain control, sterile technique and immediate post-procedure dressing.",
    visitIncludes: [
      "Candidacy assessment — debridement is powerful, but not right for every wound",
      "Conservative sharp debridement with sterile instruments",
      "Local pain-control measures before and during the procedure",
      "Immediate advanced dressing application afterward",
      "Serial debridement scheduling for heavily burdened wounds",
      "Tissue-response tracking visit over visit",
    ],
    bestFor: [
      "Wounds coated with slough or black eschar",
      "Chronic wounds that have plateaued and stopped improving",
      "Patients told they need 'weekly debridement at the wound center' but can't get there",
    ],
    icon: "scalpel",
  },
  {
    slug: "advanced-therapies",
    name: "Advanced Therapies & NPWT",
    shortName: "Advanced Therapies",
    teaser:
      "Wound VAC (NPWT) management, cellular tissue products and advanced modalities — hospital-grade care in the home.",
    intro:
      "Modern wound care goes far beyond gauze. Apollo Wound Care manages negative pressure wound therapy (wound VACs) in the home, applies cellular and tissue-based products (skin substitutes) to qualifying wounds, and matches advanced antimicrobial and collagen dressings to each wound's biology. If your wound needs hospital-grade technology, you shouldn't need a hospital bed to get it.",
    visitIncludes: [
      "Negative pressure wound therapy (wound VAC) application and canister/dressing changes",
      "Cellular and tissue-based product (skin substitute) application for qualifying wounds",
      "Advanced antimicrobial, collagen and foam dressing systems",
      "Therapy troubleshooting — alarms, leaks, seal issues",
      "Insurance documentation for advanced modality coverage",
      "Outcome tracking with photographic documentation",
    ],
    bestFor: [
      "Patients discharged with a wound VAC and no one to manage it",
      "Chronic wounds that have failed standard dressings",
      "Wounds a physician has recommended for skin-substitute grafting",
    ],
    icon: "pump",
  },
];

export function getService(slug: string): Service | undefined {
  return services.find((s) => s.slug === slug);
}
