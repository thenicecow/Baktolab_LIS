"""Repository fuer zentrale Patientenpersistenz mit Legacy-Fallback beim Laden."""

from __future__ import annotations

import logging
import posixpath
from collections.abc import Sequence

from domaene import Kulturdaten, Material, Patient
from persistenz.datei_ablage import (
    baue_datenwurzel,
    ist_patientenakten_datei,
    patientendaten_dateipfad,
)
from persistenz.json_hilfen import (
    lade_json_objekt,
    patientendaten_als_dict,
    patientendaten_aus_dict,
    patientenakte_aus_dict,
    speichere_json_objekt,
)
from utils.data_handler import DataHandler
from utils.data_manager import DataManager


logger = logging.getLogger(__name__)


class PatientenRepository:
    """Laedt und speichert Patienten und Materialien in einer zentralen JSON-Datei."""

    def __init__(self, data_manager: DataManager | None = None) -> None:
        """Initialisiert das Repository fuer die konfigurierte Datenwurzel."""
        self.data_manager = data_manager or DataManager()
        datenwurzel = baue_datenwurzel(self.data_manager.fs_root_folder)
        self.data_handler = DataHandler(self.data_manager.fs, datenwurzel)
        self.patientendatei = patientendaten_dateipfad()

    def lade_alle_patienten(self) -> list[Patient]:
        """Laedt alle Patienten und sortiert sie wie bisher alphabetisch."""
        patienten = [patient for patient, _ in self._lade_patientenakten()]

        return sorted(
            patienten,
            key=lambda patient: (
                patient.nachname.casefold(),
                patient.vorname.casefold(),
                patient.id.casefold(),
            ),
        )

    def lade_patient_nach_id(self, patient_id: str) -> Patient | None:
        """Laedt einen Patienten anhand seiner ID."""
        patientenakte = self.lade_patientenakte_nach_id(patient_id)
        if patientenakte is None:
            return None

        patient, _ = patientenakte
        return patient

    def lade_patientenakte_nach_id(
        self,
        patient_id: str,
    ) -> tuple[Patient, list[Material]] | None:
        """Laedt eine Patientenakte anhand der Patienten-ID."""
        patient_id_bereinigt = self._bereinige_patient_id(patient_id)
        if patient_id_bereinigt is None:
            return None

        for patient, materialien in self._lade_patientenakten():
            if patient.id == patient_id_bereinigt:
                return patient, materialien

        return None

    def lade_materialkontext_nach_id(
        self,
        material_id: str,
    ) -> tuple[Patient, Material, list[Material]] | None:
        """Laedt Patient, Material und Materialliste anhand einer Material-ID."""
        material_id_bereinigt = self._bereinige_material_id(material_id)
        if material_id_bereinigt is None:
            return None

        for patient, materialien in self._lade_patientenakten():
            for material in materialien:
                if material.id == material_id_bereinigt:
                    return patient, material, materialien

        return None

    def speichere_neuen_patienten(self, patient: Patient) -> None:
        """Speichert einen neuen Patienten in der zentralen JSON-Datei."""
        patientenakten = self._lade_patientenakten()

        for bestehender_patient, _ in patientenakten:
            if bestehender_patient.id == patient.id:
                raise ValueError(f"Patient mit ID '{patient.id}' existiert bereits.")

        self._uebernehme_patient_metadaten(patient, None)
        patientenakten.append((patient, []))
        self._speichere_patientenakten(patientenakten)

    def speichere_patient_mit_materialien(
        self,
        patient: Patient,
        materialien: Sequence[Material],
    ) -> None:
        """Aktualisiert einen bestehenden Patienten mitsamt seiner Materialliste."""
        patientenakten = self._lade_patientenakten()

        ziel_index: int | None = None
        bestehender_patient: Patient | None = None
        bestehende_materialien: list[Material] = []

        for index, (vorhandener_patient, vorhandene_materialien) in enumerate(patientenakten):
            if vorhandener_patient.id == patient.id:
                ziel_index = index
                bestehender_patient = vorhandener_patient
                bestehende_materialien = vorhandene_materialien
                break

        if ziel_index is None or bestehender_patient is None:
            raise ValueError(f"Patient mit ID '{patient.id}' existiert noch nicht.")

        self._uebernehme_patient_metadaten(patient, bestehender_patient)

        bestehende_materialien_nach_id = {
            material.id: material for material in bestehende_materialien
        }

        materialliste = list(materialien)
        for material in materialliste:
            if material.patient_id != patient.id:
                raise ValueError(
                    f"Material '{material.id}' verweist nicht auf Patient '{patient.id}'."
                )

            bestehendes_material = bestehende_materialien_nach_id.get(material.id)
            self._uebernehme_material_metadaten(material, bestehendes_material)

        patientenakten[ziel_index] = (patient, materialliste)
        self._speichere_patientenakten(patientenakten)

    def speichere_kulturdaten_fuer_material(
        self,
        material_id: str,
        kulturdaten: Kulturdaten,
    ) -> tuple[Patient, Material] | None:
        """Speichert Kulturdaten gezielt beim passenden Material."""
        material_id_bereinigt = self._bereinige_material_id(material_id)
        if material_id_bereinigt is None:
            return None

        materialkontext = self.lade_materialkontext_nach_id(material_id_bereinigt)
        if materialkontext is None:
            return None

        patient, _zielmaterial, materialien = materialkontext
        aktualisierte_materialien: list[Material] = []
        gespeichertes_material: Material | None = None

        for material in materialien:
            if material.id == material_id_bereinigt:
                material.kulturdaten = kulturdaten
                gespeichertes_material = material

            aktualisierte_materialien.append(material)

        if gespeichertes_material is None:
            return None

        self.speichere_patient_mit_materialien(patient, aktualisierte_materialien)
        return patient, gespeichertes_material

    def _lade_patientenakten(self) -> list[tuple[Patient, list[Material]]]:
        """Laedt Patientenakten aus der zentralen Datei oder faellt auf Legacy-Dateien zurueck."""
        patientenakten = self._lade_patientenakten_aus_zentraler_datei()
        if patientenakten is not None:
            return patientenakten

        return self._lade_patientenakten_aus_legacy_dateien()

    def _lade_patientenakten_aus_zentraler_datei(
        self,
    ) -> list[tuple[Patient, list[Material]]] | None:
        """Laedt Patientenakten aus der zentralen Datei oder ``None`` bei fehlender Datei."""
        rohdaten = lade_json_objekt(self.data_handler, self.patientendatei)
        if rohdaten is None:
            return None

        try:
            return patientendaten_aus_dict(rohdaten)
        except ValueError as exc:
            logger.warning(
                "Zentrale Patientendatei ist ungueltig (%s): %s",
                self.patientendatei,
                exc,
            )
            return None

    def _lade_patientenakten_aus_legacy_dateien(self) -> list[tuple[Patient, list[Material]]]:
        """Laedt alte Einzeldateien defensiv als Fallback."""
        patientenakten: list[tuple[Patient, list[Material]]] = []

        for dateiname in self._liste_patientendateien():
            patientenakte = self._lade_patientenakte_aus_datei(dateiname)
            if patientenakte is None:
                continue

            patientenakten.append(patientenakte)

        return patientenakten

    def _speichere_patientenakten(
        self,
        patientenakten: Sequence[tuple[Patient, Sequence[Material]]],
    ) -> None:
        """Schreibt alle Patientenakten in die zentrale JSON-Datei."""
        daten = patientendaten_als_dict(patientenakten)
        speichere_json_objekt(self.data_handler, self.patientendatei, daten)

    def _liste_patientendateien(self) -> list[str]:
        """Liest die Legacy-Einzeldateien der Patientenakten aus der Datenwurzel."""
        if not self._datenwurzel_verfuegbar():
            return []

        try:
            eintraege = self.data_handler.filesystem.ls(self.data_handler.root_path, detail=True)
        except (FileNotFoundError, OSError, ValueError) as exc:
            logger.warning("Datenverzeichnis konnte nicht gelesen werden: %s", exc)
            return []

        dateinamen: list[str] = []

        for eintrag in eintraege:
            voller_name = self._name_aus_listeneintrag(eintrag)
            if not voller_name:
                continue

            dateiname = posixpath.basename(voller_name)
            if ist_patientenakten_datei(dateiname):
                dateinamen.append(dateiname)

        return sorted(set(dateinamen))

    def _lade_patientenakte_aus_datei(
        self,
        dateiname: str,
    ) -> tuple[Patient, list[Material]] | None:
        """Laedt und validiert eine Legacy-Einzeldatei einer Patientenakte."""
        rohdaten = lade_json_objekt(self.data_handler, dateiname)
        if rohdaten is None:
            return None

        try:
            return patientenakte_aus_dict(rohdaten)
        except ValueError as exc:
            logger.warning("Patientenakte ist ungueltig (%s): %s", dateiname, exc)
            return None

    def _datenwurzel_verfuegbar(self) -> bool:
        """Prueft, ob die konfigurierte Datenwurzel erreichbar ist."""
        try:
            return self.data_handler.filesystem.exists(self.data_handler.root_path)
        except (FileNotFoundError, OSError, ValueError):
            return False

    @staticmethod
    def _name_aus_listeneintrag(eintrag: object) -> str | None:
        """Extrahiert einen Dateinamen aus einem Filesystem-Listeneintrag."""
        if isinstance(eintrag, dict):
            eintragstyp = str(eintrag.get("type", "")).lower()
            if eintragstyp and eintragstyp != "file":
                return None

            name = eintrag.get("name")
            if name is None:
                return None

            return str(name)

        if isinstance(eintrag, str):
            return eintrag

        return None

    @staticmethod
    def _bereinige_patient_id(patient_id: str | None) -> str | None:
        """Bereinigt eine optionale Patienten-ID fuer Suchzugriffe."""
        if not isinstance(patient_id, str):
            return None

        bereinigt = patient_id.strip()
        return bereinigt or None

    @staticmethod
    def _bereinige_material_id(material_id: str | None) -> str | None:
        """Bereinigt eine optionale Material-ID fuer Suchzugriffe."""
        if not isinstance(material_id, str):
            return None

        bereinigt = material_id.strip()
        return bereinigt or None

    @staticmethod
    def _uebernehme_patient_metadaten(
        patient: Patient,
        bestehender_patient: Patient | None,
    ) -> None:
        """Ergaenzt fehlende Erstellmetadaten eines Patienten aus bestehenden Daten."""
        if bestehender_patient is not None:
            if patient.erstellt_am is None:
                patient.erstellt_am = bestehender_patient.erstellt_am

            if patient.erstellt_von_user_id is None:
                patient.erstellt_von_user_id = bestehender_patient.erstellt_von_user_id

        patient.setze_erstellinformationen_wenn_fehlend()

    @staticmethod
    def _uebernehme_material_metadaten(
        material: Material,
        bestehendes_material: Material | None,
    ) -> None:
        """Ergaenzt fehlende Erstellmetadaten eines Materials aus bestehenden Daten."""
        if bestehendes_material is not None:
            if material.erstellt_am is None:
                material.erstellt_am = bestehendes_material.erstellt_am

            if material.erstellt_von_user_id is None:
                material.erstellt_von_user_id = bestehendes_material.erstellt_von_user_id

        material.setze_erstellinformationen_wenn_fehlend()
