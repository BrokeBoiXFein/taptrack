# TapTrack work log (Claude Code sessions)

A plain record of everything Claude Code did on TapTrack, in order, from the first session on 2026-10-20 to 2026-10-22. It backs up the short entries in `notes/AI_LOG.md` for the Congressional App Challenge AI disclosure. Ayaan made the decisions noted below; Claude wrote the code, gathered and checked data, and drafted text inside the app.

Before these sessions (2026-10-14 to 2026-10-20, in Claude chat): research on NY-03 issues and past winners, idea comparison, review of H2OScore, first transcription of Jericho and Plainview data, first version of the app and build script.

---

## 2026-10-20: Starting point

- Read `CLAUDE.md`, `notes/KICKOFF.md`, `README.md`, `data/water.json`, `src/app.html`, `build.py`. Followed the kickoff plan phase by phase.

## Phase 1: Trustworthy data

**Report checker (`tools/extract.py`)**
- Wrote a pdfplumber script that downloads a district report (cached in `tools/.cache/`, ignored by git), finds the rows for 1,4-dioxane, PFOA, PFOS, nitrate and lead, and prints numbers, units, sample dates and "ND" marks.
- `--check` mode compares every value in `data/water.json` to its report and lists anything to check by hand. It never edits the data.

**Smoke test (`tests/smoke.test.js`, `package.json`)**
- jsdom test that renders every view for every district and fails on script errors or "undefined", "NaN", "[object Object]" in the page. Run with `npm test`.

**Fixes**
- `build.py` read and wrote files without an encoding, which garbles "µ" on Windows. Now UTF-8.
- `npm test` pointed at the `tests/` folder, which Node 24 reads as a file. Changed to `tests/*.test.js`.

**Setup help**
- Helped Ayaan cd into a folder with a space in its name, install Python (winget) and pdfplumber.

**Data check results**
- All 47 values matched their report rows. Small round numbers were checked against the right column by hand.
- Ayaan's decisions:
  - Plainview PFOA/PFOS 2021 to 2022 and PFOS 2025 are listed as "tested but not detected", so they were changed from blank to 0 (ND).
  - Jericho 2024 report prints PFOA's limit as 50,000 ng/L (the limit for other PFAS); added as a report-error note after confirming it in the PDF.
  - Plainview 2017 lead sampling had one home at 91.7 µg/L; added as a note.
  - Jericho PFOS 2024 and 2025 left blank (not in the tables).
- The checker learned to recognize "tested but not detected" lists.

## 2026-10-22: Making the app friendlier

**Encoding bug**
- Units showed as "Âµg/L" in the browser because the page never declared UTF-8. Added the charset and viewport tags.

**Interactivity (Ayaan asked for simpler explanations and more buttons)**
- Ran a short design brief (Ayaan chose: any resident first, calm and trustworthy tone; glass meter, year slider, tap-to-explain words). Wrote `PRODUCT.md`.
- Glass meters on each contaminant row that fill toward a dashed line (New York's limit).
- Year slider with "Play the years" that updates every number in place.
- "What do these words mean?" buttons: highest result, limit, ND, ppb, ppt, ppm, 90th percentile, action level.
- Detail pages: plain question headings, a new "Can a home filter help?" section, year buttons under the chart with a one-line readout and report link.
- Compare any two districts instead of only the first two.
- Fixed: 8px gap around the dark bands; lowercase "pfoa" in the summary.

**Address dropdown and map (Ayaan asked for both, pointing to the NY Health Department water systems page)**
- Address box now shows matching addresses with town and ZIP as you type (Photon, an OpenStreetMap search built for type-ahead). Nominatim kept as a backup.
- `tools/boundaries.py` downloads district outlines from EPA's service area map into `data/boundaries.geojson`; `build.py` puts them into the page, so finding your district runs in the browser.
- Leaflet street map with every NY-03 district outlined; your district highlighted with a pin; tap a district to open it.
- Fixed: Leaflet error when the page redrew before the old map was removed; outlines not drawing because Leaflet needs a view first.

**Layout and wording (Ayaan's requests)**
- District page order: name, map, year slider, data, aquifer breakdown. The aquifer section got its own heading and a one-line explanation of each layer.
- Data text made short and technical: "Watch · 78% of limit · peak 10.9 (2022)". Summary reads "Over limit: … Watch: … OK: …".

## Phase 2: More districts

- Found 26 reports for Hicksville, Glen Cove, Port Washington and Manhasset-Lakeville (2019 to 2025) through district websites, their WordPress media libraries, and web search. Port Washington 2021 to 2022 and Manhasset-Lakeville 2020 could not be found anywhere.
- Read every report, verified tricky rows by rendering the page (Manhasset-Lakeville 2023 lead) and reading footnotes (Hicksville 2019).
- Ayaan's decisions: keep Hicksville 2019 PFOS 111.0 as printed with a note about the missing footnote; Glen Cove 2020 lead 3.2 with a note about 3.0 in later reports; keep EPA population counts; leave missing years blank with notes.
- Added all four districts with series, timelines, notes and report links. The checker confirmed every value matches its PDF and learned two more patterns (lead repeated across reports, "Tested for But Not Detected" headings).
- Added "linked to" text for each contaminant (health effects and sources).

**Ranking and map colors (Ayaan's requests)**
- District ranking: "Overall" ranks by each district's worst result that year as a share of its limit (no made-up score; the method is shown), or by one contaminant.
- Map colors every district OK / Watch / Over limit for the chosen year and follows Play. Five districts were over in 2020 (1,4-dioxane), one in 2025 (Glen Cove, PFOA).
- Hovering a contaminant shows what it is linked to.
- Fixed: values just over a limit showed "1.0× limit"; now "101% of limit".

**Look (Ayaan's request)**
- White and dark navy blue; Calibri (Carlito fallback) for most text, Arial for small labels; light theme only. Updated `CLAUDE.md` and `PRODUCT.md`.

## Phase 3: Features

- Shareable links: `#jericho`, `#jericho-dioxane`, `#jericho-filter`, `#jericho-notes`, `#compare`. The address bar follows clicks and Back works. "Copy link" buttons.
- "New report should be out" note when a district's newest report is older than expected after June 1.
- Print summary: hides map and controls, adds questions to ask the district, contact details and full source links.
- Translations (in progress, not yet committed): Spanish, Simplified Chinese and Korean interface text, glossary and contaminant explainers in `data/i18n.json`, machine-translated by Claude and marked for native-speaker review. District notes and timelines stay in English, labeled.

## Questions answered along the way

- Per-well data: annual reports only give district-wide ranges; well locations are withheld for security; homes get blended water. Advised against splitting districts by well. Suggested an optional "by plant" table from deferral reports and EPA UCMR 5 data.

## State at the end of 2026-10-22

- 6 districts with full history (Jericho, Plainview, Hicksville, Glen Cove, Port Washington, Manhasset-Lakeville); 12 more listed with EPA outlines.
- 93 automated tests passing.
- Left: finish translations; Phase 4 (GitHub Pages, test 10 real addresses, accessibility pass); Phase 5 (demo video outline, final AI log check).
