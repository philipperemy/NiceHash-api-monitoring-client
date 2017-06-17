from time import sleep, time

from conf import c, logger
from nicehash_api_client import NiceHashClient
from utils import send_email_notification, get_btc_usd_rate


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
        logger.debug('Email sent for subject = {}, content = {}'.format(email_subject, email_content))


def run_monitoring_tool():
    email_sender = AlertEmailSender(c.MAIL.GMAIL_USERNAME,
                                    c.MAIL.GMAIL_PASSWORD,
                                    c.MAIL.NOTIFICATION_EMAIL)

    # part online - offline
    addr = c.BITCOIN_WALLET_PUBLIC_ID
    nice_hash_client = NiceHashClient(addr)
    polling_interval_sec = 60  # 1 minute
    rig_names_to_monitor = c.RIG_HOSTNAMES
    previous_rig_statuses = [True] * len(rig_names_to_monitor)  # initial statuses
    rig_statuses = list(previous_rig_statuses)

    # part balance
    ref_fiat_currency = c.REFERENCE_FIAT_CURRENCY
    interval_between_balance_reporting_sec = 60 * 60 * 4  # in seconds
    last_balance_reporting_time = 0

    while True:
        logger.debug('run_monitoring_tool() - RUNNING')

        # PART ONLINE - OFFLINE INSPECTION
        rig_names, speeds, up_time_minutes, locations, algo_ids = nice_hash_client.get_mining_rigs()
        connected_rig_names = set(rig_names)

        for i, rig_name_to_monitor in enumerate(rig_names_to_monitor):
            if rig_name_to_monitor not in connected_rig_names:
                logger.debug('{} is down.'.format(rig_name_to_monitor))
                rig_statuses[i] = False
                if previous_rig_statuses[i] is True:
                    email_sender.send_email(email_subject='Host not connected',
                                            email_content='[{}] is down. Please check.'.format(
                                                rig_name_to_monitor))
            else:
                logger.debug('{} is connected.'.format(rig_name_to_monitor))
                rig_statuses[i] = True
                if previous_rig_statuses[i] is False:
                    email_sender.send_email(email_subject='Host successfully connected',
                                            email_content='[{}] appears to be connected. Congrats.'.format(
                                                rig_name_to_monitor))

        previous_rig_statuses = list(rig_statuses)

        # PART BALANCE
        unpaid_balance_btc = nice_hash_client.get_unpaid_balance_btc()
        price_for_one_btc_in_fiat_currency = get_btc_usd_rate(ref_fiat_currency)
        unpaid_balance_fiat = unpaid_balance_btc * price_for_one_btc_in_fiat_currency

        if (time() - last_balance_reporting_time) > interval_between_balance_reporting_sec:
            email_sender.send_email(email_subject='Unpaid Balance',
                                    email_content='Your unpaid balance is now {0:.8f} BTC ({1:.2f} {2} approx).'.format(
                                        unpaid_balance_btc, unpaid_balance_fiat, ref_fiat_currency))
            last_balance_reporting_time = time()

        logger.debug('Going to sleep for {} seconds.'.format(polling_interval_sec))
        sleep(polling_interval_sec)


if __name__ == '__main__':
    run_monitoring_tool()
