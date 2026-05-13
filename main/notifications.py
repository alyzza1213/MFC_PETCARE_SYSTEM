from django.conf import settings
from django.core.mail import EmailMessage, get_connection

def send_registration_email(user):
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return False, "SMTP credentials are missing."

    subject = "Welcome to MFC Pet Life 🐾"
    body = f"""
Hi {user.username},

Your account has been successfully created!

You can now log in using your username and password.

Thank you,
MFC Pet Life Team
"""
    try:
        connection = get_connection(timeout=settings.EMAIL_TIMEOUT)
        email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            connection=connection,
        )
        email.send()
        return True, None
    except Exception as e:
        return False, str(e)


def send_appointment_approval_email(appointment):
    subject = "Your Appointment is Approved ✅"
    body = f"""
Hi {appointment.client.username},

Your appointment on {appointment.date} at {appointment.time} has been approved!

Thank you,
MFC Pet Life Team
"""
    email = EmailMessage(subject, body, to=[appointment.client.email])
    try:
        email.send()
    except Exception as e:
        print("Appointment email error:", e)


def send_payment_confirmation_email(appointment):
    subject = "Payment Confirmed 💰"
    body = f"""
Hi {appointment.client.username},

Your payment has been successfully confirmed.

Thank you,
MFC Pet Life Team
"""
    email = EmailMessage(subject, body, to=[appointment.client.email])
    try:
        email.send()
    except Exception as e:
        print("Payment email error:", e)
