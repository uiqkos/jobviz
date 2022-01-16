import re
from typing import Dict, List

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry


class CaptchaDodger(requests.Session):
    def __init__(self, proxies: Dict[str, List] = None, verbose=True):
        super().__init__()

        self.verbose = verbose

        self.proxy_dict = dict(http=[], https=[])
        self.proxy_dict.update(proxies)

        retry = Retry(total=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)

        self.mount('http://', adapter)
        self.mount('https://', adapter)

        self.update_proxy('http')
        self.update_proxy('https')

    def update_proxy(self, protocol) -> bool:
        if self.proxy_dict[protocol]:
            self.proxies[protocol] = self.proxy_dict[protocol].pop(0)

            if self.verbose:
                print(f'Current proxy: [{protocol}] {self.proxies[protocol]}')

            return True

        return False

    def get(self, url, *args, **kwargs):
        protocol = re.findall(r'(\w+)://', url)[0]

        while True:
            try:
                response = super().get(url, *args, **kwargs)

                if not response.ok:
                    if not self.update_proxy(protocol):
                        return response

                else:
                    return response

            except Exception as e:
                if not self.update_proxy(protocol):
                    raise e

