import unittest

from src.data.utils import CaptchaDodger


WRONG_PROXY = '34.23.220.102:80'
CORRECT_PROXY = '101.99.95.54:80'


class TestCaptchaDodger(unittest.TestCase):
    def setUp(self) -> None:
        self.session = CaptchaDodger({
            'https': [
                WRONG_PROXY,
                CORRECT_PROXY,
            ]
        })

    def test_proxy_update(self):
        self.assertListEqual(
            self.session.proxy_dict['https'],
            [
                CORRECT_PROXY
            ]
        )
        self.assertEqual(self.session.proxies['https'], WRONG_PROXY)

        self.session.update_proxy('https')

        self.assertFalse(self.session.proxy_dict['https'])
        self.assertEqual(self.session.proxies['https'], CORRECT_PROXY)

    def test_get(self):
        url = 'https://icanhazip.com'

        self.assertListEqual(
            self.session.proxy_dict['https'],
            [
                CORRECT_PROXY
            ]
        )
        self.assertEqual(self.session.proxies['https'], WRONG_PROXY)

        response = self.session.get(url, timeout=3)

        self.assertFalse(self.session.proxy_dict['https'])
        self.assertEqual(self.session.proxies['https'], CORRECT_PROXY)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.strip(), CORRECT_PROXY[:CORRECT_PROXY.index(':')])
