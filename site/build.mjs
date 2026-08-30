/* Builds the static site into site/dist.
   No dependencies: a small Markdown subset renderer covers what the kit's docs
   actually use — headings, GFM tables, lists, blockquotes, rules, inline code,
   bold, italic, links. Run with: node site/build.mjs */
import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
const docs = join(root, "wound-care");
const dist = join(here, "dist");

const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const slug = (t) =>
  t.toLowerCase().replace(/[^\w\s-]/g, "").trim().replace(/\s+/g, "-").slice(0, 60);

function inline(t) {
  return esc(t)
    .replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, a, b) =>
      `<a href="${b.replace(/"/g, "&quot;")}">${a}</a>`);
}

function markdown(src) {
  const lines = src.split("\n");
  const out = [];
  const toc = [];
  let i = 0;
  const flushPara = (buf) => { if (buf.length) out.push(`<p>${inline(buf.join(" "))}</p>`); buf.length = 0; };
  let para = [];

  while (i < lines.length) {
    const line = lines[i];

    if (/^\s*$/.test(line)) { flushPara(para); i++; continue; }

    if (/^```/.test(line)) {
      flushPara(para);
      const body = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) body.push(lines[i++]);
      i++;
      out.push(`<pre><code>${esc(body.join("\n"))}</code></pre>`);
      continue;
    }

    const h = /^(#{1,4})\s+(.*)$/.exec(line);
    if (h) {
      flushPara(para);
      const level = h[1].length, text = h[2].trim(), id = slug(text);
      if (level === 2 || level === 3) toc.push({ level, text, id });
      out.push(`<h${level} id="${id}">${inline(text)}</h${level}>`);
      i++; continue;
    }

    if (/^---+\s*$/.test(line)) { flushPara(para); out.push("<hr>"); i++; continue; }

    // GFM table: header row, delimiter row, then body
    if (/^\s*\|/.test(line) && /^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1] || "")) {
      flushPara(para);
      const cells = (r) => r.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const head = cells(line);
      i += 2;
      const body = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) body.push(cells(lines[i++]));
      out.push(
        `<div class="tw"><table><thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join("")}</tr></thead>` +
        `<tbody>${body.map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`
      );
      continue;
    }

    if (/^\s*>/.test(line)) {
      flushPara(para);
      const body = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) body.push(lines[i++].replace(/^\s*>\s?/, ""));
      out.push(`<blockquote>${markdown(body.join("\n")).html}</blockquote>`);
      continue;
    }

    const li = /^(\s*)([-*]|\d+\.)\s+(.*)$/.exec(line);
    if (li) {
      flushPara(para);
      const ordered = /\d/.test(li[2]);
      const items = [];
      while (i < lines.length) {
        const m = /^(\s*)([-*]|\d+\.)\s+(.*)$/.exec(lines[i]);
        if (!m) {
          // continuation line belonging to the previous item
          if (items.length && /^\s{2,}\S/.test(lines[i])) { items[items.length - 1] += " " + lines[i].trim(); i++; continue; }
          break;
        }
        items.push(m[3]); i++;
      }
      out.push(`<${ordered ? "ol" : "ul"}>${items.map((t) => `<li>${inline(t)}</li>`).join("")}</${ordered ? "ol" : "ul"}>`);
      continue;
    }

    para.push(line.trim()); i++;
  }
  flushPara(para);
  return { html: out.join("\n"), toc };
}

const NAV = [
  { href: "/", label: "Overview" },
  { href: "/builder", label: "Note builder" },
  { href: "/reference", label: "Clinical reference" },
  { href: "/playbooks", label: "Etiology playbooks" },
  { href: "/template", label: "Note template" },
  { href: "/phrases", label: "Smart phrases" },
  { href: "/example", label: "Worked example" },
];

function shell({ title, desc, body, active, toc = [], wide = false }) {
  const nav = NAV.map((n) =>
    `<a href="${n.href}"${n.href === active ? ' class="on" aria-current="page"' : ""}>${n.label}</a>`).join("");
  const aside = toc.length
    ? `<aside class="toc"><h2>On this page</h2><nav>${toc
        .map((t) => `<a href="#${t.id}" class="l${t.level}">${esc(t.text)}</a>`).join("")}</nav></aside>`
    : "";
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/site.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🩹</text></svg>">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="top-in">
    <a class="brand" href="/"><span class="brand-m">Wound Care</span><span class="brand-s">Documentation Teaching Kit</span></a>
    <nav class="nav">${nav}</nav>
  </div>
</header>
<div class="banner" role="note">For teaching, not for charting. Use fictional patients — every note the builder produces is marked as a teaching example.</div>
<main id="main" class="${wide ? "wide" : "doc"}">${aside}<div class="body">${body}</div></main>
<footer class="foot">
  <p>Teaching material for wound care documentation. Not clinical advice, and not a substitute for your own judgment, your institution's standards, or a real chart. Nothing here is coding advice — verify codes, modifiers, units and coverage against your own payer policy.</p>
  <p class="foot-s">All example patients are fictional.</p>
</footer>
</body>
</html>`;
}

const PAGES = [
  { file: "clinical-reference.md", out: "reference/index.html", href: "/reference", title: "Clinical Reference", desc: "Measurement math, healing benchmarks, nutrition targets, the impediment matrix, and the infection framework." },
  { file: "etiology-playbooks.md", out: "playbooks/index.html", href: "/playbooks", title: "Etiology Playbooks", desc: "Assessment and plan by wound type: sacral, trochanteric, ischial, heel, venous, diabetic foot, arterial and mixed." },
  { file: "progress-note-template.md", out: "template/index.html", href: "/template", title: "Note Template", desc: "The fill-in progress note, ordered to match the visit." },
  { file: "smart-phrases.md", out: "phrases/index.html", href: "/phrases", title: "Smart Phrases", desc: "Copy-paste documentation blocks by section, including per-etiology assessment and plan." },
  { file: "worked-example-note.md", out: "example/index.html", href: "/example", title: "Worked Example Note", desc: "A complete note for a fictional two-wound patient." },
];

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

// doc pages
for (const p of PAGES) {
  const src = readFileSync(join(docs, p.file), "utf8");
  const { html, toc } = markdown(src);
  const page = shell({ title: `${p.title} — Wound Care Teaching Kit`, desc: p.desc, body: html, active: p.href, toc });
  mkdirSync(join(dist, dirname(p.out)), { recursive: true });
  writeFileSync(join(dist, p.out), page);
}

// the builder: authored as a fragment for the artifact host, so split its head
// material out and wrap it in a real document for the web
const raw = readFileSync(join(docs, "note-builder.html"), "utf8");
const split = raw.indexOf('<div class="wrap">');
if (split < 0) throw new Error("builder: could not find the body boundary");
const headBits = raw.slice(0, split).trim();
const bodyBits = raw.slice(split);
mkdirSync(join(dist, "builder"), { recursive: true });
writeFileSync(join(dist, "builder/index.html"), `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Load a worked wound care visit, change values, and watch a complete teaching note assemble.">
<meta name="robots" content="noindex">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🩹</text></svg>">
${headBits}
<style>
  .site-bar{
    display:flex; flex-wrap:wrap; align-items:center; gap:14px;
    padding:10px 20px; border-bottom:1px solid var(--border);
    background:var(--surface); font-size:13px;
  }
  .site-bar a{color:var(--ink-2); text-decoration:none}
  .site-bar a:hover{color:var(--accent)}
  .site-bar .home{font-weight:600; color:var(--ink)}
  @media print{ .site-bar{display:none !important} }
</style>
</head>
<body>
<div class="site-bar">
  <a class="home" href="/">← Wound Care Teaching Kit</a>
  <a href="/reference">Clinical reference</a>
  <a href="/playbooks">Etiology playbooks</a>
  <a href="/example">Worked example</a>
</div>
${bodyBits}
</body>
</html>`);

// landing page + stylesheet
cpSync(join(here, "src/site.css"), join(dist, "site.css"));
const landing = readFileSync(join(here, "src/index-body.html"), "utf8");
writeFileSync(join(dist, "index.html"), shell({
  title: "Wound Care Documentation — Teaching Kit",
  desc: "A teaching kit for wound care documentation: eight worked cases, an interactive note builder, and the clinical reference behind them.",
  body: landing, active: "/", wide: true,
}));

console.log("built site/dist:", [...PAGES.map(p => p.out), "builder/index.html", "index.html", "site.css"].join(", "));
