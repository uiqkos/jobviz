import os
import subprocess
import threading
from datetime import datetime
from typing import Iterator

import requests
from dateutil.relativedelta import relativedelta
from mongoengine import connect

from src.data.api import get_vacancy, find_vacancies
from src.data.coverage import Coverage
from src.data.vacancy import Vacancy
from src.utils import DefaultArgumentParser
from src.data.utils import CaptchaDodger


def find_vacancies_in_date_range(
        date_from: datetime,
        date_to: datetime = None,
        wrap: bool = True,
        requests_session: requests.Session = None,
        verbose: int = 1,
        intervals: int = 2,
        **kwargs
) -> Iterator[Vacancy]:
    """
    Функция находит вакансии в диапазоне дат.
    Если найдено (found) > получено (per_page * pages), то
    происходит поиск уже по 2 диапазонам. Повторяется до тех пор пока не будут получены все
    вакансии в исходном диапазоне.

    Parameters
    ----------
    date_from:
        дата, которая ограничивает снизу диапазон дат публикации вакансий
    date_to:
        дата, которая ограничивает сверху диапазон дат публикации вакансий
    wrap:
        преобразовывать ответ в Vacancy или оставтить json (dict)
    requests_session:
        сессия, отправляющая запросы
    verbose:
        управляет количеством сообщений
        0 - нет сообщений,
        1 - сообщение о каждой сохраненной вакансии,
        n - сообщение о каждой n-ой сохраненной вакансии
    intervals:
        количество промежутков, на которые разделяется интервал дат
    kwargs:
        дополнительные параметры api.find_vacancies

    """

    requests_session = requests_session or requests.Session()
    date_to = date_to or datetime.now()

    cov = Coverage(start=date_from, end=date_to)

    if any(map(cov.is_subset, Coverage.objects)):
        if verbose:
            print(f'{date_from} to {date_from} - skip')
        return

    find_vacancies_params = dict(
        date_from=date_from.isoformat(),
        date_to=date_to.isoformat(),
        requests_session=requests_session,
        **kwargs
    )

    response = find_vacancies(**find_vacancies_params)

    if response.per_page * response.pages < response.found \
            and date_from < date_to:

        date_step = (date_to - date_from) / intervals

        date_ranges = [
            (date_from + date_step * step, date_from + date_step * (step + 1))
            for step in range(intervals)
        ]

        for date_range in date_ranges:
            for vacancy in find_vacancies_in_date_range(
                    *date_range,
                    wrap=wrap,
                    requests_session=requests_session,
                    verbose=verbose,
                    intervals=2,
                    **kwargs
            ):
                yield vacancy

    else:
        for page in range(response.pages):
            for vacancy_dict in find_vacancies(page=page, **find_vacancies_params).items:
                yield get_vacancy(vacancy_dict['id'], requests_session=requests_session, wrap=wrap)

    cov.save()


def load_vacancies(
        db_host: str,
        db_port: str,
        db: str,
        date_from: datetime,
        date_to: datetime,
        proxy: str = '',
        proxy_file: str = '',
        verbose: int = 200,
        terminals: bool = False,
        workers: int = 4
) -> None:
    """Получает и сохраняет все вакансии в диапазоне дат"""
    connect(db=db, host=db_host, port=db_port)

    kwargs = dict(date_from=date_from, date_to=date_to, verbose=verbose, intervals=workers)

    if not hasattr(load_vacancies, 'saved'):
        load_vacancies.saved = 0

    if proxy or proxy_file:
        if proxy_file != '':
            with open(proxy_file, 'r') as proxy_file:
                proxies = list(map(str.strip, proxy_file.readlines()))

            if terminals:
                date_step = (date_to - date_from) / workers

                date_ranges = [
                    (date_from + date_step * step, date_from + date_step * (step + 1))
                    for step in range(workers)
                ]

                for proxy, date_range in zip(proxies, date_ranges):
                    subprocess.call(f"C:\\Users\\uiqko\\projects\\jobviz\\venv\\Scripts\\python.exe -m "
                                    f"src.data.load_vacancies "
                                    f"--proxy-file=C:\\Users\\uiqko\\projects\\jobviz\\proxies.txt "
                                    f'--verbose={verbose} '
                                    f'--date-from={date_range[0].isoformat()} '
                                    f'--date-to={date_range[1].isoformat()}',
                                    close_fds=True, )
                return

            else:
                requests_session = CaptchaDodger({'https': proxies})

        else:
            requests_session = CaptchaDodger({'https': [proxy]})

        kwargs['requests_session'] = requests_session

    for vacancy in find_vacancies_in_date_range(**kwargs):
        vacancy.save()
        load_vacancies.saved += 1

        if verbose == 1:
            print(f'Vacancy(id={vacancy.id}, published_at={vacancy.published_at})', end=' ')
            print(f'----- saved (count: {load_vacancies.saved})')

        elif verbose > 1:
            if load_vacancies.saved % verbose == 0:
                print('saved: ', load_vacancies.saved)


if __name__ == '__main__':
    parser = DefaultArgumentParser(description='Загружает все вакансии за последний год')

    parser.add_argument(
        '--proxy-file',
        default='',
        help="Файл со строками вида ip:port"
    )

    parser.add_argument(
        '--proxy',
        default='',
        help="Прокси вида ip:port"
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
        '--date-from',
        default=(datetime.now() - relativedelta(years=1)).isoformat(),
        help='Дата, которая ограничивает снизу диапазон дат публикации вакансий'
    )

    parser.add_argument(
        '--date-to',
        default=datetime.now().isoformat(),
        help='Дата, которая ограничивает сверху диапазон дат публикации вакансий'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Количество потоков'
    )

    parser.add_argument(
        '--terminals',
        action='store_true',
        help='Запускать скрипт для каждой прокси в отдельном терминале'
    )

    args = parser.parse_args()

    load_vacancies(
        db_host=args.db_host,
        db_port=args.db_port,
        db=args.db,
        proxy=args.proxy,
        proxy_file=args.proxy_file,
        date_from=datetime.fromisoformat(args.date_from),
        date_to=datetime.fromisoformat(args.date_to),
        verbose=args.verbose,
        terminals=args.terminals,
        workers=args.workers
    )
