from argparse import Namespace

from tcupdate import diff
from tcupdate.__main__ import Ctx


def test_version_code_is_found_in_both_forms():
    assert diff.VERSION_RE.findall("22CPA-1Euro_Auctions_Vers_1_2026") == ["Vers_1_2026"]
    assert diff.VERSION_RE.findall("Versione nr. CSFC-F0002_2026") == ["CSFC-F0002_2026"]
    assert diff.VERSION_RE.findall("Versione 2 del 2026") == []


def test_new_code_keeps_the_spelling_found_in_the_file_name():
    assert diff.same_form("Versione_1_2026", "Vers_2_2026") == "Versione_2_2026"
    assert diff.same_form("Vers_1_2026", "Vers_2_2026") == "Vers_2_2026"
    assert diff.same_form("CSFC-F0001_2025", "CSFC-F0002_2026") == "CSFC-F0002_2026"


def test_output_names_follow_the_previous_file_of_each_language():
    care = Ctx(Namespace(family="Fleequid Care", from_=1, to=2, draft=None, langs="EN"))
    assert care.out_name("EN").name == "Condizioni_Specifiche_Fleequid_Care_CSFC-F0002_2026_DEF_DEF_EN.docx"
    auctions = Ctx(Namespace(family="1 Euro Auctions", from_=1, to=2, draft="bozza-non-letta.docx", langs="EN"))
    auctions._changes = {"version_prev": ["Vers_1_2026"], "version_new": ["Vers_2_2026"]}
    assert auctions.out_name("EN").name == "2_CPA_1EuroAuction_Versione_2_2026_DEF_ENG.docx"
    assert auctions.out_name("CZ").name == "2_CPA_1EuroAuction_Versione_2_2026_DEF_CECO.docx"


def test_general_reference_is_always_the_latest_version(tmp_path, monkeypatch):
    """Un testo di riferimento rimasto a una versione vecchia viene sostituito anche se il file è più recente del Word."""
    import os, time
    from tcupdate import __main__ as cli
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    stale = tmp_path / "work" / "refs" / "general_EN.txt"
    stale.parent.mkdir(parents=True)
    stale.write_text("testo della versione precedente")
    os.utime(stale, (time.time() + 3600,) * 2)
    assert cli._general_ref("EN") == stale.relative_to(tmp_path)
    assert "Binding Agreement" in stale.read_text()
