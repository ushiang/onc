def send_email():
    from django.core.mail import send_mail

    send_mail('Sample subject', 'Great message', '', ['pukonu@gmail.com'], fail_silently=False)
