from time import sleep

from conf import c, logger
from nicehash_api_client import NiceHashClient
from utils import send_email_notification


class AlertEmailSender:
    def __init__(self, gmail_user, gmail_password, target_email):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
        self.target_email = target_email
        self.id_emails_sent = list()

    def send_email(self, email_subject, email_content):
        email_id = email_subject + email_content
        if len(self.id_emails_sent) > 0:  # we don't want to send duplicates every time we pull.
            last_id_email_sent = self.id_emails_sent[-1]
            if last_id_email_sent == email_id:
                logger.debug('Email already sent for subject = {}, content = {}'.format(email_subject, email_content))
                return

        send_email_notification(self.gmail_user,
                                self.gmail_password,
                                self.target_email,
                                email_content,
                                email_subject)
        logger.debug('Email sent for subject = {}, content = {}'.format(email_subject, email_content))
        self.id_emails_sent.append(email_id)


def run_monitoring_tool():
    email_sender = AlertEmailSender(c.MAIL.GMAIL_USERNAME,
                                    c.MAIL.GMAIL_PASSWORD,
                                    c.MAIL.NOTIFICATION_EMAIL)

    addr = c.BITCOIN_WALLET_PUBLIC_ID
    nice_hash_client = NiceHashClient(addr)
    polling_interval_sec = 60  # 1 minute
    rig_names_to_monitor = c.RIG_HOSTNAMES

    while True:
        logger.debug('run_monitoring_tool() - RUNNING')
        rig_names, speeds, up_time_minutes, locations, algo_ids = nice_hash_client.get_mining_rigs()
        connected_rig_names = set(rig_names)

        for rig_name_to_monitor in rig_names_to_monitor:
            if rig_name_to_monitor not in connected_rig_names:
                email_sender.send_email(email_subject='Host not connected',
                                        email_content='[{}] appears not to be connected. Please check.'.format(
                                            rig_name_to_monitor))
            else:
                logger.debug('{} is connected.'.format(rig_name_to_monitor))

        logger.debug('Going to sleep for {} seconds.'.format(polling_interval_sec))
        sleep(polling_interval_sec)


if __name__ == '__main__':
    run_monitoring_tool()
