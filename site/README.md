# The site

A static site for the teaching kit: the landing page, the note builder, and the
reference documents rendered as web pages.

## Build

```
node site/build.mjs
```

No dependencies. It reads the Markdown in `wound-care/`, renders it to HTML, wraps
the builder in a real document, and writes everything to `site/dist/`.

`site/dist/` is generated — do not edit it. Edit the Markdown in `wound-care/`,
`site/src/index-body.html` for the landing page, or `site/src/site.css` for
styling, then rebuild.

## Deploy to Vercel

`vercel.json` at the repo root already sets the build command and output
directory, so there is nothing to configure.

**From the dashboard:** Add New → Project → import this repository → Deploy.
Vercel reads `vercel.json` and no framework preset is needed.

**From the CLI:**

```
npm i -g vercel
vercel          # preview deploy
vercel --prod   # production
```

## Preview locally

```
node site/build.mjs
npx serve site/dist        # or: python3 -m http.server -d site/dist
```

`cleanUrls` is on in production, so `/reference` serves `reference/index.html`.
Most local static servers resolve directory paths the same way.

## A note on the builder

`wound-care/note-builder.html` is authored as a fragment so it can be published
as an artifact. The build splits its head material from its body and wraps it in
a full HTML document, and adds a small bar linking back into the site. The file
stays the single source — edit it there, not in `dist`.
