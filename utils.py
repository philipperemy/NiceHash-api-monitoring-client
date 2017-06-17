from forex_python.bitcoin import BtcConverter
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


def get_btc_usd_rate(currency):
    b = BtcConverter()
    return b.get_latest_price(currency)
