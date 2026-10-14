import json
import re
from argparse import Namespace

from tcupdate import align, inject
from tcupdate.__main__ import Ctx
from tcupdate.docx_model import Docx


def test_new_unnumbered_section_keeps_the_italian_format_not_the_anchor_numbering(tmp_path):
    """1 Euro Auctions v2: la sezione finale nuova non ha un paragrafo precedente con lo stesso formato.

    Non deve ereditare la numerazione dell'ultimo comma (6.5), dopo il quale viene inserita.
    """
    c = Ctx(Namespace(family="1 Euro Auctions", from_=1, to=2, draft="bozza-non-letta.docx", langs="EN"))
    it_prev, it_new = Docx(c.prev_docs["IT"]), Docx(c.it_new_clean())
    translations = json.loads((c.work / "translations" / "EN.json").read_text())["translations"]
    out = tmp_path / "EN.docx"
    inject.run(c.changes, it_prev, it_new, Docx(c.prev_docs["EN"]), align.load(c.work / "alignment_EN.json"),
               translations, out)
    built = Docx(out)
    assert [p.key for p in built.paras] == [p.key for p in it_new.paras]
    section = built.paras[57:]
    assert [p.text for p in section][:2] == ["*****", "Specific approval pursuant to arts. 1341 and 1342 of the Italian Civil Code"]
    assert all(b"<w:numPr" not in p.ppr_xml() and b"it-IT" not in p.ppr_xml() for p in section)
    # le dichiarazioni xmlns dipendono dal file di provenienza, non dal formato del paragrafo
    fmt = lambda p: re.sub(rb' xmlns:\w+="[^"]*"', b"", p.ppr_xml())
    assert [fmt(p) for p in section] == [fmt(p) for p in it_new.paras[57:]]
    assert "Vers_2_2026" in " ".join(built.header_texts().values())
