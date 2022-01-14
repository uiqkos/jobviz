from dataclasses import dataclass, fields, field, Field
from operator import attrgetter
from typing import Union, Iterator, Tuple, AnyStr, Any, Dict, List

import requests

from src.data.vacancy import Vacancy


BASE_URL = 'https://api.hh.ru/'


def find_dictionaries(
        requests_session: requests.Session = None,
        **kwargs
) -> Iterator[Tuple[AnyStr, Any]]:
    """Поочередно возращает название и содержимое словарей данных"""
    requests_session = requests_session or requests.Session()

    response = requests_session.get(BASE_URL + 'dictionaries', **kwargs)

    if response.ok:
        for name, value in response.json().items():
            yield name, value

    else:
        raise Exception(f'Failed to get dictionaries from {response.url} Error: {response.text}')

    # professional_roles
    response = requests_session.get(BASE_URL + 'professional_roles', **kwargs)

    if response.ok:
        yield 'professional_roles', response.json()['categories']

    else:
        raise Exception(f'Failed to get professional_roles from {response.url} Error: {response.text}')


def get_vacancy(
        vacancy_id: str,
        wrap: bool = True,
        requests_session: requests.Session = None,
        **kwargs
) -> Union[Dict, Vacancy]:
    """
    Parameters
    ----------
    vacancy_id:
        id вакансии
    wrap:
        преобразовывать ответ в Vacancy или оставтить json (dict)
    requests_session:
        сессия, отправляющая запросы
    kwargs:
        Дополнительные параметры get запроса

    Returns
    -------
    Возращает вакансию с указанным id
    """
    requests_session = requests_session or requests.Session()

    url = BASE_URL + 'vacancies/' + vacancy_id
    response = requests_session.get(url, **kwargs)

    if response.ok:
        if wrap:
            return Vacancy(**response.json())
        return response.json()

    else:
        raise Exception(f'Failed to get vacancy from {response.url}. Error: {response.text}')


@dataclass
class VacanciesResponse:
    per_page: int
    items: List[Dict]
    page: int
    pages: int
    found: int
    clusters: Any
    arguments: Any


class DynamicVacanciesResponse(VacanciesResponse):
    """При инстанцировании поля, не входящие в VacanciesResponse, записываются в поле _extra, но обращение к ним
    происходит через __getattr__ """
    def __init__(self, **kwargs):
        self_fields = list(map(attrgetter('name'), fields(VacanciesResponse)))

        super_fields = {key: value for key, value in kwargs.items() if key in self_fields}
        super(DynamicVacanciesResponse, self).__init__(**super_fields)

        extra_keys = set(kwargs.keys()).difference(super_fields.keys())
        self._extra = dict(zip(
            extra_keys,
            map(
                kwargs.get,
                extra_keys
            )
        ))

    def __getattr__(self, item):
        if item not in self.__dict__:
            return self._extra[item]
        return self.__dict__[item]


def find_vacancies(
        wrap: bool = True,
        requests_session: requests.Session = None,
        **kwargs
) -> Union[Dict, DynamicVacanciesResponse]:
    """
    Parameters
    ----------
    wrap:
        преобразовывать ответ в VacanciesResponse или оставтить json (dict)
    requests_session:
        сессия, отправляющая запросы
    kwargs:
        дополнительные параметры get запроса

    Returns
    -------
    Возращает вакансии в виде VacanciesResponse или json
    """
    requests_session = requests_session or requests.Session()

    url = BASE_URL + 'vacancies/'
    response = requests_session.get(url, params=kwargs)

    if response.ok:
        if wrap:
            return DynamicVacanciesResponse(**response.json())
        return response.json()
    else:
        raise Exception(f'Failed to get vacancies from {response.url}. Error: {response.text}')
