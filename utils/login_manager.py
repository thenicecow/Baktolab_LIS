import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton class that manages user authentication for the application.

    Handles user login, registration, and session management using
    streamlit-authenticator. Credentials are stored in a YAML file via
    the DataManager.
    """

    def __new__(cls, *args, **kwargs):
        """
        Singleton: returns existing instance from session state if available.

        Returns:
            LoginManager: The singleton instance, either existing or newly created.
        """
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        instance = super(LoginManager, cls).__new__(cls)
        st.session_state.login_manager = instance
        return instance

    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        """
        Initializes authentication components if not already initialized.

        Args:
            data_manager (DataManager): The DataManager instance to use for credential storage.
            auth_credentials_file (str): Filename for storing user credentials.
            auth_cookie_name (str): Cookie name for session management.
        """
        if hasattr(self, 'authenticator'):
            return
        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(
            self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key
        )

    def _load_auth_credentials(self):
        """
        Loads user credentials from the configured credentials file.

        Returns:
            dict: User credentials, defaulting to empty usernames dict if file not found.
        """
        return self.data_manager.load_app_data(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """Saves current user credentials to the credentials file."""
        self.data_manager.save_app_data(self.auth_credentials, self.auth_credentials_file)

    def login_register(self, login_title='Login', register_title='Register new user'):
        """
        Handles authentication. When not logged in, shows the login/register page
        and stops further execution. When logged in, adds the logout button to the
        sidebar and returns, allowing app.py to set up its own navigation.

        Args:
            login_title (str): Label for the login tab.
            register_title (str): Label for the registration tab.
        """
        if st.session_state.get("authentication_status") is True:
            with st.sidebar:
                st.write(f"Angemeldet als: **{st.session_state.get('name')}**")
                self.authenticator.logout()
        else:
            page_fn = lambda: self._login_register_page(login_title, register_title)
            pg = st.navigation([st.Page(page_fn, title="Login", icon=":material/login:")])
            pg.run()
            st.stop()

    def _login_register_page(self, login_title, register_title):
        """Page function shown when the user is not authenticated."""
        login_tab, register_tab, forgot_pw_tab = st.tabs(
    (login_title, register_title, "Passwort vergessen")
)
        with login_tab:
            self._login()
        with register_tab:
            self._register()
        with forgot_pw_tab:
            self._forgot_password()

    def _login(self):
        """Renders the login form and handles authentication status messages."""
        self.authenticator.login()
        if st.session_state["authentication_status"] is False:
            st.error("Username/password is incorrect")
        else:
            st.warning("Please enter your username and password")

    def _register(self):
        """
        Renders the registration form and handles user registration flow.

        Displays password requirements, processes registration attempts,
        and saves credentials on successful registration.
        """
        st.info("""
        The password must be 8-20 characters long and include at least one uppercase letter,
        one lowercase letter, one digit, and one special character from @$!%*?&.
        """)
        res = self.authenticator.register_user()
        if res[1] is not None:
            st.success(f"User {res[1]} registered successfully")
            try:
                self._save_auth_credentials()
                st.success("Credentials saved successfully")
            except Exception as e:
                st.error(f"Failed to save credentials: {e}")

    def _forgot_password(self):
        """
        Renders a forgot-password form.

        streamlit-authenticator erzeugt dabei ein neues zufälliges Passwort.
        Dieses muss danach sicher an den Benutzer übermittelt werden.
        """
        st.info(
            "Falls du dein Passwort vergessen hast, kannst du hier ein neues zufälliges Passwort erzeugen."
        )

        try:
            username, email, new_password = self.authenticator.forgot_password(
                captcha=False,
                send_email=False
            )

            if username:
                st.success("Neues Passwort wurde erzeugt.")
                st.write(f"Username: {username}")
                st.write(f"E-Mail: {email}")
                st.warning(f"Neues temporäres Passwort: {new_password}")

                try:
                    self._save_auth_credentials()
                    st.success("Neue Zugangsdaten wurden gespeichert.")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der neuen Zugangsdaten: {e}")

            elif username is False:
                st.error("Username nicht gefunden.")

        except Exception as e:
            st.error(f"Fehler beim Zurücksetzen des Passworts: {e}")
