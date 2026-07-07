export interface Borough {
  slug: string;
  name: string;
  /** e.g. "Brooklyn, NY" */
  geoName: string;
  headline: string;
  intro: string;
  /** Unique local color for SEO copy — neighborhoods served. */
  neighborhoods: string[];
  /** Borough-specific paragraph about why house calls matter there. */
  whyHouseCalls: string;
}

export const boroughs: Borough[] = [
  {
    slug: "manhattan",
    name: "Manhattan",
    geoName: "Manhattan, New York, NY",
    headline: "Mobile Wound Care in Manhattan",
    intro:
      "From Inwood to the Financial District, Apollo Wound Care brings specialist wound treatment directly to Manhattan apartments, brownstones and senior residences. No crosstown traffic, no waiting rooms — Timothy Donoho, PA comes to you with everything needed for hospital-grade wound care.",
    neighborhoods: [
      "Upper East Side",
      "Upper West Side",
      "Harlem",
      "Washington Heights",
      "Inwood",
      "Midtown",
      "Chelsea",
      "Greenwich Village",
      "Lower East Side",
      "Financial District",
    ],
    whyHouseCalls:
      "Manhattan may have world-class hospitals on every other avenue, but for a patient with a draining leg ulcer, a fifth-floor walk-up and a crosstown bus make weekly wound-center visits nearly impossible. House calls remove every one of those barriers — care arrives at your door, on your schedule, with no waiting room exposure.",
  },
  {
    slug: "brooklyn",
    name: "Brooklyn",
    geoName: "Brooklyn, NY",
    headline: "Mobile Wound Care in Brooklyn",
    intro:
      "Brooklyn is Apollo Wound Care's busiest borough — and for good reason. From Bay Ridge to Bushwick, thousands of Brooklynites live with chronic wounds that need weekly expert attention. We bring that expertise to your home, your family member's home, or your adult-care residence.",
    neighborhoods: [
      "Bay Ridge",
      "Bensonhurst",
      "Borough Park",
      "Flatbush",
      "Canarsie",
      "East New York",
      "Bushwick",
      "Williamsburg",
      "Park Slope",
      "Sheepshead Bay",
      "Brighton Beach",
      "Crown Heights",
    ],
    whyHouseCalls:
      "Brooklyn is New York's most populous borough, and its wound care centers book out weeks in advance. For seniors in Bensonhurst or bed-bound patients in Canarsie, the trip alone can undo a week of healing — pressure injuries worsen with every hour spent sitting in transit. In-home care means treatment happens on time, every time.",
  },
  {
    slug: "queens",
    name: "Queens",
    geoName: "Queens, NY",
    headline: "Mobile Wound Care in Queens",
    intro:
      "Queens is vast — and getting from Far Rockaway or Bayside to a Manhattan wound center is a half-day expedition. Apollo Wound Care erases that distance. Timothy Donoho, PA travels throughout Queens delivering debridement, compression therapy, wound VAC management and advanced dressings at home.",
    neighborhoods: [
      "Astoria",
      "Long Island City",
      "Jackson Heights",
      "Flushing",
      "Bayside",
      "Forest Hills",
      "Jamaica",
      "Richmond Hill",
      "Ozone Park",
      "Far Rockaway",
      "Whitestone",
      "Elmhurst",
    ],
    whyHouseCalls:
      "Queens is the largest borough by area, and its transit map leaves entire neighborhoods — the Rockaways, eastern Queens, College Point — far from any wound specialty center. For the borough's many multigenerational households caring for aging parents at home, a wound specialist who comes to the kitchen table changes everything.",
  },
  {
    slug: "the-bronx",
    name: "The Bronx",
    geoName: "The Bronx, NY",
    headline: "Mobile Wound Care in The Bronx",
    intro:
      "The Bronx carries one of the highest diabetes burdens in New York State — and with it, some of the city's highest rates of diabetic foot ulcers and amputations. Apollo Wound Care exists to bend that curve, bringing limb-preserving wound expertise into Bronx homes from Riverdale to Soundview.",
    neighborhoods: [
      "Riverdale",
      "Kingsbridge",
      "Fordham",
      "Belmont",
      "Pelham Bay",
      "Throgs Neck",
      "Soundview",
      "Hunts Point",
      "Morrisania",
      "Co-op City",
      "Mott Haven",
      "Wakefield",
    ],
    whyHouseCalls:
      "Research consistently shows that regular, uninterrupted wound care is what saves limbs — and missed appointments are what costs them. In a borough where many patients juggle dialysis schedules, limited mobility and long bus transfers, bringing the specialist to the patient removes the single biggest predictor of a bad outcome: the missed visit.",
  },
  {
    slug: "staten-island",
    name: "Staten Island",
    geoName: "Staten Island, NY",
    headline: "Mobile Wound Care on Staten Island",
    intro:
      "Staten Islanders know the routine: the ferry, the bridge traffic, the trek to appointments in Brooklyn or Manhattan. Apollo Wound Care makes the trip so you don't have to — full-service mobile wound care from St. George to Tottenville, in your home and on your schedule.",
    neighborhoods: [
      "St. George",
      "Stapleton",
      "Port Richmond",
      "West Brighton",
      "New Dorp",
      "Great Kills",
      "Eltingville",
      "Annadale",
      "Tottenville",
      "Willowbrook",
    ],
    whyHouseCalls:
      "Staten Island has the fewest specialty wound resources of any borough relative to its population, and for South Shore residents, reaching one can mean two hours of travel each way. A home visit replaces that entire ordeal with a knock on the door — and for post-surgical patients told not to drive, it is often the only realistic way to get expert wound care at all.",
  },
];

export function getBorough(slug: string): Borough | undefined {
  return boroughs.find((b) => b.slug === slug);
}
