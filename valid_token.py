import json
import base64
import time
from datetime import datetime, timezone


def check_chatgpt_session(input_data):

    try:
        # ========= PARSE =========
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
            except Exception:
                return 'INVALID_JSON'
        else:
            data = input_data

        if not isinstance(data, dict):
            return 'INVALID_FORMAT'

        user = data.get('user')
        account = data.get('account')
        access_token = data.get('accessToken')
        expires = data.get('expires')

        if not user or not access_token:
            return 'MISSING_DATA'

        if not user.get('id') or not user.get('email'):
            return 'INVALID_USER_DATA'

        # ========= DECODE JWT =========
        try:
            payload_part = access_token.split('.')[1]
            payload_part += '=' * (-len(payload_part) % 4)

            decoded = base64.urlsafe_b64decode(payload_part)
            jwt_data = json.loads(decoded)

        except Exception:
            return 'INVALID_ACCESS_TOKEN'

        # ========= CHECK JWT EXP =========
        exp = jwt_data.get('exp')

        if not exp or exp < int(time.time()):
            return 'ACCESS_TOKEN_EXPIRED'

        # ========= EXTRACT JWT =========
        jwt_auth = jwt_data.get('https://api.openai.com/auth', {})
        jwt_profile = jwt_data.get('https://api.openai.com/profile', {})

        jwt_user_id = jwt_auth.get('chatgpt_user_id')
        jwt_plan = jwt_auth.get('chatgpt_plan_type')
        jwt_email = jwt_profile.get('email')

        # ========= CONSISTENCY CHECK =========
        # if user.get('id') != jwt_user_id:
        #     return 'USER_MISMATCH'

        # if user.get('email') != jwt_email:
        #     return 'EMAIL_MISMATCH'

        if account and account.get('planType') != jwt_plan:
            return 'PLAN_MISMATCH'

        # ========= CHECK EXPIRES =========
        if expires:
            try:
                exp_time = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                if exp_time < datetime.now(timezone.utc):
                    return 'SESSION_EXPIRED'
            except Exception:
                return 'INVALID_EXPIRES_FORMAT'

        # ========= ACCOUNT =========
        if account and account.get('isDelinquent'):
            return 'ACCOUNT_PROBLEM'

        # ========= CHECK PLAN TYPE (ONLY FREE ALLOWED) =========
        if jwt_plan != 'free':
            return 'PLAN_NOT_FREE'

        # ========= RESULT =========
        return {
            'status': 'VALID',
            'user_id': user.get('id'),
            'email': user.get('email'),
            'plan': account.get('planType') if account else None,
            'expires': expires
        }

    except Exception as e:
        return f'ERROR: {str(e)}'
    
# primer = '{"user":{"id":"user-Z7ULm6XwiweqcjycVH09c32P","email":"albarievproduct@gmail.com","idp":"google-oauth2","iat":1771607651,"mfa":false},"expires":"2026-05-21T17:15:10.559Z","account":{"id":"02cdbf4f-bf3c-4128-b5e8-bee118bd6fce","planType":"free","structure":"personal","isFedrampCompliantWorkspace":false,"isConversationClassifierEnabledForWorkspace":true,"isDelinquent":false,"residencyRegion":"no_constraint","computeResidency":"no_constraint"},"accessToken":"eyJhbGciOiJSUzI1NiIsImtpZCI6IjE5MzQ0ZTY1LWJiYzktNDRkMS1hOWQwLWY5NTdiMDc5YmQwZSIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS92MSJdLCJjbGllbnRfaWQiOiJhcHBfWDh6WTZ2VzJwUTl0UjNkRTduSzFqTDVnSCIsImV4cCI6MTc3MjQ3MTY1MSwiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS9hdXRoIjp7ImNoYXRncHRfYWNjb3VudF9pZCI6IjAyY2RiZjRmLWJmM2MtNDEyOC1iNWU4LWJlZTExOGJkNmZjZSIsImNoYXRncHRfYWNjb3VudF91c2VyX2lkIjoidXNlci1aN1VMbTZYd2l3ZXFjanljVkgwOWMzMlBfXzAyY2RiZjRmLWJmM2MtNDEyOC1iNWU4LWJlZTExOGJkNmZjZSIsImNoYXRncHRfY29tcHV0ZV9yZXNpZGVuY3kiOiJub19jb25zdHJhaW50IiwiY2hhdGdwdF9wbGFuX3R5cGUiOiJmcmVlIiwiY2hhdGdwdF91c2VyX2lkIjoidXNlci1aN1VMbTZYd2l3ZXFjanljVkgwOWMzMlAiLCJpc19zaWdudXAiOnRydWUsInVzZXJfaWQiOiJ1c2VyLVo3VUxtNlh3aXdlcWNqeWNWSDA5YzMyUCJ9LCJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJhbGJhcmlldnByb2R1Y3RAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJpYXQiOjE3NzE2MDc2NTEsImlzcyI6Imh0dHBzOi8vYXV0aC5vcGVuYWkuY29tIiwianRpIjoiMWJhYWQ0NjgtMDBiNy00OTRjLTkyNWItYjM0OGU1MjdiYjUwIiwibmJmIjoxNzcxNjA3NjUxLCJwd2RfYXV0aF90aW1lIjoxNzcxNjA3NjQ4NTM2LCJzY3AiOlsib3BlbmlkIiwiZW1haWwiLCJwcm9maWxlIiwib2ZmbGluZV9hY2Nlc3MiLCJtb2RlbC5yZXF1ZXN0IiwibW9kZWwucmVhZCIsIm9yZ2FuaXphdGlvbi5yZWFkIiwib3JnYW5pemF0aW9uLndyaXRlIl0sInNlc3Npb25faWQiOiJhdXRoc2Vzc18yd0MwWTBGTTRjZzJIUHVFY2JxSTZXWFQiLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwOTU4NDQyNzkwMjUyOTc3MDUwMCJ9.Qh-h8K-g_VKL-JVUZlkIQQW55EyZP1pIEiPzaHbeZKWqRuk9dR_4AE902XbjvnWSmFyagOtNstqaOlPvuFmEeS2Ux5ctKlLBlM4L5xjf1KX6sdy0J0toDwCMndQs4WuFgCsceN6zzHwe03WqFa--YT-Ff_YhEkLOiOFOT8-ktqLAonAy_Zy6iCXks0y02SSr8jAcRjZRjnHscIK3jks2qwewi7ltUU0HlqsHHO5uCLQ7WvRVILnq1K6CgtKxhkgxSVlVGU6XkpNV8gwozUAhacmFgAef8Dyuc5gqmurjWdY_Dju7k7PyRlAgJa5BqEW0fwk_fnWgAsWB8AUbSe8Yq4FejDNB_gatR5QjjjIcFp0r56fgY6t6KEBytHkMqTLmna8EnBLwd6f3s_xlSoSAvdjOiqBXJ3ZbOn36hV3IP3-l9w8o8HaAcJLBBN5r5BPD2IsU2G5qpYNihBZB8uM3LkSeNa9CQkSaqAaodLrbCV08j0oUebW_B9uR2VTrELLaa-hnKqo93d11mCGMdPIxhMcwCNIcTaE9yqAdW3_TASjJvSh9K0Ljwzq6Ep_v-ij_K2z_FkNBCblui7xNw1uuINYI3Xv-IPzRCdNIQGNf5T6ZZ-izT3ckhIi5lHv_tNQ4vjwFAXJKPJNz-ZQhoneAfugiSgVOqsPucPh8PRWX018","authProvider":"openai","sessionToken":"eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..abEfmcYo3fcojDn6.sUbQW527nkfmkmJ8fcu9_dZT_rZV-WzIQ-Pj-MUm_57YX_BB1OjDvFD7qlCfN8xj7Qfq6qNwS3SOS3zK-kPVFLjNB1SFzUZeCyahiwkJ2zAu3bwxlpKUl4y4xWHPmGu3aNp97ANlbHbpPCL5kUaiDAVzFadMS3OuzkrbFMgu_-l4ZIu_gVz2oIp0C7boBOaeoUXPqRrc8oSgFpnGhgC4NeULD-nEydIncZl-0A2kKANbB9dFQeVVjYszdCAQWvYw7OYS1MT3COwQ6Fu5bFSYW1cXI5pp_Lkk8dn383fp4ttaXpBA4vLum6fIo3UmATuZVKzTBzb5NBwuA0vgD63G0G98n9T9B9DsyGKrUr8ZYJI7EYRD3EGGSrMcvYDTSWVU7XUGSRx-uBx4xVfqPDph11DDZT86lRG5Z7JZ9t6Ou2vUTUB6B2_J0dBpY-TcZtoZxkdYiYYlSlmVVTy-mZs7iSQKE1iSMbvdDchjM24udmb0rA0iPWBiFOSFEuLSCfcw8vDkhNaAGSYX2cAxhCNhHZenY91fNaV8o08SRa3_VN2qgkL-ShKO6waxiF5bh-aTghRHhbQqM3CK7hoAAw_6RGqGiZWYeUVsxexnEKuFnGTvCCFlFdqwLrcGysL6h322DQQEMbmi3-Nbid4Lqs8bVMfiKhfx0zV2abVCJ7OtyWmQsOwShAzm07qIHwBI_krp5nvfboBcN7Nos6b-LqsU0UqZ6xLxDPYZ-jj5Ya9US0VmsVXt6iw17l-0H6wxo8Tw29jLkWrKDjBwEtEuY9GibNijxw6N3O8PvO-BDePCKbCTAeiRPHNITQaU6sfz5vgbyYwDpAhlJ9EeK3JrNdMQP7pfByxhueX2N43FyTC0dk3tXK1cmu8glnE1T0Y1h2aHfh1-vY1GsOhwTFBWB0VUFs_hp6R2sSM1XMNF_seFe9iKq8h8ZGpVEhxcg0LeiLKYImStVVTBja9BEkdCrZIDDEo3aP0Ptb9WmIzTy7VPBPhLBRtjWbcJ5kvWR_Xar4zYsYPuPqxjlXdudYV3y2CO2TDPqPE3Q28mQQzOFPKu9eRCPzqaFupB8XPO6RMPD4iXc7IraySlfUCr0Dt_5REt8E7aQS7O48iQEnc5yM-0FSgzbdVL2_auPBHgN6d66yApgXaJCFqjAK22edW2_xWSX34FgikrHsyMJm90Tp-LSRV4-pAgGpCDTnVhpwKTkAJ8G1QFFHveuSsrs0FCcn_xVmAFQF3ILpmOu79FR2HVTMbvp8BiOTl7KeOPVUxgivf9ocSDUULCnVONCwTqIDaOPmD9ulLH1kDbY_AlxAyxHMh1jP07xgFDm_6fHhjRSwygCB6fC4cKmnFP62mcorCQjHruOw1D-iTI5snoByIAtz3cjsLP9ulbS6aEqnda5Da4yLs6Jc1GyJ1tiGPuoCnrpHYVHLfnucdp9IE7HBd_XZ8BssdDGX7d-F4bHBlanvkLN53-Fory5yvCgOoI5dCPrLhO4KxrAcylC0z_Z8mZTPkb3_zK7w0689XTVD5U2FizvDyT8XHWBJMRbeSUJWaDqi6Nz71rlqcjDowRl0fnAWJRYsCuVBtjlOJ707rpI5H5ITwmS3LzWMZerdBhjcWE4k9q_90UYwBLF7umUn9I97TUQ10jwKvpeDBUnlj0tiGlgxlpZ1cnkxhGH9wkbi7uvT-haG9YWVglMoMnNJGBY_xFyoCiQHekUOWrdpkYnVn_6Wpi5iE4UfHEkLwzMxBncHJp2R9c_itt9pSZeWThfEB4gXR9J3FrvWpHx4CRVd2v2IV1WxbgSkeSopjGGOWfzi_mDUyWE978yTpzMeTL7Ujj8zK4E4UfygNrK8RXRVQg2Uucy1kTokfZZR0HBmLTZ_hoRPq6y7meXqUrOhqrvLRpEqTCYtbBaLnhTYneZTGBtH1YRYHVSfRQn9SrQxEtaL66RqTNb7FppOeO-rpOBZk0O7r52rahetmjZiwC17jfNwDI-LYJK6j5kItYiBxWyfVSBpiXe-tHayCcuGDcKd7EUv_G799zcrz1Avvm01bWea7WmMmjIaqtzOyYPAoqdbwbjHHBsFvYOxiw3RoOQxEJWtfqI2otc_rQH9gbsEiTI8wpRQYO86LECaKNddTOTytt59BzFNcBEEF6zO4YAYbc3BFX9DuoaQTpT3SPNljm8fqsU2v9IGhg3xpHA1dfyyGbpuyJFEiJ2ylsCaF4GyWDRwDzfDkW-pbNy2GbdDJR5T_D0l1uTUqQVOyw4WXv4v31qmKmMc83PTIW6RzPrrRKCUedqTUYPrlwZNyH7F5r6f4SSKmU28CgriQ41Lbb7l1FyGte87BxdP7Dh0r0zH3-1nR95G0QZSz4e8J3srEt0BCF8Jl8n8ZEBk-wdzEIUzymlbAjZvslAJakTrBiEHH_ou8YUKL9UDyN4gEFO7IGDsB7zvPqrbz31zpteMn5LnSwetB3_LNq5PhvfamNL1SNb4_H5la20kOzGpFJAElcHe0Ve4ZCRLeesuYKj9BrBdesO0ImU9jWjylqPoqCgYOK4bmWZ2L4U5Rdi7f3xv85OavrLEsrN5292p0UMgqCo7B8zLaRt85upBQSDKL1Kd1OXhOIXfkfO9RhH8z0_vfvjpykwRimk6cxXtWwoDHH1-Re0jlAOltZ2m3sV9Jb1TRyVgKFU9gVDopEgaoNGjZ74v3gXykZLqgfSDF3RckRbdtC2rMMl6_OUcdqxb74tivsGE-42_qXNboccSztR4VtTSY2_4v41Q4GfA-hyxik8nUWLVn8lIloEgwkujTwHhBn_iM_YcHAEsmmaziD8jWBZshFn4xflzeWvjD88j-yOYRl4KARXoeQ9sn5IzW8Tf5XDlPh3AjnPeLr3zy7rJuRSOPWuU0kpIxg-eQ6bHa-nNkzxffy_q-rnXbFavnqZoQGoOpcK9cuQnjrLGHa3P8ToRYqhGcxp4sl0rkuSYJ9afdgQHe7r_wNjAbTPhRJ0dLllmPivEUBqUlCChhOVQzeyPC1Kll4YnqcV8r5WAOhA16mlT8tboezhD000vngBMhYFhwY4njRLMNzzIgn52OGpAXnrN86HySp-6nHlNSzowm6baDH_CPef6IP5DsqcKK4P_daR-soZ-tOZgvdVCH45_mH8qN_qCZ_YPNSev_xGCShAul6K-EuJE-TYox9YpUetjNemzW1-yHozPuBWQ7GVDKPRC13STSPlpm6JpAnpYC6bmej0GgqzAq2V_Hf4b_dvahBgn8MCAGYlkqepR8sOv5X3P6QM9NCd_hfYerK5ppRdra-1Fn5dWNKX4mORHJxfy6qIDLYNFc73_uF9ttW8KtKuHjdRjzJE9mcm9WE-RujbmMRECPxZBhFb4tByW_FPmO3qafwGPVvyRWS3oPrzPbQyjx-eKR_BcriZ5qgI4N16RcRV3cwtvefHGoleda_359mDsBR5S9mdFQIH7vUEngajy0bMNm_YE5far1am9E6WJqS-VLpN_SdY7sN9EfONBV6ARjXWO1RVqzDTV5tLlIzh5-3gT_DDyb57rzvbXkn7BYdHdeqaB7VJ5eix5a5Z_Huo-I0yThB0WmLgwPuGxIfDmoy3vYCT5tWrQzie1hg5Gv8BjobMyw9GWkNAyMIo8x3ro3ZrM51-IoVoefLw79LdEXxSYBCFQ.R45IuBu8trE1CafvoYTacg","rumViewTags":{"light_account":{"fetched":false}}}'
# print(check_chatgpt_session(primer))