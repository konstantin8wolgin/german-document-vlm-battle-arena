from __future__ import annotations


def _doc(category: str, number: int, title: str, url: str, pages: list[int], note: str) -> dict:
    doc_id = f"{category}_{number:03d}"
    return {
        "doc_id": doc_id,
        "category": category,
        "title": title,
        "source_url": url,
        "source_license_note": note,
        "selected_pages": pages,
        "split": "active" if number <= 5 else "reserve",
        "local_pdf_path": f"data/pdfs/{doc_id}.pdf",
        "sha256": None,
    }


def curated_documents() -> list[dict]:
    public_note = "public internet PDF; verify source-specific reuse terms before redistribution"
    return [
        _doc("rechnungen", 1, "IHK Musterrechnung", "https://www.ihk.de/blueprint/servlet/resource/blob/6246454/e922f99ff6b4a5e8800ffad21680b4ce/musterrechnung-data.pdf", [1], public_note),
        _doc("rechnungen", 2, "IHK Kleinunternehmerrechnung", "https://www.ihk.de/blueprint/servlet/resource/blob/5581278/1cafa7f203df9d83e050d9f01677ffe6/rechnung-kleinunternehmer-data.pdf", [1], public_note),
        _doc("rechnungen", 3, "IHK Schleswig-Holstein Musterrechnung", "https://www.ihk.de/blueprint/servlet/resource/blob/1369812/0c4aa4a7f4e160c7a9d687a1ae6a73bd/musterrechnung-bf-data.pdf", [1], public_note),
        _doc("rechnungen", 4, "IHK Musterrechnung 2024", "https://www.ihk.de/blueprint/servlet/resource/blob/4803860/a0e4b62c2cbf6fbd8d733f6a4296eb38/musterrechnung-2024-barrierefrei-data.pdf", [1], public_note),
        _doc("rechnungen", 5, "IHK Musterrechnung mit Mehrwertsteuer", "https://www.ihk.de/blueprint/servlet/resource/blob/6779794/5ce7d6a0d1b97317c649a80b2c378e6b/musterrechnung-mit-mwst--data.pdf", [1], public_note),
        _doc("vertraege", 1, "IHK GmbH-Geschaeftsfuehrer Mustervertrag", "https://www.ihk.de/blueprint/servlet/resource/blob/1465484/56cb5f0690c00a31daa67518881271d8/gmbh-geschaeftsfuehrer-mustervertrag-data.pdf", [1, 2], public_note),
        _doc("vertraege", 2, "IHK Reinigungsvertrag", "https://www.ihk.de/blueprint/servlet/resource/blob/3699538/f37d24be295a448dd49cb3c0fecc590d/tiptop-reinigungsvertrag-gebaeudereinigung-data.pdf", [1, 2], public_note),
        _doc("vertraege", 3, "IHK Werkvertrag", "https://www.ihk.de/blueprint/servlet/resource/blob/2264830/5a6d1c867ccca3c29f9e6bbb93ff5d85/werkvertrag-data.pdf", [1, 2], public_note),
        _doc("vertraege", 4, "IHK Fernabsatzvertraege", "https://www.ihk.de/blueprint/servlet/resource/blob/1407038/a7e6cbc38c20c905a1afecc048e9ced1/merkblatt-fernabsatzvertraege-data.pdf", [1, 2], public_note),
        _doc("vertraege", 5, "IHK UN-Kaufrecht", "https://www.ihk.de/blueprint/servlet/resource/blob/5240230/883cab8a0b4c3d22e27b909e670ec7fc/un-kaufrecht-broschuere-data.pdf", [1, 2], public_note),
        _doc("behoerdenpost", 1, "FragDenStaat Widerspruchsbescheid Flensburg", "https://fragdenstaat.de/files/foi/628496/02-widerspruchsbescheid_pub_geschwaerzt.pdf?download=", [1, 2], "redacted public FOI correspondence"),
        _doc("behoerdenpost", 2, "FragDenStaat Widerspruch BSB", "https://fragdenstaat.de/files/foi/1014668/widerspruch-bsb-22042025_geschwaerzt.pdf?download=", [1, 2], "redacted public FOI correspondence"),
        _doc("behoerdenpost", 3, "FragDenStaat Widerspruch Bescheid", "https://fragdenstaat.de/files/foi/104175/widerspruch_bescheid_geschwaerzt.pdf?download=", [1, 2], "redacted public FOI correspondence"),
        _doc("behoerdenpost", 4, "FragDenStaat Antwort Bescheid", "https://fragdenstaat.de/files/foi/588348/antwort-2021-04-13_geschwaerzt.pdf?download=", [1, 2], "redacted public FOI correspondence"),
        _doc("behoerdenpost", 5, "FragDenStaat BMI Widerspruchsbescheid", "https://fragdenstaat.de/files/foi/13558/bmi_widerspruchsbescheid_geschwaerzt.pdf?download=", [1, 2], "redacted public FOI correspondence"),
        _doc("versicherung", 1, "GDV Haftpflicht AHB", "https://www.gdv.de/resource/blob/6132/3206ded4f5f7698cc9df23383aecd6d6/01-allgemeine-versicherungsbedingungen-fuer-die-haftpflichtversicherung-ahb--data.pdf", [1, 2], public_note),
        _doc("versicherung", 2, "GDV Cyber AVB", "https://www.gdv.de/resource/blob/6100/a0fed56c4947751cdc20b5206c171d98/01-allgemeine-versicherungsbedingungen-fuer-die-cyberrisiko-versicherung-avb-cyber--data.pdf", [1, 2], public_note),
        _doc("versicherung", 3, "GDV Wohngebaeude VGB 2022", "https://www.gdv.de/resource/blob/37090/562b0c381cf8f48be1cdafb8e74cc2e3/allgemeine-wohngebaeude-versicherungsbedingungen-vgb-2022-wohnflaechenmodell--data.pdf", [1, 2], public_note),
        _doc("versicherung", 4, "GDV Hausrat VHB 2022", "https://www.gdv.de/resource/blob/6114/458ab7b03401b2bb3bd22b707a5ec6cc/allgemeine-hausrat-versicherungsbedingungen-vhb-2022-quadratmetermodell--data.pdf", [1, 2], public_note),
        _doc("versicherung", 5, "GDV Kfz AKB 2015", "https://www.gdv.de/resource/blob/6178/ec39e06d2f552aca5f35f19277c94603/01-allgemeine-bedingungen-fuer-die-kfz-versicherung-akb-2015--data.pdf", [1, 2], public_note),
        _doc("bank_finanzen", 1, "Bundesbank SEPA Mandatsvordruck", "https://www.bundesbank.de/resource/blob/604032/f58c7ae5ddc02201a64b5b8e3176de4d/mL/4806-mandatsvordruck-hvb-entgelte-data.pdf", [1, 2], public_note),
        _doc("bank_finanzen", 2, "Bundesbank SEPA Lastschrift Verfahrensregeln", "https://www.bundesbank.de/resource/blob/895176/d6e28cbceb27abad572105d33fddc9fa/mL/verfahrensregeln-fuer-sepa-lastschriften-1-0-032023-data.pdf", [1, 2], public_note),
        _doc("bank_finanzen", 3, "Bundesbank EBICS Verfahrensregeln", "https://www.bundesbank.de/resource/blob/964228/6db68b835ecd37d6f54ae4633bb9462a/472B63F073F071307366337C94F8C870/verfahrensregeln-ebics-2025-data.pdf", [1, 2], public_note),
        _doc("bank_finanzen", 4, "Bundesbank Kundendaten-Meldebogen Hinweise", "https://www.bundesbank.de/resource/blob/600130/958232a965af20619743f26139cb2525/472B63F073F071307366337C94F8C870/3000a-ausfuellhinweise-zum-kundendaten-meldebogen-data.pdf", [1, 2], public_note),
        _doc("bank_finanzen", 5, "Bundesbank SEPA Mitteilung", "https://www.bundesbank.de/resource/blob/671762/99f22b8717bbd84d144db74f0bfad87b/mL/2008-03-19-4001-data.pdf", [1, 2], public_note),
        _doc("steuer", 1, "BMF Vollmacht Besteuerungsverfahren", "https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/2025-03-27-neufassung-muster-vollmachten.pdf?__blob=publicationFile&v=5", [1, 2], public_note),
        _doc("steuer", 2, "BMF Vordruck EZVA", "https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Altersvorsorge/2025-10-17-vordruck-ezva.pdf?__blob=publicationFile&v=2", [1, 2], public_note),
        _doc("steuer", 3, "BMF Steuerbescheinigung Kapitalertragsteuer", "https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Abgeltungsteuer/2025-05-16-kapitalertragSt-steuerbescheinigung.pdf?__blob=publicationFile&v=3", [1, 2], public_note),
        _doc("steuer", 4, "BMF Anlage EUER 2025", "https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Einkommensteuer/2025-08-29-anlage-EUER-2025.pdf?__blob=publicationFile&v=3", [1, 2], public_note),
        _doc("steuer", 5, "BMF Energetische Steuerermaessigung", "https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Einkommensteuer/2024-12-23-steuererm-energetische-bmf-schreiben.pdf?__blob=publicationFile&v=4", [1, 2], public_note),
        _doc("medizin", 1, "KBV Mustersammlung", "https://www.kbv.de/documents/infothek/rechtsquellen/bundesmantelvertrag/anlage-02-vordruckvereinbarung/02_Mustersammlung.pdf", [1, 2], public_note),
        _doc("medizin", 2, "KBV Vordruckvereinbarung", "https://www.kbv.de/documents/infothek/rechtsquellen/bundesmantelvertrag/anlage-02-vordruckvereinbarung/02_Vordruckvereinbarung.pdf", [1, 2], public_note),
        _doc("medizin", 3, "KBV Blankoformularbedruckung", "https://www.kbv.de/documents/infothek/rechtsquellen/bundesmantelvertrag/anlage-02a-blankoformularbedruckung/02a_Blankoformularbedruckung.pdf", [1, 2], public_note),
        _doc("medizin", 4, "KBV Muster 9 2026", "https://www.kbv.de/documents/praxis/verordnungen/muster-9-2026.pdf", [1], public_note),
        _doc("medizin", 5, "KBV PTV Ausfuellhilfen", "https://www.kbv.de/documents/infothek/rechtsquellen/psychotherapie/ptv-ausfuellhilfen.pdf", [1, 2], public_note),
        _doc("formulare", 1, "Arbeitsagentur Buergergeld Hauptantrag", "https://www.arbeitsagentur.de/datei/antrag-sgb2_ba042689.pdf", [1, 2], public_note),
        _doc("formulare", 2, "Arbeitsagentur Weiterbewilligungsantrag", "https://www.arbeitsagentur.de/datei/weiterbewilligung-sgb2_ba042699.pdf", [1, 2], public_note),
        _doc("formulare", 3, "Arbeitsagentur Anlage EK", "https://www.arbeitsagentur.de/datei/anlageek_ba032960.pdf", [1, 2], public_note),
        _doc("formulare", 4, "Arbeitsagentur Anlage KDU", "https://www.arbeitsagentur.de/datei/anlagekdu_ba032980.pdf", [1, 2], public_note),
        _doc("formulare", 5, "Arbeitsagentur Anlage SV", "https://www.arbeitsagentur.de/datei/anlagesv_ba033005.pdf", [1, 2], public_note),
    ]
