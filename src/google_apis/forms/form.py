"""
Model a Google form using a template-driven workflow.

Includes helpers to create a form, apply batch updates, and convert
existing items from a pulled Google Form into batchUpdate requests.
"""
from __future__ import annotations
from typing import Optional
from pathlib import Path
import json

from .api_client import FormsAPIClient
from .form_template import GoogleFormTemplate


class GoogleForm:
    """
    Composed of the FormsAPIClient, FormsConfig, the FormsTemplate

    Outward facing interface for this utility
        create_and_apply()
    
    """
    def __init__(self, client: FormsAPIClient, template: GoogleFormTemplate) -> None:
        self.client = client
        self.template = template
        self.form_id: Optional[str] = None
        self.responder_uri: Optional[str] = None

    def append_items(self, requests_block: dict) -> dict:
        if not self.form_id:
            raise RuntimeError("Could not append, form not created")
        
        return self.client.batch_update(self.form_id, requests_block)
    
    def refresh(self) -> dict:
        if not self.form_id:
            raise RuntimeError("Could not append, form not created")
        
        return self.client.get_form(self.form_id)
    
    def __repr__(self) -> str:
        return f"GoogleForm(title={self.template.title!r}, form_id={self.form_id})"
    
    def create_and_apply(self) -> dict:
        metadata = self.client.create_form(self.template.title)
        self.form_id = metadata.get("formId")
        self.responder_uri = metadata.get("responderUri")

        reqs = self.template.batch_update.get("requests", [])
        if reqs:
            self.client.batch_update(self.form_id, {"requests": reqs})

        return self.client.get_form(self.form_id)
    
    @staticmethod
    def items_to_batch_requests(items: list[dict]) -> list[dict]:
        """
        Convert items forms, into the batchUpdate createItem to play nice with the Google api
        
        From the docs:
            questionItem.question.textQuestion
            questionItem.question.choiceQuestion
            questionItem.question.checkboxQuestion
            questionItem.question.dateQuestion
            questionItem.question.timeQuestion
        """
        # requests: list[dict] = []
        pass

# Demo methods for testing!
def _demo_create_from_template(template: str = None) -> None:
    """
    Create a Google form from a given template (hardcoded in json)
    :param template: The filepath with a JSON template
    
    """
    if template is None:
        raise RuntimeError("Cannot create form form template=None")

    outfile: str = "out_created_form"
    form = GoogleForm.from_registry(template)
    created_form: dict = form.create_and_apply()
    print(f"\n Form ID: {form.form_id}")

    Path(outfile).write_text(json.dumps(created_form, indent=2))
    print(f"\n Wrote form json to {outfile}")

def _demo_reverse_import(form_id: str) -> None:
    """ Get the JSON representation of a google form via their official api"""
    outfile: str = "output_imported_form_json"
    client = FormsAPIClient()
    raw_form_json = client.get_form(form_id)

    Path(outfile).write_text(json.dumps(raw_form_json, indent=2))
    print(f"\n Wrote form json to {outfile}")

if __name__ == "__main__":

    # Either choose the import or template for demo or unit testing?
    
    # 1.
    # _demo_create_from_template()

    # 2.
    # pulled_form_id: str = None # TODO: CHANGE THIS HERE
    # _demo_reverse_import(form_id=pulled_form_id)
    pass

