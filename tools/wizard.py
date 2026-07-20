#!/usr/bin/env python3
"""PURE wizard generator — compile the class files into a web form.

Usage:
    python3 tools/wizard.py [--out docs/index.html] [--pure v0.1.1]

Reads classes/**/*.md and emits one self-contained HTML page: a guided
form whose dropdown cascade IS the taxonomy tree and whose inputs ARE
the class-file field tables and questions. The form is never edited by
hand — change a class file, rerun this, and the form follows the spec.

The generated page: paste an article, walk the questions, and it builds
a canonical PURE report in the browser (claims sorted, RFC 8785-style
canonical JSON, SHA-256 report id, event key) with live verification
that every quote is a verbatim substring of the pasted source.
"""
import argparse
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_table(lines, start):
    """Parse a markdown table starting at index `start`; return (rows, next_i)."""
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip().strip("`") for c in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))]
        if cells and cells[0].lower() not in ("field", "name") and not set(cells[0]) <= {"-", " ", ":"}:
            rows.append([c.replace("\\|", "|") for c in cells])
        i += 1
    return rows, i


def parse_class_file(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    fields, guidance, questions = [], [], {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"##.*Fields \(normative\)", line):
            while i < len(lines) and not lines[i].strip().startswith("|"):
                i += 1
            rows, i = parse_table(lines, i)
            fields = [{"name": r[0], "type": r[1] if len(r) > 1 else "",
                       "rule": r[2] if len(r) > 2 else ""} for r in rows]
            continue
        if re.match(r"##.*Reserved facet names", line):
            while i < len(lines) and not lines[i].strip().startswith("|"):
                i += 1
            rows, i = parse_table(lines, i)
            guidance = [{"name": r[0], "meaning": r[1] if len(r) > 1 else ""} for r in rows]
            continue
        m = re.match(r"- \*\*([\w.:]+)\*\* — (.+)", line)
        if m:
            questions[m.group(1)] = m.group(2)
        i += 1
    for f in fields:
        f["question"] = questions.get(f["name"], "")
    return fields, guidance


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "index.html"))
    ap.add_argument("--pure", default="v0.1.1")
    args = ap.parse_args()

    data = {"pure": args.pure, "classes": {}, "common": {"fields": [], "guidance": []}}
    for path in sorted(glob.glob(os.path.join(ROOT, "classes", "**", "*.md"), recursive=True)):
        rel = os.path.relpath(path, os.path.join(ROOT, "classes"))
        class_id = rel[:-3].replace(os.sep, ".")
        fields, guidance = parse_class_file(path)
        if class_id == "common":
            data["common"] = {"fields": fields, "guidance": guidance}
        else:
            data["classes"][class_id] = {"fields": fields}

    html = TEMPLATE.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    open(args.out, "w", encoding="utf-8").write(html)
    n = len(data["classes"])
    print(f"wrote {args.out}: {n} class(es), {sum(len(c['fields']) for c in data['classes'].values())} class fields, "
          f"{len(data['common']['fields'])} common fields, {len(data['common']['guidance'])} guidance facets")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PURE encoder</title>
<style>
:root { --bg:#fff; --fg:#1a1a1a; --mut:#666; --line:#ddd; --ok:#0a7a33; --bad:#b3261e; --accent:#0b57d0; --card:#f7f7f8; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#111; --fg:#eee; --mut:#9a9a9a; --line:#333; --ok:#5dd48a; --bad:#ff8a80; --accent:#8ab4f8; --card:#1c1c1e; }
}
* { box-sizing:border-box }
body { margin:0 auto; max-width:860px; padding:2rem 1rem 6rem; font:15px/1.5 system-ui,sans-serif; background:var(--bg); color:var(--fg) }
h1 { font-size:1.5rem; margin:.2rem 0 } h2 { font-size:1.05rem; margin:2rem 0 .6rem; border-bottom:1px solid var(--line); padding-bottom:.3rem }
.sub { color:var(--mut); margin:0 0 1.2rem }
label { display:block; font-weight:600; margin:.8rem 0 .2rem }
.q { font-weight:400; color:var(--mut); font-size:.85rem; margin:-.1rem 0 .3rem }
input, select, textarea { width:100%; padding:.45rem .6rem; font:inherit; color:var(--fg); background:var(--bg); border:1px solid var(--line); border-radius:6px }
textarea { min-height:70px } #src { min-height:180px; font-family:ui-monospace,monospace; font-size:.85rem }
.row { display:flex; gap:.6rem; flex-wrap:wrap } .row > div { flex:1; min-width:140px }
.claimcard { background:var(--card); border:1px solid var(--line); border-radius:10px; padding: .8rem 1rem 1rem; margin:.8rem 0 }
.qcheck { font-size:.8rem; margin-top:.25rem } .ok { color:var(--ok) } .bad { color:var(--bad) }
button { padding:.55rem 1.1rem; font:inherit; font-weight:600; border-radius:8px; border:1px solid var(--line); background:var(--card); color:var(--fg); cursor:pointer }
button.primary { background:var(--accent); border-color:var(--accent); color:#fff }
pre { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:1rem; overflow-x:auto; font-size:.8rem }
.pill { display:inline-block; font-size:.75rem; padding:.1rem .5rem; border:1px solid var(--line); border-radius:99px; color:var(--mut); margin-left:.4rem }
.err { color:var(--bad); font-weight:600 }
details { margin:.6rem 0 } summary { cursor:pointer; font-weight:600 }
</style>
</head>
<body>
<h1>PURE encoder <span class="pill" id="rev"></span></h1>
<p class="sub">The form below is compiled from the class files in the spec repo — the dropdowns are the taxonomy, the questions are the spec. Rule of the game: <b>no quote, no claim</b> — every value must cite the exact words in the source.</p>

<h2>1 · What kind of event?</h2>
<div class="row" id="cascade"></div>

<div id="rest" style="display:none">
<h2>2 · The source</h2>
<label>Source URL</label><input id="url" placeholder="https://…">
<label>Paste the source text <span class="q">quotes are verified against exactly these bytes</span></label>
<textarea id="src" placeholder="Paste the article / report text here…"></textarea>

<h2>3 · The event</h2>
<div class="claimcard">
  <label>Quote establishing the event type <span class="pill">what · required</span></label>
  <div class="q">The sentence in the source that shows what kind of event this is.</div>
  <textarea id="what_q"></textarea><div class="qcheck" id="what_qc"></div>
  <label>When did it happen? <span class="pill">when · required</span></label>
  <div class="q">Event start. Date only if that's all the source states; keep local offset if a time is stated (e.g. 2026-06-17T19:56-05:00).</div>
  <input id="when" placeholder="YYYY-MM-DD or full ISO instant">
  <label>Quote for when</label><textarea data-qfor="when" id="when_q"></textarea><div class="qcheck" id="when_qc"></div>
  <label>Where? <span class="pill">where · required</span></label>
  <div class="q">One locus ID: geo:&lt;geohash&gt; / gn: / wd: when resolvable, else the source's place phrase verbatim. This feeds the event key.</div>
  <input id="where" placeholder="geo:dnbygq  ·  or  ·  Coastal City, Region X, Country Y">
  <label>Quote for where</label><textarea id="where_q"></textarea><div class="qcheck" id="where_qc"></div>
</div>

<h2>4 · Location detail <span class="pill">optional facets — only what the source states</span></h2>
<div id="locfields"></div>
<details><summary>More location facets (venue, address, region…)</summary><div id="locguid"></div></details>

<h2>5 · The facts</h2>
<div id="classfields"></div>

<h2>6 · Statements <span class="pill">said — what someone asserted, opinion or claim</span></h2>
<div id="saids"></div>
<button onclick="addSaid()">+ add statement</button>

<h2>7 · Derivation <span class="pill">via — only if this source credits another work</span></h2>
<div class="claimcard">
  <label>Derived from (URL or name)</label><input id="via">
  <label>Quote (e.g. “according to …”)</label><textarea id="via_q"></textarea><div class="qcheck" id="via_qc"></div>
</div>

<h2>8 · Seal</h2>
<button class="primary" onclick="build()">Build canonical report</button>
<div id="problems"></div>
<pre id="out" style="display:none"></pre>
<button id="dl" style="display:none" onclick="download()">Download report.json</button>
</div>

<script>
const DATA = /*__DATA__*/null;
document.getElementById('rev').textContent = DATA.pure;
const $ = id => document.getElementById(id);
let currentClass = null, sealed = null;

// ---- taxonomy cascade ----
function renderCascade(prefix) {
  const box = $('cascade');
  // remove selects deeper than prefix
  while (box.children.length > prefix.split('.').filter(Boolean).length) box.removeChild(box.lastChild);
  const ids = Object.keys(DATA.classes);
  const depth = prefix ? prefix.split('.').length : 0;
  const opts = [...new Set(ids.filter(id => id.startsWith(prefix)).map(id => id.split('.')[depth]).filter(Boolean))];
  if (!opts.length) return;
  const wrap = document.createElement('div');
  const sel = document.createElement('select');
  sel.innerHTML = '<option value="">— select —</option>' + opts.map(o => `<option>${o}</option>`).join('');
  sel.onchange = () => {
    const p = prefix ? prefix + '.' + sel.value : sel.value;
    if (DATA.classes[p]) { currentClass = p; renderForm(); }
    else { currentClass = null; $('rest').style.display = 'none'; }
    if (sel.value) renderCascade(p);
  };
  wrap.appendChild(sel); box.appendChild(wrap);
}

function fieldCard(f, idprefix) {
  const isEnum = f.type.startsWith('enum(');
  const opts = isEnum ? f.type.slice(5, -1).split('|') : [];
  const valInput = isEnum
    ? `<select id="${idprefix}_v"><option value="">—</option>${opts.map(o=>`<option>${o}</option>`).join('')}</select>`
    : f.type === 'bool'
    ? `<select id="${idprefix}_v"><option value="">—</option><option>true</option><option>false</option></select>`
    : `<input id="${idprefix}_v" placeholder="${f.type==='count'||f.type==='number'?'number':'value'}">`;
  return `<div class="claimcard">
    <label>${f.name} <span class="pill">${f.type}</span></label>
    ${f.question ? `<div class="q">${f.question}</div>` : f.rule ? `<div class="q">${f.rule}</div>` : ''}
    <div class="row">
      <div><label>Answer</label>
        <select id="${idprefix}_mode" onchange="modeChange('${idprefix}')">
          <option value="absent">not mentioned by the source</option>
          <option value="value">stated value</option>
          ${f.type==='count'?'<option value="min">at least N (“at least 12”)</option>':''}
          <option value="null">raised, but no value stated</option>
        </select></div>
      <div id="${idprefix}_vwrap" style="display:none"><label>Value</label>${valInput}</div>
    </div>
    <div id="${idprefix}_more" style="display:none">
      <label>Quote (verbatim from source) <span class="pill">required</span></label>
      <textarea id="${idprefix}_q" oninput="qcheck('${idprefix}')"></textarea>
      <div class="qcheck" id="${idprefix}_qc"></div>
      <div class="row"><div><label>Attributed to (by) <span class="pill">optional</span></label><input id="${idprefix}_by"></div>
      <div><label>As of (t) <span class="pill">optional</span></label><input id="${idprefix}_t" placeholder="ISO date/time"></div></div>
    </div>
  </div>`;
}

function modeChange(p) {
  const m = $(p + '_mode').value;
  $(p + '_vwrap').style.display = (m === 'value' || m === 'min') ? '' : 'none';
  $(p + '_more').style.display = m === 'absent' ? 'none' : '';
}
function qcheck(p) {
  const q = $(p + '_q').value, src = $('src').value, el = $(p + '_qc');
  if (!q) { el.textContent = ''; return; }
  const hit = src.includes(q);
  el.textContent = hit ? '✓ verbatim quote found in source' : '✗ NOT found verbatim in the pasted source';
  el.className = 'qcheck ' + (hit ? 'ok' : 'bad');
}
document.addEventListener('input', e => { if (e.target.id === 'src') refreshQChecks(); });
function refreshQChecks() {
  document.querySelectorAll('[id$="_q"]').forEach(t => { const p = t.id.slice(0, -2); if ($(p + '_qc')) qcheck(p); });
  ['what','when','where','via'].forEach(k => simpleQ(k));
}
function simpleQ(k) {
  const q = $(k + '_q').value, el = $(k + '_qc'); if (!el) return;
  if (!q) { el.textContent=''; return; }
  const hit = $('src').value.includes(q);
  el.textContent = hit ? '✓ found in source' : '✗ not found verbatim';
  el.className = 'qcheck ' + (hit ? 'ok' : 'bad');
}
['what','when','where','via'].forEach(k => document.addEventListener('input', e => { if (e.target.id === k + '_q') simpleQ(k); }));

let fieldRegistry = [];
function renderForm() {
  $('rest').style.display = '';
  fieldRegistry = [];
  const cf = $('classfields'); cf.innerHTML = '';
  DATA.classes[currentClass].fields.forEach((f, i) => {
    const p = 'f' + i; fieldRegistry.push({p, f, ext: false});
    cf.insertAdjacentHTML('beforeend', fieldCard(f, p));
  });
  const lf = $('locfields'); lf.innerHTML = '';
  DATA.common.fields.forEach((f, i) => {
    const p = 'c' + i; fieldRegistry.push({p, f, ext: false});
    lf.insertAdjacentHTML('beforeend', fieldCard(f, p));
  });
  const lg = $('locguid'); lg.innerHTML = '';
  DATA.common.guidance.forEach((g, i) => {
    const p = 'g' + i; const f = {name: g.name, type: 'string', rule: g.meaning, question: g.meaning};
    fieldRegistry.push({p, f, ext: true});
    lg.insertAdjacentHTML('beforeend', fieldCard(f, p));
  });
}

let saidCount = 0;
function addSaid() {
  const p = 's' + saidCount++;
  $('saids').insertAdjacentHTML('beforeend', `<div class="claimcard">
    <label>Statement (what they said, as content)</label><textarea id="${p}_v"></textarea>
    <div class="row"><div><label>By (required)</label><input id="${p}_by"></div></div>
    <label>Quote (verbatim from source)</label><textarea id="${p}_q" oninput="qcheck('${p}')"></textarea><div class="qcheck" id="${p}_qc"></div>
  </div>`);
}

// ---- canonicalization & sealing ----
function canon(o) {
  if (Array.isArray(o)) return '[' + o.map(canon).join(',') + ']';
  if (o && typeof o === 'object') return '{' + Object.keys(o).sort().map(k => JSON.stringify(k) + ':' + canon(o[k])).join(',') + '}';
  return JSON.stringify(o);
}
async function sha256hex(str) {
  const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
}
function claimValue(p, f) {
  const m = $(p + '_mode').value;
  if (m === 'absent') return undefined;
  if (m === 'null') return null;
  const raw = $(p + '_v').value.trim();
  if (raw === '') return undefined;
  if (m === 'min') return {min: Number(raw)};
  if (f.type === 'count' || f.type === 'number') return Number(raw);
  if (f.type === 'bool') return raw === 'true';
  return raw;
}
async function build() {
  const problems = [], claims = [];
  const src = $('src').value;
  const push = (f, v, q, by, t) => {
    if (v === undefined) return;
    if (!q) { problems.push(`${f}: no quote, no claim`); return; }
    if (!src.includes(q)) { problems.push(`${f}: quote is not a verbatim substring of the source`); return; }
    const c = {f, v, q}; if (by) c.by = by; if (t) c.t = t; claims.push(c);
  };
  if (!currentClass) problems.push('pick an event class');
  else push('what', currentClass, $('what_q').value);
  if (!$('when').value) problems.push('when is required'); else push('when', $('when').value, $('when_q').value);
  if (!$('where').value) problems.push('where is required'); else push('where', $('where').value, $('where_q').value);
  fieldRegistry.forEach(({p, f, ext}) => {
    push(ext ? 'ext:' + f.name : f.name, claimValue(p, f), ($(p+'_q')||{}).value || '', ($(p+'_by')||{}).value || '', ($(p+'_t')||{}).value || '');
  });
  for (let i = 0; i < saidCount; i++) {
    const p = 's' + i; if (!$(p + '_v')) continue;
    const v = $(p + '_v').value.trim(); if (!v) continue;
    if (!$(p + '_by').value) { problems.push('statement: by is required for said'); continue; }
    push('said', v, $(p + '_q').value, $(p + '_by').value);
  }
  if ($('via').value) push('via', $('via').value, $('via_q').value);
  if (!$('url').value) problems.push('source URL is required');
  if (!src) problems.push('paste the source text');

  $('problems').innerHTML = problems.length ? '<p class="err">' + problems.map(e=>'• '+e).join('<br>') + '</p>' : '';
  if (problems.length) { $('out').style.display='none'; $('dl').style.display='none'; return; }

  claims.sort((a, b) => (a.f < b.f ? -1 : a.f > b.f ? 1 : canon(a) < canon(b) ? -1 : 1));
  const report = {
    pure: DATA.pure,
    source: { url: $('url').value, sha256: await sha256hex(src), retrievedAt: new Date().toISOString().replace(/\.\d+Z$/, 'Z') },
    claims
  };
  const bytes = canon(report);
  const id = 'sha256:' + await sha256hex(bytes);
  const whereV = $('where').value;
  const cell = whereV.startsWith('geo:') ? whereV.slice(4, 8) : whereV;
  const key = `${currentClass}|${$('when').value.slice(0, 10)}|${cell}`;
  sealed = bytes;
  $('out').style.display = '';
  $('out').textContent = `report id: ${id}\nevent key: ${key}\n\n` + JSON.stringify(report, null, 2);
  $('dl').style.display = '';
}
function download() {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([sealed + '\n'], {type: 'application/json'}));
  a.download = 'report.json'; a.click();
}
renderCascade('');
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
