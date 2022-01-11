from datetime import datetime
from math import ceil
from multiprocessing.pool import ThreadPool
from pprint import pprint
from typing import Iterator, Tuple

import requests
from dateutil.relativedelta import relativedelta
from mongoengine import connect
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from src.data.api import get_vacancy, find_vacancies
from src.data.coverage import Coverage
from src.data.utils import DefaultArgumentParser
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


def load_and_save_vacancies_in_date_range(
        date_from: datetime,
        date_to: datetime = None,
        requests_session: requests.Session = None,
        verbose=1
) -> int:
    """
    Получает и сохраняет все вакансии за последний год

    Parameters
    ----------
    requests_session
    verbose: управляет количеством сообщений
        0 - нет сообщений,
        1 - сообщение о каждой сохраненной вакансии,
        n - сообщение о каждой n-ой сохраненной вакансии

    Returns
    -------
    Количество сохраненных вакансий
    """
    requests_session = requests_session or requests.Session()

    if not hasattr(load_and_save_vacancies_in_date_range, 'count'):
        load_and_save_vacancies_in_date_range.count = 0

    for vacancy in find_vacancies_in_date_range(
            date_from=date_from,
            date_to=date_to,
            requests_session=requests_session
    ):
        vacancy.save()

        if verbose == 1:
            print(f'Vacancy(id={vacancy.id}, published_at={vacancy.published_at})', end=' ')
            print(f'----- saved (count: {load_and_save_vacancies_in_date_range.count})')

        elif verbose > 1:
            if load_and_save_vacancies_in_date_range.count % verbose == 0 and load_and_save_vacancies_in_date_range.count:
                print('saved: ', load_and_save_vacancies_in_date_range.count)

        load_and_save_vacancies_in_date_range.count += 1

    return load_and_save_vacancies_in_date_range.count


if __name__ == '__main__':
    parser = DefaultArgumentParser(description='Загружает все вакансии за последний год')

    parser.add_argument(
        '--proxy-file',
        default='proxies.txt',
        help="Файл со строками вида ip:port (default: 'proxies.txt')"
    )

    parser.add_argument(
        '--use-proxy',
        action='store_true',
        help="Использовать прокси или нет. Необходимо указать '--proxy-file'"
    )

    parser.add_argument(
        '--verbose',
        type=int,
        default=200,
        help='Управляет количеством сообщений'
             '0 - нет сообщений, 1 - сообщение о каждой сохраненной вакансии, '
             'n - сообщение о каждой n-ой сохраненной вакансии'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Количество потоков'
    )

    args = parser.parse_args()

    connect(
        db=args.db,
        host=args.db_host,
        port=args.db_port,
    )

    if args.use_proxy:
        workers = args.workers
        pool = ThreadPool(workers)

        period = relativedelta(years=1)
        date_from = datetime.now() - period
        date_to = datetime.now()
        date_step = (date_to - date_from) / workers

        date_ranges = [
            (date_from + date_step * step, date_from + date_step * (step + 1))
            for step in range(workers)
        ]

        with open(args.proxy_file, 'r') as proxy_file:
            proxies = list(map(str.strip, proxy_file.readlines()))

        def process(tup):
            proxy, date_range = tup

            session = requests.Session()

            retry = Retry(total=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)

            session.mount('http://', adapter)
            session.mount('https://', adapter)

            session.proxies['https'] = proxy

            try:
                load_and_save_vacancies_in_date_range(
                    date_range[0],
                    date_range[1],
                    requests_session=session,
                    verbose=args.verbose
                )

            except Exception as e:
                print(e)

        pprint(list(zip(proxies, date_ranges * ceil(len(proxies) / len(date_ranges)))))

        pool.map(process, zip(proxies, date_ranges * ceil(len(proxies) / len(date_ranges))))

        pool.close()
        pool.join()

    else:
        load_and_save_vacancies_in_date_range(verbose=args.verbose)
