// Renders every page for every district and fails on script errors or broken text. Run: npm test
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM, VirtualConsole } = require("jsdom");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "docs", "index.html"), "utf8");
const data = JSON.parse(fs.readFileSync(path.join(root, "data", "water.json"), "utf8"));
const BAD = /\bundefined\b|\bNaN\b|\[object Object\]/;

function open(hash) {
  const errors = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", (e) => errors.push(e.message));
  vc.on("error", (e) => errors.push(String(e)));
  const dom = new JSDOM(html, {
    url: "http://localhost/" + (hash ? "#" + hash : ""),
    runScripts: "dangerously",
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(w) {
      w.scrollTo = () => {};
      w.addEventListener("error", (e) => errors.push(e.message));
    },
  });
  const w = dom.window;
  const doc = w.document;
  return {
    doc,
    errors,
    click(sel) {
      const el = doc.querySelector(sel);
      assert.ok(el, "missing element " + sel);
      el.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
    },
    choose(value) {
      const sel = doc.getElementById("pick");
      sel.value = value;
      sel.dispatchEvent(new w.Event("change", { bubbles: true }));
    },
    check(where) {
      const text = doc.getElementById("app").textContent;
      assert.deepStrictEqual(errors, [], where + ": script errors");
      assert.ok(text.trim().length > 50, where + ": page is empty");
      const m = text.match(BAD);
      assert.ok(!m, where + ': page text contains "' + (m && m[0]) + '" near: ' + (m && text.slice(Math.max(0, m.index - 60), m.index + 20)));
      for (const a of doc.querySelectorAll("svg[aria-label], button[aria-label]")) {
        const l = a.getAttribute("aria-label");
        assert.ok(!BAD.test(l), where + ": bad aria-label: " + l);
      }
    },
  };
}

test("home with no district", () => {
  const p = open("");
  p.check("home (empty)");
  assert.ok(p.doc.querySelector('[data-go="jericho"]'));
});

test("picking a not-yet-added district shows a message", () => {
  const p = open("");
  const o = data.otherDistricts[0];
  p.choose("pws:" + o.pwsid);
  p.check("home (other district)");
  assert.match(p.doc.getElementById("msg").textContent, /not added yet/);
});

test("address search with an empty box asks for an address", () => {
  const p = open("");
  const form = p.doc.getElementById("find");
  form.dispatchEvent(new p.doc.defaultView.Event("submit", { bubbles: true, cancelable: true }));
  assert.match(p.doc.getElementById("msg").textContent, /Type an address/);
});

test("address lookup finds the right district from the EPA outlines", () => {
  const p = open("");
  const at = p.doc.defaultView.TapTrack.districtAt;
  const cases = [
    [-73.4829973, 40.7847594, "NY2902845"], // 100 Main Pkwy E, Plainview
    [-73.6895363, 40.8303203, "NY2912267"], // 100 Main St, Port Washington
    [-73.5398, 40.792, "NY2902831"], // Jericho Tpke at Route 106
    [-73.5251, 40.7673, "NY2902829"], // Hicksville station
    [-73.6337, 40.8623, "NY2902826"], // Glen Cove City Hall
    [-73.6996, 40.7967, "NY2902836"], // Manhasset station
    [-73.6386561, 40.7420722, null], // 100 Main St, Mineola: its own village system, not in TapTrack
  ];
  for (const [lon, lat, want] of cases) assert.strictEqual(at(lon, lat), want, lon + "," + lat);
});

test("ranking lists every district, follows the year slider and the rate-by chips", () => {
  const p = open("jericho");
  const w = p.doc.defaultView;
  const rows = () => [...p.doc.querySelectorAll("#ranking li")].map((li) => li.textContent);
  assert.strictEqual(rows().length, data.districts.length);
  const yr = p.doc.getElementById("yr");
  for (const rk of [...p.doc.querySelectorAll("[data-rk]")].map((b) => b.dataset.rk)) {
    p.click('[data-rk="' + rk + '"]');
    assert.strictEqual(p.doc.querySelector('[data-rk="' + rk + '"]').getAttribute("aria-pressed"), "true");
    for (let y = +yr.min; y <= +yr.max; y++) {
      yr.value = String(y);
      yr.dispatchEvent(new w.Event("input", { bubbles: true }));
      p.check("ranking " + rk + " " + y);
      assert.strictEqual(rows().length, data.districts.length);
      assert.match(p.doc.getElementById("rank-note").textContent, new RegExp("Ranked for " + y));
    }
  }
});

test("shareable links open the right page, and clicking updates the link", () => {
  for (const d of data.districts) {
    for (const key of Object.keys(data.contaminants)) {
      const p = open(d.id + "-" + key);
      p.check("link " + d.id + "-" + key);
      assert.strictEqual(p.doc.querySelector(".detail h1").textContent, data.contaminants[key].name);
    }
    for (const page of ["filter", "notes", "compare"]) {
      const p = open(d.id + "-" + page);
      p.check("link " + d.id + "-" + page);
      assert.ok(p.doc.querySelector(".detail h1"), page);
    }
  }
  const p = open("jericho");
  p.click('[data-key="nitrate"]');
  assert.strictEqual(p.doc.defaultView.location.hash, "#jericho-nitrate");
  p.click('[data-view="home"]');
  assert.strictEqual(p.doc.defaultView.location.hash, "#jericho");
  const bad = open("not-a-district");
  bad.check("unknown link");
});

test("new report banner: due after June 1, only when the district is behind", () => {
  const p = open("");
  const T = p.doc.defaultView.TapTrack;
  assert.strictEqual(T.expectedYear(new Date(2026, 4, 31)), "2024"); // May 31, 2026: the 2025 report may not be out yet
  assert.strictEqual(T.expectedYear(new Date(2026, 5, 1)), "2025"); // June 1, 2026
  assert.strictEqual(T.dueBanner("jericho", new Date(2026, 9, 22)), ""); // has 2025
  assert.match(T.dueBanner("jericho", new Date(2027, 6, 1)), /The 2026 report should be out/);
});

test("hovering a contaminant explains what it is linked to", () => {
  const p = open("jericho");
  for (const k of Object.keys(data.contaminants)) {
    const tip = p.doc.getElementById("tip-" + k);
    assert.ok(tip && /^Linked to: .+ From: /.test(tip.textContent), k + " tooltip");
    assert.strictEqual(p.doc.querySelector('[data-key="' + k + '"]').getAttribute("aria-describedby"), "tip-" + k);
  }
});

test("address box is an accessible dropdown, and the page works without the map library", () => {
  const p = open("jericho");
  const box = p.doc.getElementById("addr");
  assert.strictEqual(box.getAttribute("role"), "combobox");
  assert.strictEqual(box.getAttribute("aria-controls"), "addr-list");
  box.value = "100 Main";
  box.dispatchEvent(new p.doc.defaultView.Event("input", { bubbles: true }));
  p.check("typing an address");
  assert.match(p.doc.body.textContent, /map could not load/);
});

for (const d of data.districts) {
  test(d.id + ": home", () => {
    const p = open(d.id);
    p.check(d.id + " home");
    assert.ok(p.doc.body.textContent.includes(d.name));
    assert.ok(p.doc.body.textContent.includes("Not medical advice"));
    assert.strictEqual(p.doc.querySelectorAll(".log button").length, 5);
  });

  test(d.id + ": picking from the list opens it", () => {
    const p = open("");
    p.choose(d.id);
    p.check(d.id + " picked");
    assert.ok(p.doc.querySelector(".band h1").textContent.includes(d.name));
  });

  for (const key of Object.keys(data.contaminants)) {
    test(d.id + ": detail " + key, () => {
      const p = open(d.id);
      p.click('[data-key="' + key + '"]');
      p.check(d.id + " detail " + key);
      assert.ok(p.doc.querySelector(".detail h1"));
      assert.ok(p.doc.body.textContent.includes("Not medical advice"));
      p.click('[data-view="home"]');
      p.check(d.id + " back from " + key);
    });
  }

  test(d.id + ": filter, every concern on and off", () => {
    const p = open(d.id);
    p.click('[data-view="filter"]');
    p.check(d.id + " filter");
    for (const id of ["pfas", "nitrate", "baby", "lead", "dioxane"]) {
      for (const on of [true, false, true]) {
        const box = p.doc.querySelector('[data-concern="' + id + '"]');
        box.checked = on;
        box.dispatchEvent(new p.doc.defaultView.Event("change", { bubbles: true }));
        p.check(d.id + " filter " + id + "=" + on);
      }
    }
    assert.ok(p.doc.body.textContent.includes("Not medical advice"));
  });

  test(d.id + ": compare, every tab", () => {
    const p = open(d.id);
    p.click('[data-view="compare"]');
    p.check(d.id + " compare");
    for (const b of [...p.doc.querySelectorAll("[data-ck]")].map((x) => x.dataset.ck)) {
      p.click('[data-ck="' + b + '"]');
      p.check(d.id + " compare " + b);
    }
  });

  test(d.id + ": year slider, every year", () => {
    const p = open(d.id);
    const w = p.doc.defaultView;
    const yr = p.doc.getElementById("yr");
    assert.ok(yr, "slider missing");
    for (let y = +yr.min; y <= +yr.max; y++) {
      yr.value = String(y);
      yr.dispatchEvent(new w.Event("input", { bubbles: true }));
      p.check(d.id + " year " + y);
      assert.strictEqual(p.doc.getElementById("yr-out").textContent, String(y));
      assert.strictEqual(p.doc.querySelectorAll(".log .fill").length, 5);
      for (const f of p.doc.querySelectorAll(".log .fill")) assert.match(f.style.transform, /^scaleY\(\d(\.\d+)?\)$/, d.id + " " + y + " bad fill");
    }
    p.click("[data-play]");
    assert.strictEqual(p.doc.querySelector("[data-play]").getAttribute("aria-pressed"), "true");
    p.click("[data-play]");
    assert.strictEqual(p.doc.querySelector("[data-play]").getAttribute("aria-pressed"), "false");
  });

  test(d.id + ": word buttons open and close", () => {
    const p = open(d.id);
    for (const t of [...p.doc.querySelectorAll(".term")].map((x) => x.dataset.term)) {
      p.click('.term[data-term="' + t + '"]');
      const def = p.doc.getElementById("def");
      assert.ok(!def.hidden && def.textContent.length > 20, t + " did not open");
      p.check(d.id + " term " + t);
      p.click('.term[data-term="' + t + '"]');
      assert.ok(def.hidden, t + " did not close");
    }
  });

  test(d.id + ": detail year buttons", () => {
    const p = open(d.id);
    for (const key of Object.keys(data.contaminants)) {
      p.click('[data-key="' + key + '"]');
      for (const y of [...p.doc.querySelectorAll("button[data-py]")].map((x) => x.dataset.py)) {
        p.click('button[data-py="' + y + '"]');
        p.check(d.id + " " + key + " year " + y);
        assert.match(p.doc.querySelector(".readout").textContent, new RegExp("^" + y + ":"));
      }
      p.click('[data-view="home"]');
    }
  });

  test(d.id + ": compare any two districts", () => {
    const p = open(d.id);
    p.click('[data-view="compare"]');
    for (const other of data.districts) {
      const s = p.doc.querySelector('[data-cmp="B"]');
      s.value = other.id;
      s.dispatchEvent(new p.doc.defaultView.Event("change", { bubbles: true }));
      p.check(d.id + " compare with " + other.id);
      const ths = [...p.doc.querySelectorAll("th")].map((x) => x.textContent);
      assert.notStrictEqual(ths[1], ths[2], "compared a district with itself");
    }
  });

  test(d.id + ": report errors page", () => {
    const p = open(d.id);
    p.click('[data-view="notes"]');
    p.check(d.id + " notes");
    assert.strictEqual(p.doc.querySelectorAll(".notes li").length, d.notes.length);
  });
}
