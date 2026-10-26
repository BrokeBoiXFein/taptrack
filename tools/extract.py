"""Read contaminant rows from a water district report PDF.

  python tools/extract.py <pdf url or path>    show the rows found
  python tools/extract.py --check              compare data/water.json to every report
  python tools/extract.py --check --district jericho --year 2024
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys
import urllib.request

import pdfplumber

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / ".cache"

NAMES = {
    "dioxane": r"1\s*,\s*4\s*-?\s*dioxane",
    "pfoa": r"\bPFOA\b|perfluoro-?\s*octanoic",
    "pfos": r"\bPFOS\b|perfluoro-?\s*octane\s*sulfon",
    "nitrate": r"\bnitrate",
    "lead": r"\blead\b",
}
EXPECTED_UNIT = {"dioxane": "ug/l", "pfoa": "ng/l", "pfos": "ng/l", "nitrate": "mg/l", "lead": "ug/l"}
UNIT_RE = re.compile(r"(µg/l|μg/l|ug/l|ng/l|mg/l|ppb|ppt|ppm)", re.I)
UNIT_NORM = {"µg/l": "ug/l", "μg/l": "ug/l", "ug/l": "ug/l", "ppb": "ug/l", "ng/l": "ng/l", "ppt": "ng/l", "mg/l": "mg/l", "ppm": "mg/l"}
MONTHS = r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
DATE_RE = re.compile(
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"            # 3/14/22
    r"|\b\d{1,2}/\d{4}\b"                       # 3/2022
    r"|\b(?:" + MONTHS + r")\.?\s*\d{0,2},?\s*(?:20\d\d)?\b"  # March 2022
    r"|\b20[0-3]\d\s*[-–]\s*20[0-3]\d\b"       # 2021-2022
    r"|\b20[0-3]\d\b"                           # 2022
    r"|\bquarterly\b|\bmonthly\b|\bannual(?:ly)?\b",
    re.I,
)
NUM_RE = re.compile(r"(?<![A-Za-z\d.])(\d+(?:\.\d+)?)")
ND_RE = re.compile(r"\bN\.?D\.?\b|non-?detect|not detected", re.I)
# Heading of a "tested but not detected" list
ND_LIST_RE = re.compile(r"contaminants\s+(?:which|that)\s+(?:have\s+been|were)\s+(?:undetected|not\s+detected)|tested\s+for\s+but\s+not\s+detected", re.I)


def fetch(src):
    """Download a URL once into tools/.cache, or return a local path."""
    if not re.match(r"https?://", src):
        return pathlib.Path(src)
    CACHE.mkdir(parents=True, exist_ok=True)
    name = hashlib.sha1(src.encode()).hexdigest()[:12] + "_" + src.rsplit("/", 1)[-1]
    path = CACHE / name
    if not path.exists():
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 (TapTrack report checker)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            path.write_bytes(r.read())
    return path


def lines_of(path):
    """Every text line and table row in the PDF."""
    out = []
    with pdfplumber.open(path) as pdf:
        for n, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            raw = [l.strip() for l in text.splitlines() if l.strip()]
            nd_page = bool(ND_LIST_RE.search(re.sub(r"\s+", " ", text)))
            for i, l in enumerate(raw):
                out.append({"page": n, "text": l, "next": raw[i + 1: i + 3], "nd_page": nd_page})
            for table in page.extract_tables() or []:
                for row in table:
                    cells = [re.sub(r"\s+", " ", c or "").strip() for c in row]
                    if any(cells):
                        out.append({"page": n, "text": " | ".join(cells), "next": [], "table": True})
    return out


def parse(key, line):
    text = line["text"]
    body = re.sub(NAMES[key], " ", text, flags=re.I)
    # Some tables put the numbers on the next line
    if not NUM_RE.search(DATE_RE.sub(" ", body)) and line["next"]:
        body += " " + " ".join(line["next"])
    dates = [d.strip() for d in DATE_RE.findall(body) if d.strip()]
    rest = DATE_RE.sub(" ", body)
    units = sorted({UNIT_NORM[u.lower()] for u in UNIT_RE.findall(rest)})
    rest = UNIT_RE.sub(" ", rest)
    nums = [float(n) for n in NUM_RE.findall(rest)]
    return {"page": line["page"], "text": text, "nums": nums, "units": units, "dates": dates,
            "nd": bool(ND_RE.search(body)), "table": line.get("table", False)}


def is_row(key, p):
    if not (p["nums"] or p["nd"]):
        return False
    if key == "lead":
        # "lead" appears in a lot of plain text, so require a unit or "90th"
        return bool(p["units"]) or bool(re.search(r"90", p["text"]))
    return len(p["text"]) < 220 or p["table"]


def extract(src):
    lines = lines_of(fetch(src))
    found = {k: [] for k in NAMES}
    nd_list = {k: False for k in NAMES}
    for line in lines:
        for key, pat in NAMES.items():
            if re.search(pat, line["text"], re.I):
                if line.get("nd_page") and not UNIT_RE.search(line["text"]) and not re.search(r"\d\.\d", line["text"]):
                    nd_list[key] = True
                p = parse(key, line)
                if is_row(key, p):
                    found[key].append(p)
    return found, nd_list, len(lines)


def show(src):
    found, nd_list, n = extract(src)
    print(src)
    if not n:
        print("  No text layer. The PDF may be a scan; check it by hand.")
        return
    for key, rows in found.items():
        print(f"\n  {key.upper()}  ({len(rows)} rows)" + ("  listed as tested, not detected" if nd_list[key] else ""))
        for p in rows:
            unit = ",".join(p["units"]) or "-"
            flag = "  <-- unit differs" if p["units"] and EXPECTED_UNIT[key] not in p["units"] else ""
            print(f"    p{p['page']:<3} nums={fmtnums(p['nums'])} nd={'Y' if p['nd'] else '-'} unit={unit} dates={p['dates'][:3]}{flag}")
            print(f"         {p['text'][:150]}")


def fmtnums(nums):
    return "[" + ", ".join(f"{x:g}" for x in nums) + "]"


def check(district_id=None, year=None):
    data = json.loads((ROOT / "data" / "water.json").read_text(encoding="utf-8"))
    rows, problems = [], []
    for d in data["districts"]:
        if district_id and d["id"] != district_id:
            continue
        for y, url in sorted(d["reports"].items()):
            if year and y != str(year):
                continue
            try:
                found, nd_list, n = extract(url)
            except Exception as e:
                problems.append(f"{d['id']} {y}: could not read report ({e}). {url}")
                continue
            if not n:
                problems.append(f"{d['id']} {y}: no text layer, check by hand. {url}")
                continue
            for key in NAMES:
                have = d["series"].get(key, {}).get(y)
                hits = found[key]
                nums = sorted({x for p in hits for x in p["nums"]})
                units = sorted({u for p in hits for u in p["units"]})
                lead_seen = key == "lead" and any(abs(x - v) < 1e-9 for x in nums for v in d["series"].get("lead", {}).values())
                if have is None and lead_seen:
                    status = "-"  # lead is filed under its sampling year
                elif have is None:
                    status = "listed ND, JSON blank" if nd_list[key] and key != "lead" else ("report has rows, JSON blank" if nums else "-")
                elif have == 0:
                    status = ("match (ND)" if any(p["nd"] for p in hits) else "match (ND list)" if nd_list[key]
                              else "NOT FOUND" if not hits else "MISMATCH")
                else:
                    status = "match" if any(abs(x - have) < 1e-9 for x in nums) else ("NOT FOUND" if not hits else "MISMATCH")
                unit_flag = bool(units) and EXPECTED_UNIT[key] not in units
                rows.append((d["id"], y, key, have, nums, units, status, unit_flag))
                if status not in ("match", "match (ND)", "match (ND list)", "-") or unit_flag:
                    pages = sorted({p["page"] for p in hits})
                    why = status + ("; unit printed as " + ",".join(units) if unit_flag else "")
                    problems.append(f"{d['id']} {y} {key}: JSON={have} report numbers={fmtnums(nums[:12])} pages={pages} -> {why}. {url}")

    print(f"{'district':<10} {'year':<5} {'contam':<8} {'json':>7}  {'status':<28} report numbers")
    for did, y, key, have, nums, units, status, uf in rows:
        h = "-" if have is None else f"{have:g}"
        print(f"{did:<10} {y:<5} {key:<8} {h:>7}  {status + (' (unit)' if uf else ''):<28} {fmtnums(nums[:10])} {','.join(units)}")
    print(f"\n{len(problems)} items to check by hand:")
    for p in problems:
        print("  - " + p)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?", help="report PDF URL or path")
    ap.add_argument("--check", action="store_true", help="compare data/water.json against every report")
    ap.add_argument("--district")
    ap.add_argument("--year")
    a = ap.parse_args()
    if a.check:
        check(a.district, a.year)
    elif a.src:
        show(a.src)
    else:
        ap.print_help()
