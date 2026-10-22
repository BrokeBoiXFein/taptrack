"""Build dist/index.html: inserts data/water.json and data/boundaries.geojson into src/app.html."""
import json, pathlib
root = pathlib.Path(__file__).parent
def blob(name):
    data = json.loads((root / "data" / name).read_text(encoding="utf-8"))
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
page = (root / "src/app.html").read_text(encoding="utf-8")
page = page.replace("/*__DATA__*/", blob("water.json")).replace("/*__BOUNDS__*/", blob("boundaries.geojson"))
out = root / "dist/index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page, encoding="utf-8")
(root / "docs").mkdir(exist_ok=True)
(root / "docs/index.html").write_text(page, encoding="utf-8")
print("wrote", out, "and docs/index.html,", out.stat().st_size, "bytes")
