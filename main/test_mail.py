from django.http import HttpResponse
from django.core.mail import send_mail

def test_email(request):
    send_mail(
        "Test Email",
        "SMTP from Django view works!",
        "noreply@mfcpetcare.xyz",
        ["alyzzalongboy88@gmail.com"],
        fail_silently=False,
    )
    return HttpResponse("Email sent!")