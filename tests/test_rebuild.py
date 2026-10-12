import json
import zipfile

import pytest

from tcupdate import rebuild
from tcupdate import toc
from tcupdate.docx_model import Docx

from .conftest import CLI, DRAFT, REDLINE, REPO

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


# ---------- funzioni pure ----------
def test_nums_ignore_thousand_separators():
    assert rebuild.nums("€ 5.000,00") == rebuild.nums("€5,000.00") == rebuild.nums("5 000,00 €")
    assert rebuild.nums("art. 12.6 entro 3 giorni") == {"126", "3"}


def test_wdiff_marks_removals_and_additions():
    assert rebuild.wdiff("entro tre giorni", "entro cinque giorni lavorativi") == \
        "entro [-tre-] {+cinque+} giorni {+lavorativi+}"


def test_redline_pairs_split_rejected_and_accepted(tmp_path):
    body = (f'<w:document xmlns:w="{W}"><w:body><w:p><w:r><w:t>Il </w:t></w:r>'
            '<w:del><w:r><w:delText>vecchio</w:delText></w:r></w:del>'
            '<w:ins><w:r><w:t>nuovo</w:t></w:r></w:ins><w:r><w:t> testo</w:t></w:r></w:p>'
            '<w:p/></w:body></w:document>')
    path = tmp_path / "redline.docx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", body)
    assert rebuild.redline_pairs(path) == [("Il vecchio testo", "Il nuovo testo")]


def test_build_chunks_puts_definitions_and_titles_first(monkeypatch):
    monkeypatch.setattr(rebuild, "CHUNK_WORDS", 10)
    units = [{"id": "u1", "article": "0", "level": 1, "words": 2},
             {"id": "u2", "article": "1", "level": 1, "words": 5},
             {"id": "u3", "article": "2", "level": 0, "words": 1},
             {"id": "u4", "article": "2", "level": 1, "words": 8},
             {"id": "u5", "article": "3", "level": 0, "words": 1},
             {"id": "u6", "article": "3", "level": 1, "words": 8}]
    chunks = rebuild.build_chunks(units)
    assert [(c["id"], c["units"], c["words"]) for c in chunks] == [
        ("k01", ["u1", "u2", "u3", "u5"], 9), ("k02", ["u4"], 8), ("k03", ["u6"], 8)]


# ---------- controllo delle traduzioni ----------
@pytest.fixture
def mini_work(tmp_path):
    units = [{"id": "u1", "key": "2.1", "markup": "<b>Prezzo</b>: € 5.000,00 ai sensi dell'art. 3.2, vedi info@fleequid.com"}]
    (tmp_path / "units.json").write_text(json.dumps(units))
    (tmp_path / "chunks.json").write_text(json.dumps([{"id": "k02", "units": ["u1"]}]))
    (tmp_path / "rb" / "EN").mkdir(parents=True)

    def write(translations):
        (tmp_path / "rb" / "EN" / "tr_k02.json").write_text(json.dumps({"translations": translations}))
        return rebuild.check_chunk(tmp_path, "EN", "k02")
    return tmp_path, write


def test_check_chunk_accepts_a_faithful_translation(mini_work):
    _, write = mini_work
    assert write({"u1": "<b>Price</b>: €5,000.00 pursuant to Art. 3.2, see info@fleequid.com"}) == []


def test_check_chunk_reports_each_kind_of_defect(mini_work):
    work, write = mini_work
    assert rebuild.check_chunk(work, "EN", "k02") == ["k02: manca tr_k02.json"]
    assert "traduzione mancante" in write({})[0]
    errs = "\n".join(write({"u1": "Price: €6,000.00 pursuant to Art. 3.2\tsee the site", "u9": "x"}))
    for expected in ("B/I/U", "a capo o tabulazione", "numeri/rinvii mancanti ['500000']",
                     "non presenti nell'IT ['600000']", "link/e-mail mancante o alterato: info@fleequid.com",
                     "id estranei al blocco ['u9']"):
        assert expected in errs
    (work / "rb" / "EN" / "tr_k02.json").write_text("{")
    assert "JSON non valido" in rebuild.check_chunk(work, "EN", "k02")[0]


def test_check_chunk_waiver_silences_only_the_number_check(mini_work):
    work, write = mini_work
    (work / "rb" / "EN" / "waivers.json").write_text('["u1"]')
    assert write({"u1": "<b>Price</b>: five thousand euros pursuant to Art. three, see info@fleequid.com"}) == []


# ---------- lavoro reale General T&C v9, inglese ----------
def test_units_and_chunks_from_the_firm_redline_are_reproducible(v9):
    it_prev, it_new = Docx(v9.prev_docs["IT"]), Docx(v9.it_new_clean())
    units = rebuild.build_units(it_prev, it_new, REDLINE, v9.changes)
    stored = json.loads((v9.work / "units.json").read_text())
    # u325 (riga dell'indirizzo): archiviata «identico» prima che l'IT pulita perdesse la virgola finale della v8
    origin = lambda us: [(u["id"], u["idx"], u["key"], u["prev_idx"], u["cat"]) for u in us if u["id"] != "u325"]
    assert origin(units) == origin(stored)
    assert {u["cat"] for u in units} == {"identico", "ritoccato", "modificato", "riscritto", "nuovo"}
    without_redline = rebuild.build_units(it_prev, it_new, None, v9.changes)
    assert sum(u["prev_idx"] is None for u in without_redline) > sum(u["prev_idx"] is None for u in units)
    assert [c["units"] for c in rebuild.build_chunks(stored)] == \
        [c["units"] for c in json.loads((v9.work / "chunks.json").read_text())]


def test_committed_english_translation_passes_every_chunk(v9):
    chunks = json.loads((v9.work / "chunks.json").read_text())
    assert [e for ch in chunks for e in rebuild.check_chunk(v9.work, "EN", ch["id"])] == []


def test_build_reproduces_the_committed_word_and_verifies(v9):
    out, log = rebuild.build_docx(v9, "EN")
    assert REPO not in out.parents and "link localizzati su /en/" in log[1]
    assert rebuild.verify_docx(v9, "EN") == []
    built, committed = Docx(out), Docx(REPO / "T&C" / "General T&C" / "Vers 9 - Multilanguage - Q4 2026" / out.name)
    body = lambda d: [p.text for p in d.paras if not p.in_toc]
    assert body(built) == body(committed)
    assert "Version no F0009_2026" in " ".join(built.header_texts().values())


def test_verify_notices_a_paragraph_that_differs_from_the_translation(v9):
    rebuild.build_docx(v9, "EN")
    path = v9.work / "rb" / "EN" / "tr_k02.json"
    data = json.loads(path.read_text())
    unit = next(iter(data["translations"]))
    data["translations"][unit] += " EXTRA"
    path.write_text(json.dumps(data, ensure_ascii=False))
    assert any(e.startswith(unit) and "diverso dalla traduzione" in e for e in rebuild.verify_docx(v9, "EN"))


def test_terms_come_from_definitions_and_article_titles(v9):
    terms = {t["it"]: t["tr"] for t in rebuild.derive_terms(v9.work, "EN")}
    assert terms["Acquirente/i"] == "Buyer(s)" and terms["CG"] == "GTC"
    assert any(k.startswith("Titolo art. 18:") for k in terms)
    assert json.loads((v9.work / "rb" / "EN" / "terms.json").read_text())[0] == {"it": "Definizioni", "tr": "Definitions"}


def test_briefs_show_binding_terms_and_secondary_glossary(v9):
    k01, k02 = rebuild.write_briefs(v9, "EN")[:2]
    assert k01.parent == v9.work / "rb" / "EN"
    assert "Glossario cumulativo (IT → EN) — secondario" in k01.read_text()
    assert "[VAS - Fleequid Care v1]" in k01.read_text()
    assert "Tabella termini v9 già fissati per EN" in k02.read_text()
    assert [p.name for p in rebuild.write_briefs(v9, "EN", "k03")] == ["brief_k03.md"]


def test_glossary_takes_terms_once_and_skips_titles_and_fragments(v9):
    rebuild.build_docx(v9, "EN")
    gpath = rebuild.brief_mod.GLOSSARY_DIR / "EN.json"
    gpath.write_text(json.dumps([{"it": "Acquirente", "tr": "Buyer", "source": "VAS - Fleequid Care v1"}]))
    added, missing = rebuild.merge_glossary(v9, "EN")
    glossary = json.loads(gpath.read_text())
    new = [g for g in glossary if g["source"] == "General T&C v9"]
    assert added == len(new) > 50 and glossary[0]["source"] == "VAS - Fleequid Care v1"
    assert {"it": "Aggiudicazione definitiva", "tr": "Final Award", "source": "General T&C v9"} in new
    assert not [g for g in new if g["it"].startswith(("Titolo art.", "http", "(")) or g["it"] == ")"]
    assert all("→" in m for m in missing) and len(missing) < 5
    assert rebuild.merge_glossary(v9, "EN")[0] == 0


# ---------- riga di comando ----------
def test_cli_check_and_glossary(v9, capsys, monkeypatch):
    monkeypatch.setattr("tcupdate.__main__.Ctx", lambda a: v9)
    with pytest.raises(SystemExit) as stop:
        rebuild.main(["check", "--lang", "en", "--chunk", "k01", *CLI])
    assert stop.value.code == 0 and "k01: OK" in capsys.readouterr().out
    with pytest.raises(SystemExit) as stop:
        rebuild.main(["build", "--lang", "EN", *CLI])
    assert stop.value.code == 0 and "verifica: OK" in capsys.readouterr().out
    rebuild.main(["terms", "--lang", "EN", *CLI])
    rebuild.main(["brief", "--lang", "EN", "--chunk", "k02", *CLI])
    rebuild.main(["glossary", "--lang", "EN", *CLI])
    out = capsys.readouterr().out
    assert "termini → " in out and "brief_k02.md" in out and "termini aggiunti a glossary/EN.json" in out
    with pytest.raises(SystemExit):
        rebuild.main(["check", *CLI])


def test_cli_prepare_writes_units_chunks_and_italian_text(v9, capsys, monkeypatch):
    monkeypatch.setattr("tcupdate.__main__.Ctx", lambda a: v9)
    stored = json.loads((v9.work / "units.json").read_text())
    rebuild.main(["prepare", "--redline", str(REDLINE), *CLI])
    assert len(json.loads((v9.work / "units.json").read_text())) == len(stored)
    assert (v9.work / "it_new.txt").read_text().startswith("[")
    assert (rebuild.ROOT / "work" / "refs" / "general_IT_v8.txt").exists()
    assert f"unità: {len(stored)}" in capsys.readouterr().out


# ---------- brief del flusso ordinario ----------
def test_ordinary_brief_shows_the_source_of_each_glossary_entry(tmp_path):
    """Fleequid Care v1 → v2: nel brief ogni voce del glossario porta il documento da cui viene."""
    from argparse import Namespace
    from tcupdate import align, brief
    from tcupdate.__main__ import Ctx
    c = Ctx(Namespace(family="Fleequid Care", from_=1, to=2, draft=None, langs="EN"))
    it_prev, target = Docx(c.prev_docs["IT"]), Docx(c.prev_docs["EN"])
    glossary = [{"it": "Acquirente", "tr": "Buyer", "source": "VAS - Fleequid Care v1"},
                {"it": "CG", "tr": "GTC", "source": "General T&C v9"}]
    path = brief.build(c.changes, it_prev, Docx(c.it_new_clean()), target, align.align(it_prev, target), "EN",
                       glossary, None, tmp_path)
    text = path.read_text()
    assert "- Acquirente → Buyer [VAS - Fleequid Care v1]" in text and "- CG → GTC [General T&C v9]" in text


# ---------- indice ----------
def test_working_copy_for_word_drops_the_read_only_recommendation(tmp_path):
    with zipfile.ZipFile(DRAFT) as z:
        assert b"<w:writeProtection" in z.read("word/settings.xml")
    copy = tmp_path / "in.docx"
    toc._copy_writable(DRAFT, copy)
    with zipfile.ZipFile(DRAFT) as a, zipfile.ZipFile(copy) as b:
        assert b"<w:writeProtection" not in b.read("word/settings.xml")
        assert a.namelist() == b.namelist()
        assert a.read("word/document.xml") == b.read("word/document.xml")
