# TapTrack

Free, year-by-year tap water history for Long Island water districts. Entry for the 2026 Congressional App Challenge, New York's 3rd District (Rep. Tom Suozzi). Builder: Ayaan Khandelwal, high school student in Jericho.

## Hard constraints

- **Deadline: Monday, October 26, 2026, 12:00 PM ET.** Plan to submit Sunday night. Submission needs source code, a 2 to 3 minute demo video, app name, target audience, how it works, and the technical challenge.
- **AI disclosure is required.** Keep a running log in `notes/AI_LOG.md` of what Claude did (data extraction, design, code). Ayaan writes all submission text himself.
- **Free, no account, no ads, no affiliate links.** That is the core difference from paid apps like H2OScore ($19.99 to $29.99 a year, everything locked, no sources shown).
- **Every number links to its source.** No black-box score. Show the method.
- **Not medical advice.** Say so on every screen with results.
- **Stay a static site.** No backend, no database, no build tooling that a high schooler can't explain to a judge. Hosted on GitHub Pages from `/docs`.

## What exists now

| Path | What it is |
| --- | --- |
| `data/water.json` | All data. `contaminants` (limits, plain-language text) and `districts` (yearly `series`, `timeline`, `notes`, `reports` links). `otherDistricts` lists NY-03 systems not yet added, with real EPA PWSIDs |
| `src/app.html` | The whole app: tokens, styles, and one vanilla JS IIFE that renders views into `#app` |
| `build.py` | Inserts `data/water.json` into `src/app.html` and writes `dist/index.html` and `docs/index.html` |

Views: home (district summary rows with sparklines), detail (full chart, limits, timeline, explainer, per-year source links), filter (concern checkboxes to filter type), compare (two districts), notes (report errors found).

Run: `python3 build.py && python3 -m http.server -d docs 8000`

## Data rules

- A yearly value is the **highest** result the district reported that year, usually its worst well. Label it that way everywhere.
- Fixed units: 1,4-dioxane and lead in µg/L (ppb). PFOA and PFOS in ng/L (ppt). Nitrate in mg/L (ppm). Reports sometimes print the wrong unit. Record it in the district's `notes`.
- `0` means reported as ND (not detected) in a year it was tested. A missing year means the report gave no value. Never guess or interpolate.
- Limits: New York PFOA 10 ppt, PFOS 10 ppt, 1,4-dioxane 1 ppb, nitrate 10 mg/L. Federal PFOA and PFOS 4 ppt (EPA 2024 rule; May 2026 proposal moves compliance to April 2031 and drops PFHxS, PFNA, GenX limits). Lead action level 15 ppb, dropping to 10 ppb in 2027.
- **Values in `data/water.json` were transcribed with AI help.** Only Jericho 2022 1,4-dioxane (10.9) and Plainview 2019 1,4-dioxane (11.0) have been re-checked. Every other value must be checked against its PDF before submission.

Known report errors (already in `notes`): Jericho 2025 prints PFOA in µg/L, lists a 36.7 mg/L nitrate value with no violation, and Jericho 2024 flags a PFOA violation that the text calls a monitoring violation.

## Data sources

- District Annual Drinking Water Quality Reports (PDFs, links in `data/water.json`). Jericho: jerichowater.org/whats-happening/wqr-archives/ (2012 to 2025). Plainview: plainviewwater.org/news/water-quality-reports/ (2012 to 2025). Hicksville: hicksvillewater.org/hwd/water-quality-report/
- EPA Community Water System Service Area Boundaries, ArcGIS FeatureServer: `https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/Water_System_Boundaries/FeatureServer/0` (fields PWSID, PWS_Name, Population_Served_Count). Address search geocodes with OpenStreetMap Nominatim, then queries this layer by point.
- Future: EPA UCMR 5 (29 PFAS plus lithium, 2023 to 2025), EPA SDWIS violations, lead service line inventories, water rates, NSF certified filter list.

## Design

Mobile-first, one reading column. Display face Bricolage Grotesque, body Atkinson Hyperlegible (chosen for readability, including older residents). Palette tokens in `:root` with light and dark themes: mineral ground, deep groundwater ink, aquifer blue accent, sand and clay strata colors. Status colors: good, watch, over. The signature element is the aquifer cross-section under the district name (Upper glacial, Magothy, Lloyd). Keep it. No emoji, no gradient washes, no single made-up score.

Copy rules: plain words, short sentences, active voice. Name things the way a resident would.

## Working rules for Claude

- Check `data/water.json` against PDFs before adding features that depend on it.
- Keep `src/app.html` readable. If splitting files, keep `build.py` producing one self-contained `docs/index.html`.
- Test every view after a change (a jsdom smoke test lives in `tests/` once added).
- Commit small. Log AI help in `notes/AI_LOG.md` with each commit.
