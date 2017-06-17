from time import sleep

from conf import c, logger
from nicehash_api_client import NiceHashClient
from utils import send_email_notification


class AlertEmailSender:
    def __init__(self, gmail_user, gmail_password, target_email):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
        self.target_email = target_email

    def send_email(self, email_subject, email_content):
        send_email_notification(self.gmail_user,
                                self.gmail_password,
                                self.target_email,
                                email_content,
                                email_subject)


def run_monitoring_tool():
    email_sender = AlertEmailSender(c.MAIL.GMAIL_USERNAME,
                                    c.MAIL.GMAIL_PASSWORD,
                                    c.MAIL.NOTIFICATION_EMAIL)

    addr = c.BITCOIN_WALLET_PUBLIC_ID
    nice_hash_client = NiceHashClient(addr)
    polling_interval_sec = 600  # 1 minute
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

        sleep(polling_interval_sec)


if __name__ == '__main__':
    run_monitoring_tool()
