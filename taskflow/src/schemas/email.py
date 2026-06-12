from pydantic import (
    BaseModel,
    ConfigDict,
)


class Email(BaseModel):

    message_id:  str
    from_email:  str
    subject:  str
    body_text:  str
    body_html: str | None
    processed:  bool
    error: str | None

    model_config = ConfigDict(from_attributes=True)