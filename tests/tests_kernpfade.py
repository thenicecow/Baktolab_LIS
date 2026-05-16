"""Pragmatische Smoke-Tests fuer die wichtigsten Kernpfade der App."""

from __future__ import annotations

from datetime import date
import unittest
from unittest.mock import Mock, patch

from domaene import Kulturdaten, KulturKeim, Material, Patient
from functions.kulturen.ansicht import (
    baue_formularschluessel,
    baue_kulturdaten_aus_formularvorschau,
    bestaetige_keimzahl,
    initialisiere_formularzustand,
    setze_keimzahl_als_unbestaetigt,
)
from functions.kulturen.beurteilung import (
    BeurteilterKeim,
    ERGEBNIS_ID_RESI,
    UrinBeurteilung,
    beurteile_urin_allgemeine_bakteriologie,
)
import functions.kulturen.ansicht as kulturen_ansicht
import functions.materialien.erfassung as material_erfassung
import functions.patienten.erfassung as patienten_erfassung
import views.befund as befund_ansicht


class FakeStreamlit:
    """Minimale Streamlit-Attrappe fuer logiknahe Tests ohne UI-Laufzeit."""

    def __init__(self) -> None:
        self.session_state: dict[str, object] = {}
        self.fehlermeldungen: list[str] = []

    def error(self, nachricht: str) -> None:
        """Speichert Fehlermeldungen zur spaeteren Pruefung."""
        self.fehlermeldungen.append(nachricht)


class FakePatientenRepository:
    """Einfache Repository-Attrappe fuer Patienten- und Materialtests."""

    def __init__(self, patientenakte: tuple[Patient, list[Material]] | None = None) -> None:
        self.patientenakte = patientenakte
        self.gespeicherte_patienten: list[Patient] = []
        self.gespeicherte_materiallisten: list[tuple[Patient, list[Material]]] = []

    def speichere_neuen_patienten(self, patient: Patient) -> None:
        """Merkt sich einen neu gespeicherten Patienten."""
        self.gespeicherte_patienten.append(patient)

    def lade_patientenakte_nach_id(
        self,
        patient_id: str,
    ) -> tuple[Patient, list[Material]] | None:
        """Liefert eine vorbereitete Patientenakte nach ID."""
        if self.patientenakte is None:
            return None

        patient, materialien = self.patientenakte
        if patient.id != patient_id:
            return None

        return patient, list(materialien)

    def speichere_patient_mit_materialien(
        self,
        patient: Patient,
        materialien: list[Material],
    ) -> None:
        """Merkt sich die zuletzt gespeicherte Materialliste eines Patienten."""
        self.gespeicherte_materiallisten.append((patient, list(materialien)))


class KernpfadSmokeTests(unittest.TestCase):
    """Deckt die wichtigsten Kernpfade der App mit pragmatischen Smoke-Tests ab."""

    def baue_patient(self, patient_id: str = "patient-1") -> Patient:
        """Erzeugt einen konsistenten Patienten fuer Tests."""
        return Patient(
            id=patient_id,
            vorname="Anna",
            nachname="Muster",
            geburtsdatum=date(1992, 5, 14),
            geschlecht="weiblich",
            erstellt_von_user_id="tester",
        )

    def baue_material(
        self,
        patient_id: str,
        material_id: str = "material-1",
        kulturdaten: Kulturdaten | None = None,
    ) -> Material:
        """Erzeugt ein konsistentes Urinmaterial fuer Tests."""
        return Material(
            id=material_id,
            patient_id=patient_id,
            materialtyp_code="urin",
            klinische_frage_code="allgemeine_bakteriologie",
            abnahmedatum=date(2026, 5, 13),
            eingangsdatum=date(2026, 5, 13),
            kulturdaten=kulturdaten or Kulturdaten(),
            erstellt_von_user_id="tester",
        )

    def test_patienten_erfassen_speichert_neuen_patienten(self) -> None:
        """Prueft den Smoke-Pfad fuer das Speichern eines neuen Patienten."""
        fake_streamlit = FakeStreamlit()
        fake_streamlit.session_state.update(
            {
                patienten_erfassung.VORNAME_SCHLUESSEL: "Anna",
                patienten_erfassung.NACHNAME_SCHLUESSEL: "Muster",
                patienten_erfassung.GEBURTSTAG_SCHLUESSEL: 14,
                patienten_erfassung.GEBURTSMONAT_SCHLUESSEL: 5,
                patienten_erfassung.GEBURTSJAHR_SCHLUESSEL: 1992,
                patienten_erfassung.GESCHLECHT_SCHLUESSEL: "weiblich",
            }
        )
        fake_repository = FakePatientenRepository()

        with patch.object(patienten_erfassung, "st", fake_streamlit):
            with patch.object(
                patienten_erfassung,
                "hole_aktuellen_user_id",
                return_value="tester",
            ):
                with patch.object(
                    patienten_erfassung,
                    "erzeuge_patient_id",
                    return_value="patient-test-1",
                ):
                    with patch.object(
                        patienten_erfassung,
                        "PatientenRepository",
                        Mock(return_value=fake_repository),
                    ):
                        erfolgsmeldung = patienten_erfassung.speichere_patient()

        self.assertIsNotNone(erfolgsmeldung)
        self.assertIn("patient-test-1", erfolgsmeldung or "")
        self.assertEqual(len(fake_repository.gespeicherte_patienten), 1)
        self.assertEqual(fake_repository.gespeicherte_patienten[0].vorname, "Anna")
        self.assertEqual(fake_streamlit.fehlermeldungen, [])

    def test_material_erfassen_speichert_material_beim_patienten(self) -> None:
        """Prueft den Smoke-Pfad fuer das Speichern eines neuen Materials."""
        patient = self.baue_patient()
        fake_repository = FakePatientenRepository((patient, []))
        fake_streamlit = FakeStreamlit()

        with patch.object(material_erfassung, "st", fake_streamlit):
            with patch.object(
                material_erfassung,
                "hole_aktuellen_user_id",
                return_value="tester",
            ):
                with patch.object(
                    material_erfassung,
                    "erzeuge_material_id",
                    return_value="material-test-1",
                ):
                    ergebnis = material_erfassung.speichere_material(
                        repository=fake_repository,
                        patient_id=patient.id,
                        materialtyp_code="urin",
                        analyse_code="allgemeine_bakteriologie",
                        abnahmedatum=date(2026, 5, 13),
                        eingangsdatum=date(2026, 5, 13),
                    )

        self.assertIsNotNone(ergebnis)
        assert ergebnis is not None
        gespeicherter_patient, material = ergebnis
        self.assertEqual(gespeicherter_patient.id, patient.id)
        self.assertEqual(material.id, "material-test-1")
        self.assertEqual(material.patient_id, patient.id)
        self.assertEqual(len(fake_repository.gespeicherte_materiallisten), 1)
        self.assertEqual(len(fake_repository.gespeicherte_materiallisten[0][1]), 1)
        self.assertEqual(fake_streamlit.fehlermeldungen, [])

    def test_kulturen_ablesen_formularpfad_liefert_bestaetigte_kulturdaten(self) -> None:
        """Prueft den Kernpfad von Formularzustand, Keimzahl-Bestaetigung und Kulturdatenbau."""
        material = self.baue_material(patient_id="patient-1")
        fake_streamlit = FakeStreamlit()

        with patch.object(kulturen_ansicht, "st", fake_streamlit):
            initialisiere_formularzustand(material)

            fake_streamlit.session_state[
                baue_formularschluessel(material.id, "keimauswahl_0")
            ] = "Escherichia coli"
            fake_streamlit.session_state[
                baue_formularschluessel(material.id, "keimzahl_code_0")
            ] = "p5"

            setze_keimzahl_als_unbestaetigt(material.id, 0)
            self.assertFalse(
                fake_streamlit.session_state[
                    kulturen_ansicht.baue_keimzahl_bestaetigt_schluessel(material.id, 0)
                ]
            )

            bestaetige_keimzahl(material.id, 0)
            kulturdaten = baue_kulturdaten_aus_formularvorschau(material, None)

        self.assertIsNotNone(kulturdaten)
        assert kulturdaten is not None
        self.assertTrue(kulturdaten.wachstum)
        self.assertEqual(len(kulturdaten.keime), 1)
        self.assertEqual(kulturdaten.keime[0].keim_id, "Escherichia coli")
        self.assertEqual(kulturdaten.keime[0].keimzahl_code, "p5")
        self.assertEqual(kulturdaten.keime[0].rolle, "pathogen")
        self.assertEqual(fake_streamlit.fehlermeldungen, [])

    def test_beurteilung_liefert_id_und_resi_fuer_pathogenen_urin_keim(self) -> None:
        """Prueft den fachlichen Smoke-Pfad fuer die Urinbeurteilung."""
        kulturdaten = Kulturdaten(
            wachstum=True,
            keime=[
                KulturKeim(
                    keim_id="Escherichia coli",
                    keimzahl_code="p5",
                    rolle="pathogen",
                )
            ],
        )

        beurteilung = beurteile_urin_allgemeine_bakteriologie(kulturdaten)

        self.assertTrue(beurteilung.ist_gueltig)
        self.assertEqual(beurteilung.gesamtbeurteilung, ERGEBNIS_ID_RESI)
        self.assertEqual(len(beurteilung.keimbeurteilungen), 1)
        self.assertEqual(beurteilung.keimbeurteilungen[0].ergebnis, ERGEBNIS_ID_RESI)

    def test_befund_blendet_resistenzempfehlung_fuer_kontaminante_aus(self) -> None:
        """Prueft den Befundpfad fuer pathogenen und kontaminanten Keim im selben Material."""
        kulturdaten = Kulturdaten(
            wachstum=True,
            keime=[
                KulturKeim(
                    keim_id="Escherichia coli",
                    keimzahl_code="p5",
                    rolle="pathogen",
                ),
                KulturKeim(
                    keim_id="Lactobacillus spp.",
                    keimzahl_code="p5",
                    rolle="kontaminante",
                ),
            ],
        )
        material = self.baue_material(
            patient_id="patient-1",
            kulturdaten=kulturdaten,
        )
        beurteilung = UrinBeurteilung(
            gesamtbeurteilung=ERGEBNIS_ID_RESI,
            ist_gueltig=True,
            keimbeurteilungen=[
                BeurteilterKeim(
                    keim_id="Escherichia coli",
                    keimzahl_code="p5",
                    rolle="pathogen",
                    effektive_rolle="pathogen",
                    ergebnis=ERGEBNIS_ID_RESI,
                    begruendung="Ein einzelner relevanter pathogener Keim wird weiterverarbeitet.",
                ),
                BeurteilterKeim(
                    keim_id="Lactobacillus spp.",
                    keimzahl_code="p5",
                    rolle="kontaminante",
                    effektive_rolle="kontaminante",
                    ergebnis="uriflor",
                    begruendung="Kontaminationsflora ohne Resistenzempfehlung.",
                ),
            ],
        )

        keimbloecke = befund_ansicht.baue_keimbloecke(material, beurteilung)

        self.assertEqual(len(keimbloecke), 2)
        self.assertIsInstance(keimbloecke[0]["resistenzempfehlung"], str)
        self.assertIn(
            "Identifikation und Resistenztestung",
            keimbloecke[0]["resistenzempfehlung"] or "",
        )
        self.assertIsNone(keimbloecke[1]["resistenzempfehlung"])


if __name__ == "__main__":
    unittest.main()
