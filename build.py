"""Build dist/index.html: inserts data/water.json into src/app.html."""
import json, pathlib
root = pathlib.Path(__file__).parent
data = json.loads((root / "data/water.json").read_text())
page = (root / "src/app.html").read_text()
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
out = root / "dist/index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page.replace("/*__DATA__*/", blob))
(root / "docs").mkdir(exist_ok=True)
(root / "docs/index.html").write_text(out.read_text())
print("wrote", out, "and docs/index.html,", out.stat().st_size, "bytes")
