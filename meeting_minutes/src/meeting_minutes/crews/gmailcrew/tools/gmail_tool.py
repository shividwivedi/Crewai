from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from .gmail_utility import authenticate_gmail ,create_draft , create_message
from agentops import record


class GmailToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    body: str = Field(..., description="The body of the email sent")

# @record("This is for the gmail draft emails")
class GmailTool(BaseTool):
    name: str = "GmailTool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = GmailToolInput

    def _run(self, body: str) -> str:
        # Implementation goes here
        try:
            service = authenticate_gmail()
            sender = "shivanidwivedi649@gmail.com"
            to = "dwivedishivani32@gmail.com"
            subject = "Meeting Minutes"
            message_text = body

            message = create_message(sender , to , subject,message_text)
            draft = create_draft(service, "me" , message)


            return f"email is send successfully ! Draft Id : {draft['id']}"
        except Exception as e:
            return (f"Error sending email: {e}")
