import email

from django.http import HttpResponse
from django.core.mail import send_mail
import threading

def test_email(request):
    send_mail(
        "Welcome!",
        "Thanks for registering sa MFC Pet Care",
        "noreply@mfcpetcare.xyz",
        [email],
        fail_silently=True,
    )

def register(request):
    # your register logic here

    email = request.POST.get("email")

    threading.Thread(target=test_email, args=(email,)).start()

    return HttpResponse("Registered successfully!")