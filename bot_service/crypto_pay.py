import requests
from environs import Env

env = Env()
env.read_env()

CRYPTO_TOKEN = env.str('CRYPTOBOT_TOKEN')

headers = {
    'Crypto-Pay-API-Token': CRYPTO_TOKEN
}


def create_invoice(payload, amount, asset='USDT'):
    url = 'https://pay.crypt.bot/api/createInvoice'

    data = {
        'asset': asset,
        'amount': amount,
        'description': 'Оплата товара',
        'payload': payload
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if not result.get('ok'):
        raise Exception(result)

    return result['result']


def check_invoice(invoice_id):
    url = 'https://pay.crypt.bot/api/getInvoices'

    data = {
        'invoice_ids': invoice_id
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if not result.get('ok'):
        raise Exception(result)

    return result['result']['items'][0]['status']