# TapTrack

Free, year-by-year tap water history for Long Island water districts. Built for the 2026 Congressional App Challenge (NY-03).

**Live site: https://brokeboixfein.github.io/taptrack/**

Every water district publishes a yearly Annual Drinking Water Quality Report as a PDF. TapTrack puts the years side by side so residents can see how 1,4-dioxane, PFAS, nitrate and lead have changed, what the limits are, and what the district is doing about it. No account, no ads, and every number links to the report it came from.

## What's in the app

- **Find your district.** Type an address and pick it from the list (each match shows its town and ZIP), or choose a district from the menu.
- **District page.** A map of NY-03 districts colored by rating, a year slider, then one row per contaminant with a glass meter, the value, and a short status like `Watch · 78% of limit · peak 10.9 (2022)`. The bottom section explains the aquifers the district's wells draw from.
- **Contaminant page.** A chart of every year with the New York and EPA limits drawn in, year buttons that read out a value and link its report, what the district did about it, and plain answers to "What is it?", "Should I worry?" and "Can a home filter help?".
- **Ranking.** Districts ranked best to worst for the chosen year, overall or by one contaminant.
- **Compare, filter guide, report errors.** Compare any two districts, find the right type of home filter, and see mistakes found in the districts' own reports.
- **Print and share.** Print a one-page summary to bring to a district meeting, or copy a link straight to any page.

## Districts

Full history (2019 to 2025, Jericho from 2018): Jericho, Plainview, Hicksville, Glen Cove, Port Washington, Manhasset-Lakeville. The other 12 NY-03 districts appear on the map in gray and are listed as coming next.

## How it works

TapTrack is a static website: one HTML file with no server and no database. That keeps it free to host and easy to check.

### Files

| Path | What it is |
| --- | --- |
| `data/water.json` | All the water data: contaminants (limits, explanations) and districts (yearly values, report links, timeline, notes) |
| `data/boundaries.geojson` | District outlines from EPA, used for the map and the address lookup |
| `src/app.html` | The app: styles and one JavaScript file that draws every page |
| `build.py` | Puts both data files into `src/app.html` and writes `docs/index.html` (the live site) and `dist/index.html` |
| `tools/extract.py` | Reads report PDFs and checks every value in `data/water.json` against them |
| `tools/boundaries.py` | Downloads district outlines from EPA |
| `tests/smoke.test.js` | Opens every page for every district in a simulated browser and fails on any error |
| `notes/` | AI use log and work log for the Challenge disclosure |

### The data

Each district in `data/water.json` has a `series` of yearly values for each contaminant, plus `reports` (the PDF link for each year), `timeline`, `notes`, `wells` and `population`.

Rules for every value:

- A yearly value is the **highest** result the district reported that year, usually from its worst well. Most homes get water blended from several wells, so most taps are lower. The app says this on every results page.
- Units are fixed: 1,4-dioxane and lead in µg/L (ppb), PFOA and PFOS in ng/L (ppt), nitrate in mg/L (ppm).
- `0` means the report lists it as not detected (ND). A missing year means the report gave no value. Nothing is guessed or filled in.
- Lead is tested at home taps every three years, so lead values are filed under the year they were sampled.
- Limits: New York PFOA 10 ppt, PFOS 10 ppt, 1,4-dioxane 1 ppb, nitrate 10 mg/L. EPA PFOA and PFOS 4 ppt. Lead action level 15 ppb (10 from 2027).

### How a value becomes a status

For each contaminant the app takes the latest value and compares it to New York's limit:

- **Over limit** if it's above the limit.
- **Watch** if it's at least half the limit, or above EPA's lower limit for PFAS. Nitrate at half the limit also gets an infant warning, the same rule the reports follow.
- **OK** otherwise.
- **Not listed** if the contaminant stopped appearing in newer reports, which usually means it wasn't detected.

For lead, the value is the 90th percentile of home tap tests. It's compared to the action level of 15.

The status line shows the value as a share of the limit ("78% of limit", or "4.9× limit" when it's twice the limit or more) and the peak year if the value was ever over the limit. The glass meter shows the same share: it fills toward a dashed line at the limit.

### Year slider

Moving the slider rebuilds the district as it looked in that year by keeping only the values and reports up to that year. Then the same status rules run again, so every row, the summary line, the ranking and the map colors change together. "Play the years" steps through each year automatically.

### Ranking and map colors

For one contaminant, districts are ranked by their result as a share of the limit, lowest first. For "Overall", each district is ranked by its worst result that year, whichever contaminant is closest to (or furthest over) its limit. There's no made-up score, and the ranking always shows which result put a district where it is.

The map colors each district by that same rating: green OK, amber Watch, red Over limit. Districts not in TapTrack yet are dashed gray.

### Address search

1. As you type, the app asks **Photon**, a free OpenStreetMap address search, for matching addresses inside the NY-03 area and lists them with town and ZIP, so two "Main Streets" in different towns are easy to tell apart.
2. When you pick one, the app gets its map coordinates and checks which district outline it falls inside (a point-in-polygon test against `data/boundaries.geojson`). This step runs in your browser. The only service that sees what you type is Photon, which needs it to suggest addresses.
3. If the point isn't in any NY-03 district, the app asks EPA's boundary map for the name of the water system that serves it.

If Photon is down, the app falls back to OpenStreetMap's Nominatim search.

### Links, print and the new-report note

- The address bar follows what you're looking at: `#jericho`, `#jericho-dioxane`, `#jericho-filter`, `#jericho-notes`, `#compare`. You can share any page, and the browser's Back button works.
- Printing hides the map and buttons and adds the report errors to ask the district about, its phone number and the full link to every source.
- A district's report for a year is due by June 1 of the next year. If the newest report in TapTrack is older than that, the district page says the new one should be out and links to the district's reports page.

### Checking the data against the PDFs

`tools/extract.py --check` downloads every report linked in `data/water.json`, pulls out each row that names a contaminant, and checks that the value in the data appears on that row. It also recognizes "tested but not detected" lists and flags rows printed in the wrong unit. It never changes the data. It prints a list to check by hand. Every value in the app has been checked this way and by reading the PDF.

## Run it

Needs Python 3. For the tests, also Node.js.

```
python build.py
python -m http.server 8000 -d docs
```

Then open http://localhost:8000.

```
pip install pdfplumber
python tools/extract.py --check
npm install
npm test
```

## Add a district

1. Find the district in `otherDistricts` in `data/water.json` (it has the EPA ID, called a PWSID).
2. For each year's report, copy the highest value for each contaminant (the top of the range, or "level detected").
3. Add an entry to `districts` shaped like the others, with `reports` linking each year's PDF, and remove it from `otherDistricts`.
4. Run `python tools/extract.py --check --district <id>` and fix anything it flags.
5. Run `python build.py` and `npm test`.

## Hosting

GitHub Pages serves the `docs` folder from the `main` branch. `build.py` writes `docs/index.html`, so pushing a new build updates the live site.

## Sources

- District Annual Drinking Water Quality Reports (each one linked in the app and in `data/water.json`)
- EPA Community Water System Service Area Boundaries
- New York State Department of Health drinking water standards
- EPA PFAS National Primary Drinking Water Regulation (2024) and the May 2026 proposal to extend compliance to 2031
- OpenStreetMap (street map) and Photon by komoot (address search)

Not medical advice.

## AI use

Built with help from Claude (Anthropic), as the Challenge rules require us to disclose. See `notes/AI_LOG.md` for what AI helped with and `notes/WORK_LOG.md` for the full record.
