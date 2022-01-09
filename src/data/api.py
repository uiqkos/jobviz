from typing import Union

import requests

from src.data.vacancy import Vacancy

BASE_URL = 'https://api.hh.ru/'


def get_dictionaries():
    url = BASE_URL + 'dictionaries'
    response = requests.get(url)

    if response.ok:
        for name, value in response.json().items():
            yield name, value

    else:
        raise Exception('Failed to load dictionaries from %s' % url + '. Error: %s' % response.status_code)


def get_vacancy(vacancy_id, wrap=True) -> Union[dict, Vacancy]:
    url = BASE_URL + 'vacancies/' + vacancy_id
    response = requests.get(url)

    if response.ok:
        if wrap:
            return Vacancy(**response.json())
        return response.json()

    else:
        raise Exception('Failed to get vacancy from %s' % url + '. Error: %s' % response.status_code)


def get_vacancies(wrap=True, **kwargs):
    url = BASE_URL + 'vacancies/'
    # params = '&'.join(map('='.join, kwargs.items()))
    response = requests.get(url, params=kwargs)

    if response.ok:
        pass
        # for
        # if wrap:

