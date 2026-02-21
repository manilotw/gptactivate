import requests
import json
from environs import Env

env = Env()
env.read_env()

token = env.str("TOKEN_SV")
headers = {
    'Authorization': f'Bearer {token}'
}


def check_key_status(code):
    try:
        url = f'https://keys.ovh/api/v1/key/{code}/status'
        response = requests.get(url, headers=headers)

        data = response.json()
        print(data)
        
        if 'data' not in data:
            return 'invalid'
        
        status = data['data']['status']

        if status == 'available':
            return 'available'
        elif status == 'used':
            return 'used'
        elif status == 'expired':
            return 'expired'
    except Exception as e:
        return f'Something wrong!!! Please, try again later. Btw {str(e)}'
    
def activate_key(code, custom_user_token):

    try:
        url = 'https://keys.ovh/api/v1/activate'

        # Используем переданный токен или глобальный
        token_to_use = custom_user_token

        payload = {
            'key': code,
            'user_token': token_to_use
        }


        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print(data)
        if data.get('success') == False:
            if data.get('error') == 'key_not_found':
                return 'act'
            else:
                return data.get('message')
        elif data.get('success') == True:
            return 'act'
    except Exception as e:
        return f'Something wrong!!! Please, try again later. Btw {str(e)}'


      
# def activate_key(code, custom_user_token):

#     try:
#         return 'act'
#     except Exception as e:
#         return f'Something wrong!!! Please, try again later. Btw {str(e)}'



