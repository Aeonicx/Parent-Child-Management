from email.message import EmailMessage as BaseEmailMessage
from fastapi import HTTPException
from string import Template
import smtplib
import threading
from common.constants import (
    EMAIL_HOST,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST_USER,
    EMAIL_PORT,
)


EMAIL_HOST_SENDER = "info@parentchildmanagement.com"


class EmailMessage:
    def __init__(self, subject: str, body: str, sender: str, recipient: str):
        self.subject = subject
        self.body = body
        self.sender = sender
        self.recipient = recipient

    def create_message(self):
        msg = BaseEmailMessage()
        msg.set_content(self.body, subtype="html")
        msg["Subject"] = self.subject
        msg["From"] = self.sender
        msg["To"] = self.recipient
        return msg

    def send(self):
        msg = self.create_message()
        try:
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class EmailThread(threading.Thread):
    def __init__(self, subject, body, recipient):
        self.subject = subject
        self.recipient = recipient
        self.body = body
        threading.Thread.__init__(self)

    def run(self):
        email = EmailMessage(self.subject, self.body, EMAIL_HOST_SENDER, self.recipient)
        email.content_subtype = "html"
        max_tries = 3
        tries = 0
        while tries < max_tries:
            try:
                email.send()
                break  # exit the loop if email successfully sent
            except:
                tries += 1


def send_html_email(subject, body, recipient):
    email = EmailThread(subject, body, recipient)
    email.start()


# input variables to html file
def render_html_content(html_file, variables):
    # Read the HTML file
    with open(html_file, "r") as file:
        html_content = Template(file.read())

    # Substitute the variables in the HTML content
    return html_content.substitute(**variables)
