"""PDF-Hilfsfunktionen fuer den Download eines mikrobiologischen Befunds."""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None
    ImageDraw = None
    ImageFont = None


SEITENBREITE_PIXEL = 1240
SEITENHOEHE_PIXEL = 1754
SEITENRAND_PIXEL = 86
UNTERER_RAND_PIXEL = 76
KARTENABSTAND_PIXEL = 24
A4_AUFLOESUNG_DPI = 150

FARBE_HINTERGRUND = "#FFFFFF"
FARBE_TEXT = "#0F172A"
FARBE_SEKUNDAERER_TEXT = "#475569"
FARBE_AKZENT = "#1D4ED8"
FARBE_AKZENT_HELL = "#EFF6FF"
FARBE_RAHMEN = "#CBD5E1"
FARBE_BOX = "#F8FAFC"
FARBE_HINWEIS_BOX = "#FFF7ED"
FARBE_HINWEIS_RAHMEN = "#FDBA74"
FARBE_HINWEIS_AKZENT = "#EA580C"


@dataclass(slots=True)
class BefundPdfKeimblock:
    """Struktur fuer einen sichtbaren Keimblock im PDF-Befund."""

    ueberschrift: str
    keim: str
    keimzahl: str
    resistenzempfehlung: str | None = None
    rolle: str | None = None


@dataclass(slots=True)
class BefundPdfDaten:
    """Struktur fuer alle anzuzeigenden Inhalte eines exportierbaren Befunds."""

    titel: str
    datum: str
    patientenzeilen: list[str]
    befundzeilen: list[str]
    einleitung: str
    keimstatus: str | None = None
    keimbloecke: list[BefundPdfKeimblock] = field(default_factory=list)
    zusaetzliche_flora: str = ""
    validiert_durch: str = ""
    hinweise: list[str] = field(default_factory=list)
    ausgeschriebene_abkuerzungen: list[tuple[str, str]] = field(default_factory=list)
    logo_pfad: Path | None = None


def erstelle_befund_pdf(pdf_daten: BefundPdfDaten) -> bytes:
    """Erzeugt aus fachlichen Befunddaten eine mehrseitige PDF-Datei."""
    if Image is None or ImageDraw is None or ImageFont is None:
        raise RuntimeError("Pillow ist fuer die PDF-Erzeugung nicht verfuegbar.")

    renderer = _BefundPdfRenderer(pdf_daten)
    return renderer.render()


class _BefundPdfRenderer:
    """Kapselt Layout und Rendering des PDF-Befunds."""

    def __init__(self, pdf_daten: BefundPdfDaten) -> None:
        """Initialisiert Farben, Schriften und die erste PDF-Seite."""
        self.pdf_daten = pdf_daten
        self.seiten: list[object] = []
        self.seitennummer = 0

        self.marken_schrift = _lade_schrift(groesse=24, fett=True)
        self.titel_schrift = _lade_schrift(groesse=40, fett=True)
        self.abschnitt_schrift = _lade_schrift(groesse=22, fett=True)
        self.text_schrift = _lade_schrift(groesse=19, fett=False)
        self.text_fett_schrift = _lade_schrift(groesse=19, fett=True)
        self.fuss_schrift = _lade_schrift(groesse=15, fett=False)

        self.logo_bild = _lade_logo_bild(self.pdf_daten.logo_pfad)

        self.seite = None
        self.zeichenflaeche = None
        self.aktuelle_y_position = 0
        self._neue_seite()

    def render(self) -> bytes:
        """Rendert den vollständigen Befund und serialisiert ihn als PDF-Bytes."""
        self._zeichne_infokarten()
        self._zeichne_box_vollbreit(
            titel="Befundinhalt",
            zeilen=[self.pdf_daten.einleitung],
        )

        if self.pdf_daten.keimbloecke:
            for keimblock in self.pdf_daten.keimbloecke:
                keim_zeilen = [
                    f"Keim: {keimblock.keim}",
                    f"Keimzahl: {keimblock.keimzahl}",
                ]

                if keimblock.resistenzempfehlung:
                    keim_zeilen.append(
                        f"Resistenzempfehlung: {keimblock.resistenzempfehlung}"
                    )

                if keimblock.rolle:
                    keim_zeilen.append(f"Rolle: {keimblock.rolle}")

                self._zeichne_box_vollbreit(
                    titel=keimblock.ueberschrift,
                    zeilen=keim_zeilen,
                )
        elif self.pdf_daten.keimstatus:
            self._zeichne_box_vollbreit(
                titel="Keimstatus",
                zeilen=[self.pdf_daten.keimstatus],
            )

        self._zeichne_box_vollbreit(
            titel="Zusaetzliche Flora",
            zeilen=[self.pdf_daten.zusaetzliche_flora],
        )

        if self.pdf_daten.hinweise:
            self._zeichne_box_vollbreit(
                titel="Fachliche Hinweise",
                zeilen=self.pdf_daten.hinweise,
                boxfarbe=FARBE_HINWEIS_BOX,
                rahmenfarbe=FARBE_HINWEIS_RAHMEN,
                kopffarbe=FARBE_HINWEIS_AKZENT,
            )

        self._zeichne_box_vollbreit(
            titel="Validierung",
            zeilen=[f"Validiert durch: {self.pdf_daten.validiert_durch}"],
        )

        abkuerzungszeilen = [
            f"{code}: {bedeutung}"
            for code, bedeutung in self.pdf_daten.ausgeschriebene_abkuerzungen
        ]
        self._zeichne_box_vollbreit(
            titel="Ausgeschriebene Abkuerzungen",
            zeilen=abkuerzungszeilen,
        )

        self._zeichne_fusszeilen()

        pdf_puffer = BytesIO()
        seitenbilder = [seite.convert("RGB") for seite in self.seiten]
        erste_seite = seitenbilder[0]
        weitere_seiten = seitenbilder[1:]

        erste_seite.save(
            pdf_puffer,
            format="PDF",
            resolution=A4_AUFLOESUNG_DPI,
            save_all=True,
            append_images=weitere_seiten,
        )

        return pdf_puffer.getvalue()

    def _neue_seite(self) -> None:
        """Erzeugt eine neue PDF-Seite mit identischem Kopfbereich."""
        self.seitennummer += 1
        self.seite = Image.new(
            "RGB",
            (SEITENBREITE_PIXEL, SEITENHOEHE_PIXEL),
            FARBE_HINTERGRUND,
        )
        self.zeichenflaeche = ImageDraw.Draw(self.seite)

        self.seiten.append(self.seite)
        self._zeichne_kopfbereich()
        self.aktuelle_y_position = 290

    def _zeichne_kopfbereich(self) -> None:
        """Rendert den professionellen Kopfbereich mit Datum und Logo oder Text-Fallback."""
        assert self.zeichenflaeche is not None
        draw = self.zeichenflaeche

        draw.rounded_rectangle(
            (SEITENRAND_PIXEL, 52, SEITENBREITE_PIXEL - SEITENRAND_PIXEL, 72),
            radius=10,
            fill=FARBE_AKZENT,
        )

        draw.text(
            (SEITENRAND_PIXEL, 96),
            "Baktolab",
            font=self.marken_schrift,
            fill=FARBE_AKZENT,
        )
        draw.text(
            (SEITENRAND_PIXEL, 138),
            self.pdf_daten.titel,
            font=self.titel_schrift,
            fill=FARBE_TEXT,
        )
        draw.text(
            (SEITENRAND_PIXEL, 200),
            f"Befunddatum: {self.pdf_daten.datum}",
            font=self.text_fett_schrift,
            fill=FARBE_SEKUNDAERER_TEXT,
        )

        logo_box = (
            SEITENBREITE_PIXEL - 350,
            92,
            SEITENBREITE_PIXEL - SEITENRAND_PIXEL,
            228,
        )
        draw.rounded_rectangle(
            logo_box,
            radius=24,
            fill="#FFFFFF",
            outline=FARBE_RAHMEN,
            width=2,
        )

        if self.logo_bild is not None:
            logo = self.logo_bild.copy()
            logo.thumbnail((220, 104))
            logo_x = logo_box[0] + ((logo_box[2] - logo_box[0]) - logo.width) // 2
            logo_y = logo_box[1] + ((logo_box[3] - logo_box[1]) - logo.height) // 2

            if getattr(logo, "mode", "") == "RGBA":
                self.seite.paste(logo, (logo_x, logo_y), logo)
            else:
                self.seite.paste(logo, (logo_x, logo_y))
        else:
            draw.text(
                (logo_box[0] + 42, logo_box[1] + 46),
                "BAKTOLAB",
                font=self.abschnitt_schrift,
                fill=FARBE_AKZENT,
            )

        draw.line(
            (SEITENRAND_PIXEL, 258, SEITENBREITE_PIXEL - SEITENRAND_PIXEL, 258),
            fill=FARBE_RAHMEN,
            width=2,
        )

    def _zeichne_infokarten(self) -> None:
        """Rendert Patientendaten und Befundmetadaten als zwei ruhige Karten."""
        kartenbreite = (SEITENBREITE_PIXEL - 2 * SEITENRAND_PIXEL - KARTENABSTAND_PIXEL) // 2
        linke_x_position = SEITENRAND_PIXEL
        rechte_x_position = linke_x_position + kartenbreite + KARTENABSTAND_PIXEL
        start_y = self.aktuelle_y_position

        patientenhoehe = self._berechne_boxhoehe(kartenbreite, self.pdf_daten.patientenzeilen)
        befundhoehe = self._berechne_boxhoehe(kartenbreite, self.pdf_daten.befundzeilen)
        boxhoehe = max(patientenhoehe, befundhoehe)

        self._zeichne_box(
            x_position=linke_x_position,
            y_position=start_y,
            breite=kartenbreite,
            hoehe=boxhoehe,
            titel="Patientendaten",
            zeilen=self.pdf_daten.patientenzeilen,
        )
        self._zeichne_box(
            x_position=rechte_x_position,
            y_position=start_y,
            breite=kartenbreite,
            hoehe=boxhoehe,
            titel="Befunddaten",
            zeilen=self.pdf_daten.befundzeilen,
        )

        self.aktuelle_y_position = start_y + boxhoehe + KARTENABSTAND_PIXEL

    def _zeichne_box_vollbreit(
        self,
        titel: str,
        zeilen: list[str],
        boxfarbe: str = FARBE_BOX,
        rahmenfarbe: str = FARBE_RAHMEN,
        kopffarbe: str = FARBE_AKZENT,
    ) -> None:
        """Rendert einen vollbreiten Inhaltsblock mit automatischem Seitenumbruch."""
        breite = SEITENBREITE_PIXEL - 2 * SEITENRAND_PIXEL
        hoehe = self._berechne_boxhoehe(breite, zeilen)
        self._sorge_fuer_platz(hoehe + KARTENABSTAND_PIXEL)

        self._zeichne_box(
            x_position=SEITENRAND_PIXEL,
            y_position=self.aktuelle_y_position,
            breite=breite,
            hoehe=hoehe,
            titel=titel,
            zeilen=zeilen,
            boxfarbe=boxfarbe,
            rahmenfarbe=rahmenfarbe,
            kopffarbe=kopffarbe,
        )

        self.aktuelle_y_position += hoehe + KARTENABSTAND_PIXEL

    def _zeichne_box(
        self,
        x_position: int,
        y_position: int,
        breite: int,
        hoehe: int,
        titel: str,
        zeilen: list[str],
        boxfarbe: str = FARBE_BOX,
        rahmenfarbe: str = FARBE_RAHMEN,
        kopffarbe: str = FARBE_AKZENT,
    ) -> None:
        """Zeichnet eine einzelne Karte mit Kopfbereich und umbrechenden Textzeilen."""
        assert self.zeichenflaeche is not None
        draw = self.zeichenflaeche

        draw.rounded_rectangle(
            (x_position, y_position, x_position + breite, y_position + hoehe),
            radius=26,
            fill=boxfarbe,
            outline=rahmenfarbe,
            width=2,
        )

        kopfhoehe = 56
        draw.rounded_rectangle(
            (x_position, y_position, x_position + breite, y_position + kopfhoehe),
            radius=26,
            fill=FARBE_AKZENT_HELL if kopffarbe == FARBE_AKZENT else boxfarbe,
        )
        draw.rectangle(
            (x_position, y_position + 30, x_position + breite, y_position + kopfhoehe),
            fill=FARBE_AKZENT_HELL if kopffarbe == FARBE_AKZENT else boxfarbe,
        )
        draw.text(
            (x_position + 24, y_position + 15),
            titel,
            font=self.abschnitt_schrift,
            fill=kopffarbe,
        )

        text_y_position = y_position + 74
        text_breite = breite - 48
        zeilenhoehe = self._hole_zeilenhoehe(self.text_schrift)

        for zeile in zeilen:
            umbrochene_zeilen = self._umbreche_text(zeile, self.text_schrift, text_breite)

            for umbrochene_zeile in umbrochene_zeilen:
                draw.text(
                    (x_position + 24, text_y_position),
                    umbrochene_zeile,
                    font=self.text_schrift,
                    fill=FARBE_TEXT,
                )
                text_y_position += zeilenhoehe

            text_y_position += 6

    def _berechne_boxhoehe(self, breite: int, zeilen: list[str]) -> int:
        """Berechnet die benoetigte Kartenhoehe fuer umbrechende Inhaltszeilen."""
        text_breite = breite - 48
        zeilenhoehe = self._hole_zeilenhoehe(self.text_schrift)
        gesamtzahl_zeilen = 0

        for zeile in zeilen:
            umbrochene_zeilen = self._umbreche_text(zeile, self.text_schrift, text_breite)
            gesamtzahl_zeilen += max(1, len(umbrochene_zeilen))

        return 92 + gesamtzahl_zeilen * zeilenhoehe + max(0, len(zeilen) - 1) * 6 + 28

    def _sorge_fuer_platz(self, benoetigte_hoehe: int) -> None:
        """Fuehrt einen Seitenumbruch durch, wenn auf der aktuellen Seite kein Platz mehr ist."""
        verfuegbarer_platz = SEITENHOEHE_PIXEL - UNTERER_RAND_PIXEL - self.aktuelle_y_position
        if benoetigte_hoehe <= verfuegbarer_platz:
            return

        self._neue_seite()

    def _hole_zeilenhoehe(self, schriftart: object) -> int:
        """Liefert eine konsistente Zeilenhoehe fuer eine Schriftart."""
        assert self.zeichenflaeche is not None
        bbox = self.zeichenflaeche.textbbox((0, 0), "Ag", font=schriftart)
        return (bbox[3] - bbox[1]) + 7

    def _umbreche_text(self, text: str, schriftart: object, max_breite: int) -> list[str]:
        """Bricht Text anhand der verfuegbaren Breite sauber um."""
        assert self.zeichenflaeche is not None
        draw = self.zeichenflaeche

        bereinigter_text = text.strip()
        if not bereinigter_text:
            return ["-"]

        alle_zeilen: list[str] = []

        for absatz in bereinigter_text.splitlines():
            bereinigter_absatz = absatz.strip()
            if not bereinigter_absatz:
                alle_zeilen.append("")
                continue

            aktuelle_zeile = ""
            for wort in bereinigter_absatz.split():
                wortteile = [wort]
                if draw.textlength(wort, font=schriftart) > max_breite:
                    wortteile = self._teile_langes_wort(wort, schriftart, max_breite)

                for wortteil in wortteile:
                    testzeile = wortteil if not aktuelle_zeile else f"{aktuelle_zeile} {wortteil}"

                    if draw.textlength(testzeile, font=schriftart) <= max_breite:
                        aktuelle_zeile = testzeile
                        continue

                    if aktuelle_zeile:
                        alle_zeilen.append(aktuelle_zeile)

                    aktuelle_zeile = wortteil

            if aktuelle_zeile:
                alle_zeilen.append(aktuelle_zeile)

        return alle_zeilen or ["-"]

    def _teile_langes_wort(
        self,
        wort: str,
        schriftart: object,
        max_breite: int,
    ) -> list[str]:
        """Teilt sehr lange Woerter sicher in kleinere sichtbare Teile."""
        assert self.zeichenflaeche is not None
        draw = self.zeichenflaeche

        teile: list[str] = []
        aktueller_teil = ""

        for zeichen in wort:
            testteil = f"{aktueller_teil}{zeichen}"

            if aktueller_teil and draw.textlength(testteil, font=schriftart) > max_breite:
                teile.append(f"{aktueller_teil}-")
                aktueller_teil = zeichen
                continue

            aktueller_teil = testteil

        if aktueller_teil:
            teile.append(aktueller_teil)

        return teile or [wort]

    def _zeichne_fusszeilen(self) -> None:
        """Ergaenzt jede Seite um eine dezente Fusszeile mit Seitennummer."""
        for index, seite in enumerate(self.seiten, start=1):
            draw = ImageDraw.Draw(seite)
            fuss_text = f"Seite {index} von {len(self.seiten)}"
            textbreite = draw.textlength(fuss_text, font=self.fuss_schrift)
            x_position = SEITENBREITE_PIXEL - SEITENRAND_PIXEL - int(textbreite)
            y_position = SEITENHOEHE_PIXEL - 46

            draw.line(
                (SEITENRAND_PIXEL, y_position - 16, SEITENBREITE_PIXEL - SEITENRAND_PIXEL, y_position - 16),
                fill=FARBE_RAHMEN,
                width=1,
            )
            draw.text(
                (x_position, y_position),
                fuss_text,
                font=self.fuss_schrift,
                fill=FARBE_SEKUNDAERER_TEXT,
            )


def _lade_schrift(groesse: int, fett: bool) -> object:
    """Laedt moeglichst eine professionelle Sans-Serif-Schrift mit Fallback."""
    if ImageFont is None:
        raise RuntimeError("Pillow ist fuer die PDF-Erzeugung nicht verfuegbar.")

    kandidatpfade = (
        [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "arialbd.ttf",
            "DejaVuSans-Bold.ttf",
        ]
        if fett
        else [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "arial.ttf",
            "DejaVuSans.ttf",
        ]
    )

    for kandidatpfad in kandidatpfade:
        try:
            return ImageFont.truetype(kandidatpfad, groesse)
        except OSError:
            continue

    return ImageFont.load_default()


def _lade_logo_bild(logo_pfad: Path | None) -> object | None:
    """Laedt das Baktolab-Logo defensiv und liefert bei Problemen ``None``."""
    if Image is None or logo_pfad is None or not logo_pfad.exists():
        return None

    try:
        return Image.open(logo_pfad).convert("RGBA")
    except (OSError, ValueError):
        return None