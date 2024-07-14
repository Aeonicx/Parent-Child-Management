# sending test email
from core.email.config import send_html_email, render_html_content


def send_activation_email(user, token):
    subject = "Activate your account"

    message_html = render_html_content(
        "core/email/templates/activate.html",
        {"first_name": user.first_name, "token": token},
    )
    send_html_email(subject=subject, body=message_html, recipient=user.email)


def send_admin_email(child_name, parent_name, admin_emails: list):
    subject = "Child added"

    message_html = render_html_content(
        "core/email/templates/child_added.html",
        {"name": child_name, "parent_name": parent_name},
    )

    for admin_email in admin_emails:
        send_html_email(subject=subject, body=message_html, recipient=admin_email)
