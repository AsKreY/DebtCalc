import requests


class ChequeChecker:
    def __init__(self, token: str):
        self.token = token
        self.url = 'https://proverkacheka.com/api/v1/check/get'
        self.data = {'token': self.token}

    def process_cheque(self, qr_img_path: str):
        files = {'qrfile': open(qr_img_path, 'rb')}
        r = requests.post(self.url, data=self.data, files=files)
        return r.json()['data']['json']['items']
