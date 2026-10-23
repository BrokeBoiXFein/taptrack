# TapTrack

Free, year-by-year tap water history for Long Island water districts. Built for the 2026 Congressional App Challenge (NY-03).

**Live site: https://brokeboixfein.github.io/taptrack/**

Every water district publishes a yearly Annual Drinking Water Quality Report as a PDF. TapTrack puts the years side by side so residents can see how 1,4-dioxane, PFAS, nitrate and lead have changed, what the limits are, and what the district is doing about it.

## Files

| Path | What it is |
| --- | --- |
| `data/water.json` | All data: contaminants (limits, plain-language text) and districts (yearly values, timeline, report links, notes) |
| `src/app.html` | The app: layout, styles and code |
| `build.py` | Puts `data/water.json` into `src/app.html` and writes `dist/index.html` |
| `dist/index.html` | The finished single-file app. Open it in a browser or host it anywhere |

## Run it

```
python3 build.py
python3 -m http.server -d dist 8000
```

Then open http://localhost:8000. Add `#jericho` or `#plainview` to the address to open a district directly.

## Host it free on GitHub Pages

1. Push this folder to a GitHub repository.
2. In the repository, open Settings, then Pages. Set the source to the `main` branch and the `/docs` folder. `build.py` writes a copy there.
3. The site appears at `https://<username>.github.io/<repo>/`.

Address search works on a hosted site. It uses OpenStreetMap to find the address and EPA's Community Water System Service Area Boundaries map to find the district. Inside a Claude artifact preview, outside requests are blocked, so use the district picker there.

## Add a district

1. Find the district's PWSID in the `otherDistricts` list in `data/water.json`.
2. Open each year's report from the district's website. For each contaminant, copy the highest value in the table (the "Level Detected" or the top of the range).
3. Add an entry to `districts` with the same shape as Jericho: `series`, `timeline`, `notes`, `reports`, `wells`, `population`. Remove it from `otherDistricts`.
4. Use `0` for a result reported as ND (not detected) in a year it was tested. Leave a year out if the report gives no value.
5. Run `python3 build.py`.

## Data rules

- A yearly value is the highest result the district reported that year, usually from its worst well. Most homes get a blend of wells.
- Units are fixed per contaminant: 1,4-dioxane and lead in µg/L (ppb), PFOA and PFOS in ng/L (ppt), nitrate in mg/L (ppm). Some reports print the wrong unit. Record the problem in `notes`.
- Every value must link back to its report in `reports`.

## Before submitting

- Check every value in `data/water.json` against the linked PDF. The first values were transcribed with AI help and may contain mistakes.
- Disclose AI use in the submission as the 2026 rules require.

## Sources

- District Annual Drinking Water Quality Reports (links in `data/water.json`)
- EPA Community Water System Service Area Boundaries
- New York State Department of Health drinking water standards (PFOA 10 ppt, PFOS 10 ppt, 1,4-dioxane 1 ppb)
- EPA PFAS National Primary Drinking Water Regulation (PFOA and PFOS 4 ppt) and the May 2026 proposal to extend compliance to 2031
