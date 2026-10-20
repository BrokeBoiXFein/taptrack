# Claude Code kickoff prompt

Paste this as the first message in a new Claude Code session opened in this folder.

---

Read CLAUDE.md and README.md, then look through data/water.json, src/app.html and build.py. We have six days until the Congressional App Challenge deadline (Oct 26, noon ET). Work through this plan in order. Stop after each phase, show me what changed, and wait for my OK.

**Phase 1: Trustworthy data (Oct 21)**
1. Write `tools/extract.py` using pdfplumber: given a report PDF URL, download it, find the rows for 1,4-dioxane, PFOA, PFOS, nitrate and lead (90th percentile), and print the level, range, units and sample date it finds.
2. Run it on every report in data/water.json and print a table comparing each extracted value to the value in the JSON. List every mismatch for me to check by hand. Do not change the JSON without my OK.
3. Add `tests/smoke.test.js` (jsdom) that renders every view for every district and fails on any script error or "undefined"/"NaN" in the page text. Add `npm test`.

**Phase 2: More districts (Oct 22)**
4. Use tools/extract.py to add Hicksville, Glen Cove, Port Washington and Manhasset-Lakeville, 2019 to 2025. Show me each district's values and notes before writing them in.

**Phase 3: Features (Oct 23)**
5. Shareable links: `#district` and `#district-contaminant` open the right view.
6. "New report" banner: if the district's latest report year in the data is older than the current year after June 1, say the new report should be out and link the district's reports page.
7. Spanish, Chinese (Simplified) and Korean versions of the interface text, with a language switch. Contaminant explainers too. Mark machine-translated text so a native speaker can review it.
8. Print-friendly summary view the resident can bring to a district meeting (CSS print styles only).

**Phase 4: Ship (Oct 24)**
9. Push to GitHub, turn on GitHub Pages from /docs, and confirm address search works on the live site with 10 real NY-03 addresses (I will give them to you).
10. Run an accessibility pass: keyboard only, screen reader labels on charts, color contrast in both themes.

**Phase 5: Submission (Oct 25)**
11. Draft a 2 to 3 minute demo video script outline (I will write the final words myself).
12. Make sure notes/AI_LOG.md lists everything AI helped with.

Throughout: follow the data rules in CLAUDE.md, never guess a value, and keep the app a static site.
