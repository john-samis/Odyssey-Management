""" UTILITY to Get the form json from a given form id"""
from pathlib import Path
from src.google_apis.forms.api_client import FormsAPIClient, FormsAPIConfig


def get_google_form_json(form_id: str) -> dict:
    """
    return the JSON of an existing Google Form by ID.

    on desktop, needs the valid oauth config
    """
    client = FormsAPIClient(
        FormsAPIConfig(token_path=Path("token.json"), client_secrets_path=Path("credentials.json")),
        auto_session=True,
    )

    return client.get_form(form_id)


if __name__ == "__main__":
    FORM_ID: str = ""

    # TODO: Get it to write to a file via json dumps
    print(get_google_form_json(FORM_ID))

