import pytest

from tcupdate import inventory as inv


def touch(folder, *names):
    for n in names:
        (folder / n).write_bytes(b"")


def test_lang_of_reads_historical_codes():
    from pathlib import Path
    assert inv.lang_of(Path("1_CPA_1EuroAuction_Versione_1_2026_DEF_CECO.docx")) == "CZ"
    assert inv.lang_of(Path("9_Termini_F0009_2026_BOZZA_STUDIO.docx")) is None


def test_service_document_does_not_hide_the_language_word(tmp_path):
    """Il file di osservazioni «…_IT_F0009_2026» non è il Word italiano: vince il codice lingua a fine nome."""
    touch(tmp_path, "9_Termini_F0009_2026_IT.docx", "Osservazioni_sulla_bozza_IT_F0009_2026.docx",
          "9_Termini_F0009_2026_EN.docx", "~$Termini_F0009_2026_DE.docx")
    docs = inv.docs_by_lang(tmp_path)
    assert {k: v.name for k, v in docs.items()} == {"IT": "9_Termini_F0009_2026_IT.docx",
                                                    "EN": "9_Termini_F0009_2026_EN.docx"}


def test_service_document_listed_first_is_replaced(tmp_path):
    touch(tmp_path, "0_Osservazioni_IT_F0009_2026.docx", "9_Termini_F0009_2026_IT.docx")
    assert inv.docs_by_lang(tmp_path)["IT"].name == "9_Termini_F0009_2026_IT.docx"


def test_two_real_documents_for_one_language_still_fail(tmp_path):
    touch(tmp_path, "A_DEF_IT.docx", "B_DEF_ITA.docx")
    with pytest.raises(ValueError, match="Due file per la lingua IT"):
        inv.docs_by_lang(tmp_path)
