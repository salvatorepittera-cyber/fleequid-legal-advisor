"""CLI: python -m tcupdate <comando> --family "Fleequid Care" --from 1 --to 2 [--langs EN,DE] [--draft file]

Comandi (in ordine di flusso):
  inventory   elenco famiglie/versioni/lingue
  diff        IT prev vs bozza IT nuova -> work/.../changes.json + diff_report.md
  clean-it    IT nuova pulita (solo evidenziazioni rimosse + it_fixes.json) -> cartella nuova versione
  prepare     per lingua: allineamento + glossario + brief per il traduttore
  inject      per lingua: applica work/.../translations/<LANG>.json -> Word nuova versione + verifica
  toc         aggiorna i numeri di pagina dell'indice con Word + PDF di controllo
  verify      ricontrolla tutti gli output
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import align as align_mod
from . import brief as brief_mod
from . import clean_it, diff as diff_mod, inject as inject_mod, inventory as inv, toc as toc_mod, verify as verify_mod
from .docx_model import Docx

ROOT = Path(__file__).resolve().parent.parent


def slug(s: str) -> str:
    s = re.sub(r"^(VAS\s*-\s*)", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


class Ctx:
    def __init__(self, a):
        self.family = inv.find_family(a.family)
        vers = inv.families()[self.family]
        self.v_from, self.v_to = a.from_, a.to
        if self.v_from not in vers:
            raise SystemExit(f"Versione {self.v_from} non trovata per {self.family}: {list(vers)}")
        if self.v_to not in vers:
            raise SystemExit(f"Cartella della versione {self.v_to} non trovata (crea 'Vers {self.v_to} - ...' con la bozza IT)")
        self.prev_dir, self.new_dir = vers[self.v_from], vers[self.v_to]
        self.prev_docs = inv.docs_by_lang(self.prev_dir)
        self.draft = Path(a.draft) if a.draft else inv.draft_in(self.new_dir)
        self.work = ROOT / "work" / slug(self.family) / f"v{self.v_to}"
        self.work.mkdir(parents=True, exist_ok=True)
        self.langs = [l.strip().upper() for l in a.langs.split(",")] if a.langs else inv.TARGET_LANGS
        self._changes = None

    @property
    def changes(self) -> dict:
        if self._changes is None:
            p = self.work / "changes.json"
            if not p.exists():
                raise SystemExit("Esegui prima: diff")
            self._changes = json.loads(p.read_text())
        return self._changes

    def out_name(self, lang: str) -> Path:
        it_prev = self.prev_docs["IT"].name
        m = diff_mod.VERSION_RE.search(it_prev)
        vp, vn = self.changes["version_prev"], self.changes["version_new"]
        if m and vn:
            prefix = it_prev[: m.start()]
            prefix = re.sub(rf"^{self.v_from}_", f"{self.v_to}_", prefix)
            name = f"{prefix}{vn[0]}_DEF_{lang}.docx"
        else:
            name = f"{slug(self.family)}_v{self.v_to}_DEF_{lang}.docx"
        return self.new_dir / name

    def it_new_clean(self) -> Path:
        p = self.out_name("IT")
        if not p.exists():
            raise SystemExit("Esegui prima: clean-it")
        return p


def cmd_diff(c: Ctx):
    d = diff_mod.run(c.prev_docs["IT"], c.draft, c.work)
    print((c.work / "diff_report.md").read_text())
    print(f"→ {c.work / 'changes.json'}  ({len(d['changes'])} voci)")


def cmd_clean_it(c: Ctx):
    out = c.out_name("IT")
    log = clean_it.run(c.draft, out, c.work / "it_fixes.json")
    print("\n".join(log))
    print(f"→ {out}")


def _general_ref(lang: str) -> Path | None:
    fams = inv.families()
    gen = next((f for f in fams if f.lower().startswith("general")), None)
    if not gen:
        return None
    latest = fams[gen][max(fams[gen])]
    docs = inv.docs_by_lang(latest)
    if lang not in docs:
        return None
    out = ROOT / "work" / "refs" / f"general_{lang}.txt"
    if not out.exists() or out.stat().st_mtime < docs[lang].stat().st_mtime:
        brief_mod.general_text_dump(docs[lang], out)
    return out.relative_to(ROOT)


def cmd_prepare(c: Ctx):
    it_prev = Docx(c.prev_docs["IT"])
    it_new = Docx(c.it_new_clean())
    summary = []
    for lang in c.langs:
        if lang not in c.prev_docs:
            print(f"{lang}: nessun documento nella versione {c.v_from}, salto")
            continue
        tgt = Docx(c.prev_docs[lang])
        al = align_mod.align(it_prev, tgt)
        align_mod.save(al, c.work / f"alignment_{lang}.json")
        rep, problems = align_mod.report(it_prev, tgt, al, c.changes, lang)
        (c.work / f"alignment_{lang}.md").write_text(rep)
        gl = brief_mod.build_glossary(it_prev, tgt, al, lang, f"{c.family} v{c.v_from}")
        b = brief_mod.build(c.changes, it_prev, it_new, tgt, al, lang, gl, _general_ref(lang), c.work / "briefs")
        summary.append(f"{lang}: brief {b.relative_to(ROOT)}; allineamento " +
                       ("OK" if not problems else "DA CONFERMARE: " + "; ".join(problems)))
    print("\n".join(summary))


def _verify_one(c: Ctx, lang: str, it_prev: Docx, it_new_draft: Docx, it_new: Docx) -> tuple[list, list]:
    out = Docx(c.out_name(lang))
    if lang == "IT":
        return verify_mod.run(c.changes, it_prev, it_new_draft, it_new_draft, out, None, is_it=True)
    al = align_mod.load(c.work / f"alignment_{lang}.json")
    return verify_mod.run(c.changes, it_prev, it_new, Docx(c.prev_docs[lang]), out, al)


def cmd_inject(c: Ctx, strict: bool):
    it_prev = Docx(c.prev_docs["IT"])
    it_new = Docx(c.it_new_clean())
    draft = Docx(c.draft)
    report = []
    ok = True
    for lang in c.langs:
        tp = c.work / "translations" / f"{lang}.json"
        if not tp.exists():
            print(f"{lang}: manca {tp.relative_to(ROOT)}, salto")
            continue
        tr = json.loads(tp.read_text())["translations"]
        al = align_mod.load(c.work / f"alignment_{lang}.json")
        log = inject_mod.run(c.changes, it_prev, it_new, Docx(c.prev_docs[lang]), al, tr, c.out_name(lang), strict)
        errs, warns = _verify_one(c, lang, it_prev, draft, it_new)
        ok &= not errs
        report.append(f"## {lang} — {'OK' if not errs else 'ERRORI'}\n\n`{c.out_name(lang).name}`\n\n" +
                      "\n".join(f"- {l}" for l in log) +
                      ("\n\n**Errori:**\n" + "\n".join(f"- ❌ {e}" for e in errs) if errs else "") +
                      ("\n\n**Avvisi:**\n" + "\n".join(f"- ⚠️ {w}" for w in warns) if warns else "") + "\n")
        print(f"{lang}: {'OK' if not errs else 'ERRORI ' + str(errs)}" + (f"  avvisi: {warns}" if warns else ""))
    (c.work / "inject_report.md").write_text("# Iniezione traduzioni\n\n" + "\n".join(report))
    if not ok:
        sys.exit(1)


def cmd_verify(c: Ctx):
    it_prev = Docx(c.prev_docs["IT"])
    draft = Docx(c.draft)
    it_new = Docx(c.it_new_clean())
    lines = ["# Verifica output\n"]
    bad = False
    for lang in ["IT"] + c.langs:
        if not c.out_name(lang).exists():
            lines.append(f"- {lang}: output assente")
            bad = True
            continue
        errs, warns = _verify_one(c, lang, it_prev, draft, it_new)
        bad |= bool(errs)
        lines.append(f"- **{lang}**: {'✅ OK' if not errs else '❌ ' + '; '.join(errs)}" +
                     (f"  (avvisi: {'; '.join(warns)})" if warns else ""))
    (c.work / "verify_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if bad:
        sys.exit(1)


def cmd_toc(c: Ctx):
    for lang in ["IT"] + c.langs:
        p = c.out_name(lang)
        if not p.exists():
            continue
        log = toc_mod.update(p, c.work / "pdf" / (p.stem + ".pdf"))
        print(f"{lang}: " + "; ".join(log))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tcupdate", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["inventory", "diff", "clean-it", "prepare", "inject", "toc", "verify"])
    ap.add_argument("--family")
    ap.add_argument("--from", dest="from_", type=int)
    ap.add_argument("--to", type=int)
    ap.add_argument("--langs")
    ap.add_argument("--draft")
    ap.add_argument("--no-strict", action="store_true", help="consenti abbinamenti non a chiave (dopo conferma)")
    a = ap.parse_args(argv)
    if a.command == "inventory":
        inv.print_inventory()
        return
    if not (a.family and a.from_ and a.to):
        ap.error("servono --family --from --to")
    c = Ctx(a)
    {"diff": lambda: cmd_diff(c), "clean-it": lambda: cmd_clean_it(c), "prepare": lambda: cmd_prepare(c),
     "inject": lambda: cmd_inject(c, not a.no_strict), "toc": lambda: cmd_toc(c),
     "verify": lambda: cmd_verify(c)}[a.command]()


if __name__ == "__main__":
    main()
