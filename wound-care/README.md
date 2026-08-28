# Wound Care Provider Documentation Kit

A documentation system for providers performing serial debridement and advanced
wound matrix application (Microlyte Ag / tri-membrane wrap) in the SNF, home
health, and outpatient setting.

The goal is a note that does three jobs at once:

1. **Communicates clinically** — the next provider, the facility nurse, and the
   caregiver can all act on it.
2. **Survives an audit** — every billed service is supported by the elements the
   payer actually looks for.
3. **Gets written in the room** — not reconstructed from memory at 9 p.m.

---

## What's here

| File | Use it for |
| --- | --- |
| `progress-note-template.md` | The full fill-in-the-blank note, in the order you actually work through a visit. |
| `smart-phrases.md` | Copy/paste blocks by section. Bracketed `[variables]` are the only things you change. |
| `worked-example-note.md` | A complete note for a real-shaped patient — right trochanteric pressure ulcer, low albumin, thrombocytopenia, venous component, Microlyte application. Read this first. |
| `clinical-reference.md` | Measurement math, healing-trajectory benchmarks, protein targets, the impediment matrix, the infection framework, and the pre-signature audit checklist. |
| `note-builder.html` | Interactive builder — enter this week's and last week's numbers, it computes area, week-over-week change, cumulative change from baseline, and writes the narrative. Open in any browser; nothing is uploaded. |

---

## The visit flow this kit is built around

The template follows the order of the visit so you can chart as you go instead of
reconstructing afterward.

1. **Before you uncover the wound** — interval history, adherence to the turning
   schedule, what the nurse and caregiver report, pain before dressing removal.
2. **On removal** — old dressing condition, drainage strikethrough, adherence to
   the bed, patient tolerance.
3. **Measure before you touch anything** — length, width, depth, undermining.
   Post-debridement numbers are a separate set.
4. **Characterize** — tissue percentages, edges, periwound, exudate, odor.
5. **Compare to last week** — this is the paragraph that justifies continuing,
   escalating, or changing course.
6. **Systemic review** — labs, comorbidity control, nutrition, perfusion,
   offloading. The wound is the readout; these are the causes.
7. **Procedure** — consent, debridement, post-debridement reassessment.
8. **Product application** — consent, lot/size/wastage, technique per IFU.
9. **Dressing stack and orders.**
10. **Education and communication** — who you taught, what you taught, teach-back,
    who you called.
11. **Assessment and plan** — trajectory statement, impediments and what you are
    doing about each, next visit.

---

## Three things this kit words carefully, and why

**Comorbidity control is written as a realistic target, not a guideline number.**
A frail 84-year-old with a trochanteric ulcer is not going to an A1c of 6.5%, and
charting that as the goal makes the rest of the note less credible. The template
asks for the best control this patient can realistically reach, who is managing
it, and what you communicated — which is both more honest and more defensible.

**Low albumin is documented as a marker, not a diagnosis.** Albumin is a negative
acute-phase reactant: it falls with inflammation as much as with protein intake,
and a chronic wound is an inflammatory state. The nutrition section therefore
documents albumin *plus* intake, weight trend, and a specific protein
prescription — so the intervention stands on its own even if a reviewer discounts
the albumin.

**Low platelets are documented with a differential, and antibiotics are tied to
clinical findings.** Thrombocytopenia can accompany severe infection and sepsis
(consumption/DIC), but it is not a reliable marker of localized wound infection —
in fact a *rising* platelet count is the more common acute-phase response. If the
note starts antibiotics on the platelet count alone, that decision is hard to
defend. The template pairs the CBC finding with the clinical infection assessment
(NERDS/STONEES), the culture, and a stated reassessment date, so the antibiotic
decision rests on findings that support it. See `clinical-reference.md` §5.

---

## Billing note

Nothing here is coding advice. The audit checklist in `clinical-reference.md` §8
lists the *clinical* elements that support selective debridement (97597/97598),
excisional debridement (11042–11047), and skin-substitute/CTP application — verify
code selection, modifiers, and units with your coder and payer policy (LCD/NCD)
before submission.
