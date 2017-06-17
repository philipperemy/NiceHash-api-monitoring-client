from mailthon import postman, email


def send_email_notification(gmail_user, gmail_password, target_email, email_content, email_subject):
    user = '{}@gmail.com'.format(gmail_user)
    p = postman(host='smtp.gmail.com', auth=(user, gmail_password))
    r = p.send(email(
        content=email_content,
        subject=email_subject,
        sender='{0} <{0}>'.format(user),
        receivers=[target_email],
    ))
    assert r.ok
