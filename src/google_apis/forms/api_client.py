"""
Module for the Google REST API to programmatically create and manage the forms for Odyssey

"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession, Request


@dataclass(frozen=True)
class FormsAPIConfig:
    token_path: Path
    client_secrets_path: Path
    scopes: tuple[str,...] = field(default="https://www.googleapis.com/auth/forms.body",)


class FormsAPIClient:
    """ Responsible for the communication with the google forms API
    TODO: Google developers notes indicate that one must update the form to a published config before ppl can see it
    """
    FORMS_CREATE: str   = "https://forms.googleapis.com/v1/forms"
    FORMS_BATCH: str    = "https://forms.googleapis.com/v1/forms/{formId}:batchUpdate"
    FORMS_GET: str      = "https://forms.googleapis.com/v1/forms/{formId}"

    def __init__(self, config: FormsAPIConfig, auto_session: bool = False) -> None:
        self._cfg = config
        self._session: Optional[AuthorizedSession] = None

        if auto_session:
            self._session = self._create_session()


    def _get_credentials(self) -> Credentials:
        """ Get required creds for the Google api"""
        if self._cfg.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self._cfg.token_path), list(self._cfg.scopes))
        else:
            creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self._cfg.client_secrets_path),
                    list(self._cfg.scopes)
                )
                creds = flow.run_local_server(port=0)

            self._cfg.token_path.write_text(creds.to_json())

        return creds

    def _create_session(self) -> AuthorizedSession:
        """ Whip it up!"""
        return AuthorizedSession(self._get_credentials())
    
    @property
    def session(self) -> AuthorizedSession:
        """ Holds the current session"""
        if self._session is None:
            self._session = self._create_session()

        return self._session

    def create_form(self, title: str) -> dict:
        payload = {"info": {"title": title}}
        r = self.session.post(self.FORMS_CREATE, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def batch_update(self, form_id: str, requests_body: dict) -> dict:
        """ Fill in the body of the google form"""
        url = self.FORMS_BATCH.format(formId=form_id)
        r = self.session.post(url, json=requests_body, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_form(self, form_id: str) -> dict:
        """ get the json format of a google form"""
        r = self.session.get(self.FORMS_GET.format(formId=form_id), timeout=30)
        r.raise_for_status()
        return r.json()

    def __repr__(self) -> str:
        return f"FormsAPIClient(token={self._cfg.token_path}, secrets={self._cfg.client_secrets_path})"

    def __str__(self) -> str:
        return self.__repr__()

