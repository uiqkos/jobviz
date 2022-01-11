from datetime import datetime
from functools import partial
from operator import itemgetter, iadd
from typing import Iterator

import requests
from src.data.coverage import Coverage
from dateutil.relativedelta import relativedelta

from mongoengine import connect
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from src.data.api import get_vacancy, find_vacancies
from src.env import db_name
from vacancy import Vacancy


def find_vacancies_in_date_range(
        date_from: datetime,
        date_to: datetime = None,
        wrap=True,
        requests_session=None,
        **kwargs
) -> Iterator[Vacancy]:
    """
    Функция находит вакансии в диапазоне дат.
    Если найдено (found) > получено (per_page * pages), то
    происходит поиск уже по 2 диапазонам. Повторяется до тех пор пока не будут получены все
    вакансии в исходном диапазоне.

    Parameters
    ----------
    date_from: дата, которая ограничивает снизу диапазон дат публикации вакансий
    date_to: дата, которая ограничивает сверху диапазон дат публикации вакансий
    wrap: преобразовывать ответ в Vacancy или оставтить json (dict)
    requests_session
    kwargs: дополнительные параметры api.find_vacancies
    """
    requests_session = requests_session or requests.Session()
    date_to = date_to or datetime.now()

    cov = Coverage(start=date_from, end=date_to)

    if any(map(cov.is_subset, Coverage.objects)):
        print(f'{date_from} to {date_from} - skip')
        return

    params = dict(
        date_from=date_from.isoformat(),
        date_to=date_to.isoformat(),
        requests_session=requests_session,
        **kwargs
    )

    response = find_vacancies(**params)

    date_middle = date_from + (date_to - date_from) / 2

    if response.per_page * response.pages < response.found \
            and date_from < date_middle < date_to:

        for vacancy in find_vacancies_in_date_range(
                date_from, date_middle,
                wrap=wrap, requests_session=requests_session, **kwargs
        ):
            yield vacancy

        for vacancy in find_vacancies_in_date_range(
                date_middle, date_to,
                wrap=wrap, requests_session=requests_session, **kwargs
        ):
            yield vacancy

    else:
        for page in range(response.pages):
            for vacancy_dict in find_vacancies(page=page, **params).items:
                yield get_vacancy(vacancy_dict['id'], requests_session=requests_session, wrap=wrap)
        cov.save()


def load_and_save_all_vacancies(requests_session: requests.Session = None, verbose=1) -> int:
    """
    Получает и сохраняет все вакансии за последний год

    Parameters
    ----------
    requests_session
    verbose: управляет количеством сообщений
        0 - нет сообщений,
        1 - сообщение о каждой 2000ной записи,
        2 - сообщение о каждой сохраненной вакансии

    Returns
    -------
    Количество сохраненных вакансий
    """
    requests_session = requests_session or requests.Session()

    if not hasattr(load_and_save_all_vacancies, 'count'):
        load_and_save_all_vacancies.count = 0

    for vacancy in find_vacancies_in_date_range(
            date_from=datetime.now() - relativedelta(years=1),
            date_to=datetime.now(),
            requests_session=requests_session
    ):
        vacancy.save()

        if verbose == 1:
            if load_and_save_all_vacancies.count % 2000 == 0:
                print('saved: ', load_and_save_all_vacancies.count)
        elif verbose == 2:
            print(f'Vacancy(id={vacancy.id}, published_at={vacancy.published_at})', end=' ')
            print(f'----- saved (count: {load_and_save_all_vacancies.count})')

        load_and_save_all_vacancies.count += 1

    return load_and_save_all_vacancies.count


if __name__ == '__main__':
    connect(db_name)

    # Создание сессии и настройка
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Костыльный счетчик запросов
    def get(*args, **kwargs):
        get.counter += 1
        print('requests:', get.counter)
        return get.f(*args, **kwargs)


    proxy = '23.251.138.105:8080'

    session.proxies.update(dict(
        http=proxy,
        https=proxy,
        ftp=proxy,
    ))

    # get.f = session.get
    # get.counter = 0
    #
    # session.get = get

    # print(session.get('http://icanhazip.com/').text)
    print(session.get('https://api.hh.ru/vacancies').text)

    # print('saved: ', load_and_save_all_vacancies(requests_session=session, verbose=1))
    # print('requests: ', get.counter)
