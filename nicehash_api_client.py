import json

import requests


# https://www.nicehash.com/?p=api

def get_json(endpoint):
    resp = requests.get(endpoint)
    assert resp.status_code == 200
    result = json.loads(resp.content.decode('utf8').replace("'", '"'))
    assert not 'error' in result['result']
    return result


def get_location_code(loc_id):
    # 0 for EU, 1 for US, 2 for HK and 3 for JP
    if loc_id == 0:
        return 'EU'
    if loc_id == 1:
        return 'US'
    if loc_id == 2:
        return 'HK'
    if loc_id == 3:
        return 'JP'
    return 'UNKNOWN_LOCATION'


class NiceHashClient:
    def __init__(self, btc_wallet_public_addr):
        self.addr = btc_wallet_public_addr

    def get_unpaid_balance_btc(self):
        endpoint = 'https://api.nicehash.com/api?method=stats.provider&addr={}'.format(self.addr)
        result = get_json(endpoint)
        total_balance = sum([float(b['balance']) for b in result['result']['stats']])
        return total_balance

    def get_mined_currencies(self):
        endpoint = 'https://api.nicehash.com/api?method=stats.provider.ex&addr={}'.format(self.addr)
        result = get_json(endpoint)
        result = result['result']['current']
        mined_currencies = dict()
        for mined_currency in result:
            mined_currencies[mined_currency['algo']] = mined_currency['name']
        return mined_currencies

    def get_mining_rigs_for_algo(self, algo_id):
        endpoint = 'https://api.nicehash.com/api?method=stats.provider.workers&addr={}&algo={}'.format(self.addr,
                                                                                                       algo_id)
        result = get_json(endpoint)
        result = result['result']['workers']
        rig_names = [r[0] for r in result]
        speeds = [r[1]['a'] for r in result]
        up_time_minutes = [r[2] for r in result]
        locations = [get_location_code(r[5]) for r in result]
        return rig_names, speeds, up_time_minutes, locations, [algo_id] * len(rig_names)

    def get_mining_rigs(self):
        mined_currencies = self.get_mined_currencies()
        rig_names, speeds, up_time_minutes, locations, algo_ids = ([] for i in range(5))
        for algo_id in mined_currencies.keys():
            n, s, u, l, a = self.get_mining_rigs_for_algo(algo_id)
            rig_names.extend(n)
            speeds.extend(s)
            up_time_minutes.extend(u)
            locations.extend(l)
            algo_ids.extend(a)
        return rig_names, speeds, up_time_minutes, locations, algo_ids


if __name__ == '__main__':
    from conf import c

    addr = c.BITCOIN_WALLET_PUBLIC_ID
    nice_hash_client = NiceHashClient(addr)
    print('addr = {}'.format(addr))
    algo_id = '24'
    print(nice_hash_client.get_unpaid_balance_btc())
    print(nice_hash_client.get_mining_rigs_for_algo(algo_id))
    print(nice_hash_client.get_mined_currencies())
