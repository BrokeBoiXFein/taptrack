"""Download district outlines from EPA's service area map into data/boundaries.geojson.

  python tools/boundaries.py
"""
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAYER = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/Water_System_Boundaries/FeatureServer/0/query"

data = json.loads((ROOT / "data" / "water.json").read_text(encoding="utf-8"))
ids = [d["pwsid"] for d in data["districts"] + data["otherDistricts"]]
query = urllib.parse.urlencode({
    "f": "geojson",
    "where": "PWSID IN (" + ",".join("'" + i + "'" for i in ids) + ")",
    "outFields": "PWSID,PWS_Name",
    "outSR": 4326,
    "geometryPrecision": 5,
    "maxAllowableOffset": 0.0002,
})
with urllib.request.urlopen(LAYER + "?" + query, timeout=90) as r:
    gj = json.load(r)

found = {f["properties"]["PWSID"] for f in gj["features"]}
for f in gj["features"]:
    f["properties"] = {"pwsid": f["properties"]["PWSID"]}
gj["features"].sort(key=lambda f: f["properties"]["pwsid"])
gj = {"type": "FeatureCollection", "source": "EPA Community Water System Service Area Boundaries", "features": gj["features"]}
out = ROOT / "data" / "boundaries.geojson"
out.write_text(json.dumps(gj, separators=(",", ":")), encoding="utf-8")
print(f"wrote {out}, {len(found)} of {len(ids)} districts, {out.stat().st_size} bytes")
missing = [i for i in ids if i not in found]
if missing:
    print("no boundary from EPA for:", ", ".join(missing))
