"""Repository fuer die zentrale Persistenz der Verlaufsdaten im Resistenzmonitoring."""

from __future__ import annotations

import logging
import posixpath

import pandas as pd

import functions.resistenzmonitoring as resistenz_daten
from persistenz.datei_ablage import (
    resistenzmonitoring_dateiname,
    resistenzmonitoring_dateipfad,
)
from persistenz.konfiguration import hole_switchdrive_data_dir
from utils.data_manager import DataManager


logger = logging.getLogger(__name__)


class ResistenzmonitoringRepository:
    """Laedt und speichert Verlaufsdaten des Resistenzmonitorings in einer zentralen JSON-Datei."""

    def __init__(self, data_manager: DataManager | None = None) -> None:
        """Initialisiert das Repository fuer den separaten Monitoring-Unterordner."""
        self.data_manager = data_manager or DataManager()
        self.verlaufsdatei = posixpath.join(
            hole_switchdrive_data_dir(),
            resistenzmonitoring_dateipfad(),
        )
        self.alte_zentrale_verlaufsdatei = posixpath.join(
            hole_switchdrive_data_dir(),
            resistenzmonitoring_dateiname(),
        )
        self.legacy_json_datei = resistenz_daten.VERLAUF_DATEIPFAD
        self.legacy_csv_datei = resistenz_daten.LEGACY_VERLAUF_DATEIPFAD

    def lade_verlaufsdaten(self) -> pd.DataFrame:
        """Laedt die gespeicherten Verlaufsdaten oder migriert Legacy-Daten defensiv."""
        verlaufsdaten = self._lade_verlaufsdaten_aus_zentraler_datei()
        if verlaufsdaten is not None:
            return verlaufsdaten

        legacy_verlaufsdaten = self._lade_verlaufsdaten_aus_legacy_dateien()
        if legacy_verlaufsdaten.empty:
            return legacy_verlaufsdaten

        try:
            self._speichere_verlaufsdaten(legacy_verlaufsdaten)
        except (OSError, TypeError, ValueError) as exc:
            logger.warning(
                "Legacy-Verlaufsdaten konnten nicht in die neue zentrale Datei uebernommen werden (%s): %s",
                self.verlaufsdatei,
                exc,
            )
        else:
            logger.info(
                "Legacy-Verlaufsdaten wurden in die neue zentrale Datei uebernommen (%s).",
                self.verlaufsdatei,
            )

        return legacy_verlaufsdaten

    def speichere_verlaufsdaten(self, verlaufsdaten: pd.DataFrame) -> pd.DataFrame:
        """Speichert normalisierte Verlaufsdaten in der zentralen JSON-Datei."""
        normalisierte_verlaufsdaten = resistenz_daten.normalisiere_verlaufsdaten(verlaufsdaten)
        self._speichere_verlaufsdaten(normalisierte_verlaufsdaten)
        return normalisierte_verlaufsdaten

    def speichere_verlaufseintrag(self, verlaufseintrag: pd.DataFrame) -> pd.DataFrame:
        """Ergaenzt einen Verlaufseintrag und speichert den gesamten Verlauf dauerhaft."""
        bestehende_verlaufsdaten = self.lade_verlaufsdaten()
        kombinierte_verlaufsdaten = pd.concat(
            [bestehende_verlaufsdaten, verlaufseintrag],
            ignore_index=True,
        )
        return self.speichere_verlaufsdaten(kombinierte_verlaufsdaten)

    def _lade_verlaufsdaten_aus_zentraler_datei(self) -> pd.DataFrame | None:
        """Laedt Verlaufsdaten aus der zentralen JSON-Datei oder ``None`` bei fehlender Datei."""
        rohdaten = self._lade_rohdaten_aus_datei(self.verlaufsdatei)
        if rohdaten is None:
            return None

        return resistenz_daten.verlaufsdaten_aus_speicherobjekt(rohdaten)

    def _lade_verlaufsdaten_aus_legacy_dateien(self) -> pd.DataFrame:
        """Laedt alte Monitoring-Dateien defensiv als Fallback."""
        for legacy_datei in (
            self.alte_zentrale_verlaufsdatei,
            self.legacy_json_datei,
            self.legacy_csv_datei,
        ):
            rohdaten = self._lade_rohdaten_aus_datei(legacy_datei)
            if rohdaten is None:
                continue

            legacy_verlaufsdaten = resistenz_daten.verlaufsdaten_aus_speicherobjekt(rohdaten)
            if not legacy_verlaufsdaten.empty:
                return legacy_verlaufsdaten

        return resistenz_daten.hole_leeres_verlaufs_dataframe()

    def _speichere_verlaufsdaten(self, verlaufsdaten: pd.DataFrame) -> None:
        """Serialisiert Verlaufsdaten und schreibt sie in die zentrale JSON-Datei."""
        speicherobjekt = resistenz_daten.verlaufsdaten_fuer_speicherung(verlaufsdaten)
        self.data_manager.save_app_data(speicherobjekt, self.verlaufsdatei)

    def _lade_rohdaten_aus_datei(self, dateipfad: str) -> object | None:
        """Laedt ein rohes Speicherobjekt ueber den DataManager defensiv."""
        try:
            return self.data_manager.load_app_data(dateipfad)
        except FileNotFoundError:
            return None
        except (OSError, TypeError, ValueError) as exc:
            logger.warning("Datei konnte nicht geladen werden (%s): %s", dateipfad, exc)
            return None