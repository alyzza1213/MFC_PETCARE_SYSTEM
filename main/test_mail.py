import email

from django.http import HttpResponse
from django.core.mail import send_mail
import threading

def test_email(request):
    send_mail(
        "Test Email",
        "SMTP from Django view works!",
        "Welcome!",
        "Thanks for registering sa MFC Pet Care",
        "noreply@mfcpetcare.xyz",
        ["alyzzalongboy88@gmail.com"],
        fail_silently=False,
        )
    return HttpResponse("Email sent!")



