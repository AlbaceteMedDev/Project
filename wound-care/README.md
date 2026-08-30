# Wound Care Documentation — A Teaching Kit

Teaching material for wound care documentation: serial debridement and advanced
wound matrix application (Microlyte Ag / tri-membrane wrap) in the SNF, home
health, and outpatient setting.

> **This is for teaching, not for charting.** Every note the builder produces is
> marked *Teaching example — not for clinical use*, and that marker travels into
> the copied text, the PDF, and the Word file. Use fictional patients. Nothing
> here is a substitute for your own clinical judgment, your institution's
> documentation standards, or a real chart.

It teaches a note that does three things at once, because those are the three
tests a real note has to pass:

1. **Communicates clinically** — the next provider, the facility nurse, and the
   caregiver can all act on it.
2. **Holds up on review** — every service is supported by the elements a reader
   actually looks for.
3. **Gets written in the room** — not reconstructed from memory at 9 p.m.

## Start here

Open `note-builder.html` and load one of the three **teaching cases**. Each is a
complete worked visit built around one thing the note has to get right, and every
field stays editable — change a value and watch what the note does.

| Case | What it teaches |
| --- | --- |
| **Deteriorating pressure injury** | Area is flat while depth and undermining grow and infection criteria are met. Area alone is not the trajectory, and the matrix is deferred rather than applied. |
| **Stalled venous ulcer** | Clean, granulating, well-perfused, but under the four-week benchmark after six weeks. The case for advanced therapy, and the consent that goes with it. |
| **Ischemic heel — do not debride** | Dry stable eschar on a poorly perfused heel. The case where the usual treatment is wrong, closure is not the goal, and the reasoning has to be written down or it reads as neglect. |

---

## What's here

| File | Use it for |
| --- | --- |
| `progress-note-template.md` | The full fill-in-the-blank note, in the order you actually work through a visit. |
| `smart-phrases.md` | Copy/paste blocks by section. Bracketed `[variables]` are the only things you change. |
| `worked-example-note.md` | A complete note for a real-shaped patient — right trochanteric pressure ulcer, low albumin, thrombocytopenia, venous component, Microlyte application. Read this first. |
| `clinical-reference.md` | Measurement math, healing-trajectory benchmarks, protein targets, the impediment matrix, the infection framework, and the pre-signature audit checklist. |
| `etiology-playbooks.md` | The wound-type-specific assessment and plan: sacral, trochanteric, ischial, and heel pressure injuries; venous, diabetic foot, arterial, and mixed ulcers. Plus the healable / maintenance / non-healable framework and the deeper A&P structure. |
| `note-builder.html` | Interactive builder. Import a document or enter the visit, and it writes a **complete note you can edit in place** before copying — it computes area, week-over-week and four-week change against the etiology's benchmark, the tissue split, sq cm and % debrided, the protein target and gap, matrix wastage, and the NERDS/STONEES tally. Switch to **Sections** for per-section copy, or turn on **"include the sections I haven't filled in"** to get the full skeleton as headings to type under. Exports to PDF, Word, or the clipboard. One self-contained file — open it in any browser, works offline, nothing is saved or uploaded. |


### Giving this to a learner, and getting a document out

The builder is **one self-contained HTML file**. There is no install, no account,
and no server — which makes it easy to hand round a teaching session, and means
nothing a learner types goes anywhere.

**To hand it to someone:**

1. Download `wound-care/note-builder.html` from this repo (on GitHub, open the
   file and click **Download raw file**).
2. Send them the file — email attachment, shared drive, USB, whatever your
   organization allows for a document.
3. They double-click it. It opens in Chrome, Edge, Safari, or Firefox and works
   immediately, including offline.

Exported notes carry the teaching marker, so a practice note handed in or emailed
around cannot be mistaken for a chart document.

**To get a document out, once they've filled it in:**

| Button | What it produces |
| --- | --- |
| **Print / PDF** | Opens the browser's print dialog — choose **Save as PDF** for a clean, black-on-white clinical note with proper page breaks. Only the note prints; the form does not. |
| **Word** | Saves a real `.docx` named for the patient and date, which opens in Word, Pages, or Google Docs and can be edited further. |
| **Copy note** | Puts the note on the clipboard as plain text, for pasting into the EMR. |

> **In an embedded preview**, **Copy note** and **Word** both work — saving asks
> you to confirm first. **Print / PDF** needs the standalone file, because a
> preview sandbox cannot open a print dialog. The page checks which it can do and
> says so, rather than leaving a dead button.

### Importing from a document

Rather than retyping, drop a document into **Import from a document** at the top
of the form.

- **Last week's note** (the `.docx` this tool exported, or a `.txt` of it) is
  recognised as such: its measurements are offered as **last visit**, so the
  week-over-week and four-week arithmetic carries forward with the patient
  identifiers.
- **A nursing note, discharge summary, or lab report** is scanned for values it
  recognises — labs, vitals, weight, ABI, Braden, tissue percentages, and
  measurements written as `4.5 x 3.4 x 1.1 cm`.
- Reads `.txt`, `.md`, `.csv`, `.html`, and `.docx`. Several files at once merge
  into one list.

**Every value is shown with the line it came from, and nothing is written into
the form until you tick it and press Apply.** A wrong match costs you a glance,
not a wrong note.

> **What this is not.** The page does no AI and makes no network calls — it is
> pattern matching over text, running entirely on your machine. It will miss
> values phrased in ways it does not recognise, and it does not read PDFs
> (that needs a parser this page deliberately does not carry, so it stays one
> offline file). For a PDF, copy the text out and paste it in.

### Using the builder

1. Work down the eleven steps on the left in the order the visit happens.
2. The note assembles on the right as you type. Anything you leave blank is left
   out, or — with **"include the sections I haven't filled in"** ticked — appears
   as a heading with a prompt so you can type under it directly.
3. **Edit the note in place.** Click into it and rewrite anything. From your
   first keystroke, changes to the fields stop overwriting the note, and a bar
   appears offering **Rebuild from fields** if you want to start over.
4. **Copy note** puts the whole thing on the clipboard as plain text for the EMR.

Nothing is saved. Closing the tab discards everything, so export or copy the note
before you leave the page.

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

**Healability is decided before the plan, not after it.** Every wound is
classified **healable**, **maintenance**, or **non-healable / palliative**, and
the classification is written into the note. This is not a formality: in a
non-healable wound, moist wound healing is the *wrong* goal — the wound is kept
dry and stable eschar is preserved rather than debrided. That is correct care,
but only if the record says it was a decision. Otherwise the next clinician reads
it as neglect. See `etiology-playbooks.md` §0.

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
