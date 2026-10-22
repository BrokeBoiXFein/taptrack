# AI use log

Required for the 2026 Congressional App Challenge disclosure. Add a line for each session.

| Date | Tool | What AI helped with | What I did myself |
| --- | --- | --- | --- |
| 2026-10-14 to 2026-10-20 | Claude | Researched NY-03 issues and past winners, compared app ideas, reviewed H2OScore | Chose the water quality idea |
| 2026-10-20 | Claude | Transcribed values from Jericho (2018 to 2025) and Plainview (2019 to 2025) reports into data/water.json, drew screen designs, wrote the first version of the app and build script | |
| 2026-10-20 | Claude Code | Phase 1: wrote tools/extract.py (pdfplumber report reader and data check), tests/smoke.test.js (jsdom test of every view), package.json, and a Windows text-encoding fix in build.py | |
| 2026-10-20 | Claude Code | Checked every data/water.json value against its PDF with tools/extract.py; found Plainview PFOA/PFOS ND years, a Jericho 2024 PFOA limit misprint and a Plainview 2017 lead outlier | Reviewed each finding and decided what to change |
| 2026-10-22 | Claude Code | Made the app easier to use: glass meters that fill toward the limit, a year slider with Play, tap-to-explain word buttons, plain-language summaries, year buttons on each chart, and picking any two districts to compare. Wrote PRODUCT.md (design brief) | Asked for simpler explanations and more interactivity, chose which features to build and the calm tone |
