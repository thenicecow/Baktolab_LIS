"""Hilfsfunktionen fuer Datenverarbeitung und Aggregation im Resistenzmonitoring."""

from __future__ import annotations

from datetime import date

import pandas as pd


VERLAUF_DATEIPFAD = "resistance_data.csv"

STANDARD_SPALTEN: tuple[str, ...] = (
    "Zeitpunkt",
    "Auswertungsperiode",
    "Keim",
    "Antibiotikum",
    "Resistenzrate in %",
)

MONATSNAMEN: tuple[str, ...] = (
    "Januar",
    "Februar",
    "M\u00e4rz",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
)

MONAT_NACH_NUMMER: dict[str, int] = {
    monat: index for index, monat in enumerate(MONATSNAMEN, start=1)
}
MONAT_NACH_NUMMER["Maerz"] = 3


def hole_leeres_verlaufs_dataframe() -> pd.DataFrame:
    """Erzeugt ein leeres Verlaufs-DataFrame im erwarteten Zielformat."""
    return pd.DataFrame(columns=list(STANDARD_SPALTEN))


def hole_jahresoptionen(anzahl_jahre: int = 7, untergrenze: int = 2020) -> list[int]:
    """Liefert eine absteigende Liste sinnvoller Jahresoptionen fuer die Erfassung."""
    aktuelles_jahr = date.today().year
    fruehestes_jahr = max(untergrenze, aktuelles_jahr - anzahl_jahre + 1)
    return list(range(aktuelles_jahr, fruehestes_jahr - 1, -1))


def baue_auswertungsperiode(monat: str, jahr: int) -> str:
    """Erzeugt die textuelle Auswertungsperiode aus Monat und Jahr."""
    return f"{monat} {jahr}"


def parse_auswertungsperiode(periode: object) -> pd.Timestamp | None:
    """Wandelt eine textuelle Periode in einen Monats-Zeitstempel um."""
    if not isinstance(periode, str):
        return None

    bereinigt = periode.strip()
    if not bereinigt:
        return None

    teile = bereinigt.rsplit(" ", maxsplit=1)
    if len(teile) != 2:
        return None

    monat, jahr_text = teile
    monatsnummer = MONAT_NACH_NUMMER.get(monat)
    if monatsnummer is None:
        return None

    try:
        jahr = int(jahr_text)
        return pd.Timestamp(year=jahr, month=monatsnummer, day=1)
    except ValueError:
        return None


def normalisiere_verlaufsdaten(daten: object) -> pd.DataFrame:
    """Bereinigt gespeicherte Verlaufsdaten defensiv in ein konsistentes Tabellenformat."""
    if not isinstance(daten, pd.DataFrame):
        return hole_leeres_verlaufs_dataframe()

    df = daten.copy()

    for spalte in STANDARD_SPALTEN:
        if spalte not in df.columns:
            df[spalte] = pd.NA

    df = df.loc[:, list(STANDARD_SPALTEN)].copy()

    for textspalte in ("Zeitpunkt", "Auswertungsperiode", "Keim", "Antibiotikum"):
        df[textspalte] = df[textspalte].astype("string").fillna("").str.strip()

    df["Resistenzrate in %"] = pd.to_numeric(df["Resistenzrate in %"], errors="coerce")
    df["Periode_dt"] = pd.to_datetime(
        df["Auswertungsperiode"].apply(parse_auswertungsperiode),
        errors="coerce",
    )

    df = df[
        df["Zeitpunkt"].ne("")
        & df["Auswertungsperiode"].ne("")
        & df["Keim"].ne("")
        & df["Antibiotikum"].ne("")
        & df["Resistenzrate in %"].notna()
        & df["Periode_dt"].notna()
    ].copy()

    if df.empty:
        return hole_leeres_verlaufs_dataframe()

    df["Resistenzrate in %"] = df["Resistenzrate in %"].round(1)
    df = df.drop_duplicates(subset=list(STANDARD_SPALTEN), keep="last")
    df = df.sort_values(["Periode_dt", "Zeitpunkt", "Keim", "Antibiotikum"])
    df = df.drop(columns=["Periode_dt"])
    return df.reset_index(drop=True)


def baue_verlaufseintrag(
    zeitpunkt: str,
    auswertungsperiode: str,
    keim: str,
    antibiotikum: str,
    resistenzrate: float,
) -> pd.DataFrame:
    """Erzeugt einen neuen Verlaufsdatensatz im Zielschema."""
    return pd.DataFrame(
        {
            "Zeitpunkt": [zeitpunkt],
            "Auswertungsperiode": [auswertungsperiode],
            "Keim": [keim],
            "Antibiotikum": [antibiotikum],
            "Resistenzrate in %": [round(float(resistenzrate), 1)],
        }
    )


def baue_plot_daten(verlauf: pd.DataFrame) -> pd.DataFrame:
    """Ergaenzt normalisierte Verlaufsdaten um Hilfsspalten fuer Analysen und Charts."""
    df = normalisiere_verlaufsdaten(verlauf)
    if df.empty:
        leeres_df = df.copy()
        leeres_df["Resistenzrate_plot"] = pd.Series(dtype="float64")
        leeres_df["Periode_dt"] = pd.Series(dtype="datetime64[ns]")
        return leeres_df

    df["Resistenzrate_plot"] = pd.to_numeric(df["Resistenzrate in %"], errors="coerce")
    df["Periode_dt"] = pd.to_datetime(
        df["Auswertungsperiode"].apply(parse_auswertungsperiode),
        errors="coerce",
    )
    df = df.dropna(subset=["Resistenzrate_plot", "Periode_dt"])
    return df.sort_values(["Periode_dt", "Keim", "Antibiotikum"]).reset_index(drop=True)


def filtere_verlauf_nach_kombination(
    plot_daten: pd.DataFrame,
    keim: str,
    antibiotikum: str,
) -> pd.DataFrame:
    """Filtert vorbereitete Plot-Daten auf eine konkrete Keim-Antibiotikum-Kombination."""
    if plot_daten.empty:
        return plot_daten.copy()

    gefiltert = plot_daten[
        (plot_daten["Keim"] == keim) & (plot_daten["Antibiotikum"] == antibiotikum)
    ].copy()
    return gefiltert.sort_values("Periode_dt").reset_index(drop=True)


def berechne_verlaufskennzahlen(
    verlauf_kombination: pd.DataFrame,
) -> dict[str, float | int | str | None]:
    """Berechnet einfache Kennzahlen fuer eine ausgewaehlte Verlaufskombination."""
    if verlauf_kombination.empty:
        return {
            "anzahl_eintraege": 0,
            "letzte_rate": None,
            "durchschnitt_rate": None,
            "maximale_rate": None,
            "letzte_periode": None,
            "veraenderung_seit_start": None,
        }

    sortiert = verlauf_kombination.sort_values("Periode_dt").reset_index(drop=True)
    raten = sortiert["Resistenzrate_plot"].astype(float)
    erste_rate = float(raten.iloc[0])
    letzte_rate = float(raten.iloc[-1])

    veraenderung = None
    if len(sortiert) >= 2:
        veraenderung = round(letzte_rate - erste_rate, 1)

    return {
        "anzahl_eintraege": int(len(sortiert)),
        "letzte_rate": round(letzte_rate, 1),
        "durchschnitt_rate": round(float(raten.mean()), 1),
        "maximale_rate": round(float(raten.max()), 1),
        "letzte_periode": str(sortiert.iloc[-1]["Auswertungsperiode"]),
        "veraenderung_seit_start": veraenderung,
    }


def baue_matrixdaten(plot_daten: pd.DataFrame, keim: str) -> pd.DataFrame:
    """Aggregiert Verlaufseintraege eines Keims zu einer Matrix aus Periode und Antibiotikum."""
    if plot_daten.empty:
        return pd.DataFrame(
            columns=[
                "Auswertungsperiode",
                "Periode_dt",
                "Antibiotikum",
                "Resistenzrate_plot",
                "Resistenzrate_anzeige",
            ]
        )

    gefiltert = plot_daten[plot_daten["Keim"] == keim].copy()
    if gefiltert.empty:
        return pd.DataFrame(
            columns=[
                "Auswertungsperiode",
                "Periode_dt",
                "Antibiotikum",
                "Resistenzrate_plot",
                "Resistenzrate_anzeige",
            ]
        )

    matrix_daten = (
        gefiltert.groupby(["Auswertungsperiode", "Periode_dt", "Antibiotikum"], as_index=False)
        .agg(Resistenzrate_plot=("Resistenzrate_plot", "mean"))
        .sort_values(["Periode_dt", "Antibiotikum"])
        .reset_index(drop=True)
    )
    matrix_daten["Resistenzrate_plot"] = matrix_daten["Resistenzrate_plot"].round(1)
    matrix_daten["Resistenzrate_anzeige"] = matrix_daten["Resistenzrate_plot"].map(
        lambda wert: f"{wert:.1f}%"
    )
    return matrix_daten


def baue_kombinationsuebersicht(plot_daten: pd.DataFrame, keim: str) -> pd.DataFrame:
    """Erzeugt eine aggregierte Uebersicht aller Antibiotika fuer einen ausgewaehlten Keim."""
    if plot_daten.empty:
        return pd.DataFrame(
            columns=[
                "Antibiotikum",
                "Anzahl Messungen",
                "Letzte Periode",
                "Letzte Resistenzrate in %",
                "Durchschnittliche Resistenzrate in %",
                "Maximale Resistenzrate in %",
            ]
        )

    gefiltert = plot_daten[plot_daten["Keim"] == keim].copy()
    if gefiltert.empty:
        return pd.DataFrame(
            columns=[
                "Antibiotikum",
                "Anzahl Messungen",
                "Letzte Periode",
                "Letzte Resistenzrate in %",
                "Durchschnittliche Resistenzrate in %",
                "Maximale Resistenzrate in %",
            ]
        )

    aggregation = (
        gefiltert.groupby("Antibiotikum", as_index=False)
        .agg(
            **{
                "Anzahl Messungen": ("Resistenzrate_plot", "size"),
                "Durchschnittliche Resistenzrate in %": ("Resistenzrate_plot", "mean"),
                "Maximale Resistenzrate in %": ("Resistenzrate_plot", "max"),
            }
        )
    )

    letzte_eintraege = (
        gefiltert.sort_values(["Antibiotikum", "Periode_dt"])
        .groupby("Antibiotikum", as_index=False)
        .tail(1)
        .loc[:, ["Antibiotikum", "Auswertungsperiode", "Resistenzrate_plot"]]
        .rename(
            columns={
                "Auswertungsperiode": "Letzte Periode",
                "Resistenzrate_plot": "Letzte Resistenzrate in %",
            }
        )
    )

    uebersicht = aggregation.merge(letzte_eintraege, on="Antibiotikum", how="left")

    for spalte in (
        "Letzte Resistenzrate in %",
        "Durchschnittliche Resistenzrate in %",
        "Maximale Resistenzrate in %",
    ):
        uebersicht[spalte] = uebersicht[spalte].round(1)

    return uebersicht.sort_values(
        ["Maximale Resistenzrate in %", "Antibiotikum"],
        ascending=[False, True],
    ).reset_index(drop=True)
