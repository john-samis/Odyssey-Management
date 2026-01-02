"""Convenience helpers for working with Google Forms templates."""


from .form import GoogleForm
from .form_template import GoogleFormTemplate
from .api_client import FormsAPIClient


GOLDEN_TEMPLATE_PATH: str = ""

def create_practice_form() -> GoogleForm:
    """
    Create and publish a fresh Google Form

    TODO: FINISH LOGIC AFTER ALL THIS BS IS DONE


    """
    template: GoogleFormTemplate = GoogleFormTemplate("Odyssey-Attendance")
    form = GoogleForm(FormsAPIClient(), template=template)
    form.create_and_apply()
    return form

def main():
    new_form = create_practice_form()

    print("Created form:")
    print(f"  title: {new_form.template.title}")
    print(f"  formId: {new_form.form_id}")
    print(f"  responderUri: {new_form.responder_uri}")


if __name__ == "__main__":
    main()
