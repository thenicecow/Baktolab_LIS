"""Verwaltet Anmeldung, Registrierung und Passwortfunktionen der App."""

from __future__ import annotations

import secrets

import streamlit as st
import streamlit_authenticator as stauth

from utils.data_manager import DataManager


class LoginManager:
    """Verwaltet die Benutzerauthentisierung der Anwendung.

    Die Klasse kapselt Anmeldung, Registrierung und Sitzungsverwaltung mit
    `streamlit-authenticator`. Zugangsdaten werden über den `DataManager`
    in einer YAML-Datei gespeichert.
    """

    def __new__(cls, *args, **kwargs):
        """Liefert eine Singleton-Instanz aus dem Session State zurück."""
        if "login_manager" in st.session_state:
            return st.session_state.login_manager
        instance = super(LoginManager, cls).__new__(cls)
        st.session_state.login_manager = instance
        return instance

    def __init__(
        self,
        data_manager: DataManager = None,
        auth_credentials_file: str = "credentials.yaml",
        auth_cookie_name: str = "bmld_inf2_streamlit_app",
    ):
        """Initialisiert die Authentisierung, falls sie noch nicht aufgebaut wurde.

        Args:
            data_manager: Datenmanager für das Speichern der Zugangsdaten.
            auth_credentials_file: Dateiname für gespeicherte Zugangsdaten.
            auth_cookie_name: Name des Session-Cookies.
        """
        if hasattr(self, "authenticator"):
            return
        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(
            self.auth_credentials,
            self.auth_cookie_name,
            self.auth_cookie_key,
        )

    def _load_auth_credentials(self):
        """Lädt die gespeicherten Zugangsdaten."""
        return self.data_manager.load_app_data(
            self.auth_credentials_file,
            initial_value={"usernames": {}},
        )

    def _save_auth_credentials(self):
        """Speichert die aktuellen Zugangsdaten."""
        self.data_manager.save_app_data(
            self.auth_credentials,
            self.auth_credentials_file,
        )

    def login_register(
        self,
        login_title: str = "Anmelden",
        register_title: str = "Benutzerkonto erstellen",
    ):
        """Steuert Anmeldung und Registrierung.

        Wenn noch keine Anmeldung besteht, wird die Login-/Registrierungsseite
        angezeigt und die weitere Ausführung gestoppt. Wenn bereits eine
        Anmeldung besteht, wird in der Sidebar die Abmeldung sowie die
        Passwortänderung eingeblendet.
        """
        if st.session_state.get("authentication_status") is True:
            with st.sidebar:
                st.write(f"Angemeldet als: **{st.session_state.get('name')}**")

                self.authenticator.logout()

                st.markdown("---")
                with st.expander("Passwort zurücksetzen"):
                    try:
                        if self.authenticator.reset_password(
                            st.session_state.get("username")
                        ):
                            self._save_auth_credentials()
                            st.success("Passwort erfolgreich geändert.")
                    except Exception as e:
                        st.error(f"Fehler beim Ändern des Passworts: {e}")

        else:
            page_fn = lambda: self._login_register_page(login_title, register_title)
            pg = st.navigation([st.Page(page_fn, title="Anmelden", icon=":material/login:")])
            pg.run()
            st.stop()

    def _login_register_page(self, login_title, register_title):
        """Zeigt die Seite für Anmeldung, Registrierung und Passwort vergessen."""
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #7CABDE;
                background-image: radial-gradient(circle, rgba(255,255,255,0.2) 1px, transparent 1px);
                background-size: 15px 15px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("docs/images/BAKTOLABLOGO.jpeg", width=400)
        with col3:
            st.image("docs/images/ZHAW.png", width=500)

        login_tab, register_tab, forgot_pw_tab = st.tabs(
            (login_title, register_title, "Passwort vergessen?")
        )
        with login_tab:
            self._login()
        with register_tab:
            self._register()
        with forgot_pw_tab:
            self._forgot_password()

    def _login(self):
        """Rendert das Login-Formular und zeigt passende Statusmeldungen."""
        self.authenticator.login()
        if st.session_state["authentication_status"] is False:
            st.error("Benutzername oder Passwort ist falsch.")
        else:
            st.warning("Bitte Benutzernamen und Passwort eingeben.")

    def _register(self):
        """Rendert die Registrierung und speichert neue Zugangsdaten."""
        st.info(
            """
Das Passwort muss 8 bis 20 Zeichen lang sein und mindestens einen Grossbuchstaben,
einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen aus @$!%*?& enthalten.
"""
        )
        res = self.authenticator.register_user(captcha=False)
        if res and res[1] is not None:
            st.success(f"Benutzerkonto {res[1]} wurde erfolgreich erstellt.")
            try:
                self._save_auth_credentials()
                st.success("Zugangsdaten wurden erfolgreich gespeichert.")
            except Exception as e:
                st.error(f"Fehler beim Speichern der Zugangsdaten: {e}")

    def _forgot_password(self):
        """Rendert die Funktion zum Zurücksetzen eines Passworts.

        `streamlit-authenticator` erzeugt dabei ein neues zufälliges Passwort.
        Dieses muss danach sicher an den Benutzer übermittelt werden.
        """
        st.info(
            "Falls du dein Passwort vergessen hast, kannst du hier ein neues "
            "zufälliges Passwort erzeugen."
        )

        try:
            username, email, new_password = self.authenticator.forgot_password(
                captcha=False,
                send_email=False,
            )

            if username:
                st.success("Neues Passwort wurde erzeugt.")
                st.write(f"Benutzername: {username}")
                st.write(f"E-Mail: {email}")
                st.warning(f"Neues temporäres Passwort: {new_password}")

                try:
                    self._save_auth_credentials()
                    st.success("Neue Zugangsdaten wurden gespeichert.")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der neuen Zugangsdaten: {e}")

            elif username is False:
                st.error("Benutzername nicht gefunden.")

        except Exception as e:
            st.error(f"Fehler beim Zurücksetzen des Passworts: {e}")
