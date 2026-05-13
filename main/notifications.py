from django.conf import settings
from django.core.mail import EmailMessage

def send_registration_email(user):
    api_key = (settings.ANYMAIL or {}).get("BREVO_API_KEY")
    if not api_key:
        return False, "BREVO_API_KEY is not configured."

    subject = "Welcome to MFC Pet Life 🐾"
    body = f"""
Hi {user.username},

Your account has been successfully created!

You can now log in using your username and password.

Thank you,
MFC Pet Life Team
"""
    try:
        email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
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
