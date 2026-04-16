from __future__ import annotations

import logging
import posixpath
from collections.abc import Sequence

from domaene import Material, Patient
from persistenz.datei_ablage import (
    baue_datenwurzel,
    ist_patientenakten_datei,
    patientenakten_dateiname,
    patientenakten_dateipfad,
)
from persistenz.json_hilfen import (
    lade_json_objekt,
    patientenakte_als_dict,
    patientenakte_aus_dict,
    speichere_json_objekt,
)
from utils.data_handler import DataHandler
from utils.data_manager import DataManager


logger = logging.getLogger(__name__)


class PatientenRepository:
    def __init__(self, data_manager: DataManager | None = None) -> None:
        self.data_manager = data_manager or DataManager()
        datenwurzel = baue_datenwurzel(self.data_manager.fs_root_folder)
        self.data_handler = DataHandler(self.data_manager.fs, datenwurzel)

    def lade_alle_patienten(self) -> list[Patient]:
        patienten: list[Patient] = []

        for dateiname in self._liste_patientendateien():
            patientenakte = self._lade_patientenakte_aus_datei(dateiname)
            if patientenakte is None:
                continue

            patient, _ = patientenakte
            patienten.append(patient)

        return sorted(
            patienten,
            key=lambda patient: (
                patient.nachname.casefold(),
                patient.vorname.casefold(),
                patient.id.casefold(),
            ),
        )

    def lade_patient_nach_id(self, patient_id: str) -> Patient | None:
        patientenakte = self.lade_patientenakte_nach_id(patient_id)
        if patientenakte is None:
            return None

        patient, _ = patientenakte
        return patient

    def lade_patientenakte_nach_id(
        self,
        patient_id: str,
    ) -> tuple[Patient, list[Material]] | None:
        dateiname = patientenakten_dateiname(patient_id)
        patientenakte = self._lade_patientenakte_aus_datei(dateiname)

        if patientenakte is None:
            return None

        patient, materialien = patientenakte
        if patient.id != patient_id.strip():
            return None

        return patient, materialien

    def speichere_neuen_patienten(self, patient: Patient) -> None:
        dateiname = patientenakten_dateipfad(patient.id)

        if self.data_handler.exists(dateiname):
            raise ValueError(f"Patient mit ID '{patient.id}' existiert bereits.")

        self._uebernehme_patient_metadaten(patient, None)
        daten = patientenakte_als_dict(patient, [])
        speichere_json_objekt(self.data_handler, dateiname, daten)

    def speichere_patient_mit_materialien(
        self,
        patient: Patient,
        materialien: Sequence[Material],
    ) -> None:
        dateiname = patientenakten_dateipfad(patient.id)

        if not self.data_handler.exists(dateiname):
            raise ValueError(f"Patient mit ID '{patient.id}' existiert noch nicht.")

        bestehende_patientenakte = self._lade_patientenakte_aus_datei(dateiname)
        if bestehende_patientenakte is None:
            raise ValueError(
                f"Die bestehende Patientenakte fuer '{patient.id}' konnte nicht gelesen werden."
            )

        bestehender_patient, bestehende_materialien = bestehende_patientenakte

        if bestehender_patient.id != patient.id:
            raise ValueError("Die geladene Patientenakte passt nicht zur uebergebenen Patienten-ID.")

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

        daten = patientenakte_als_dict(patient, materialliste)
        speichere_json_objekt(self.data_handler, dateiname, daten)

    def _liste_patientendateien(self) -> list[str]:
        try:
            eintraege = self.data_handler.filesystem.ls(self.data_handler.root_path, detail=True)
        except (FileNotFoundError, OSError):
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
        rohdaten = lade_json_objekt(self.data_handler, dateiname)
        if rohdaten is None:
            return None

        try:
            return patientenakte_aus_dict(rohdaten)
        except ValueError as exc:
            logger.warning("Patientenakte ist ungueltig (%s): %s", dateiname, exc)
            return None

    @staticmethod
    def _name_aus_listeneintrag(eintrag: object) -> str | None:
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
    def _uebernehme_patient_metadaten(
        patient: Patient,
        bestehender_patient: Patient | None,
    ) -> None:
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
        if bestehendes_material is not None:
            if material.erstellt_am is None:
                material.erstellt_am = bestehendes_material.erstellt_am

            if material.erstellt_von_user_id is None:
                material.erstellt_von_user_id = bestehendes_material.erstellt_von_user_id

        material.setze_erstellinformationen_wenn_fehlend()
