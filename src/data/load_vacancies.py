import os
import threading
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta
from mongoengine import connect

from src.data.api import get_vacancy, find_vacancies
from src.data.coverage import Coverage
from src.data.utils import DefaultArgumentParser, CaptchaDodger


def load_and_save_vacancies_in_date_range(
        date_from: datetime,
        date_to: datetime = None,
        wrap=True,
        requests_session=None,
        verbose: int = 1,
        workers: int = 1,
        multithread: bool = False,
        **kwargs
) -> None:
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
    workers:
        количество потоков для 1 деления интервала дат
    kwargs:
        дополнительные параметры api.find_vacancies

    """

    requests_session = requests_session or requests.Session()
    date_to = date_to or datetime.now()

    if not hasattr(load_and_save_vacancies_in_date_range, 'saved'):
        load_and_save_vacancies_in_date_range.saved = 0

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

        date_step = (date_to - date_from) / workers

        date_ranges = [
            (date_from + date_step * step, date_from + date_step * (step + 1))
            for step in range(workers)
        ]

        for date_range in date_ranges:
            print(date_range)
            args_ = date_range
            kwargs_ = dict(
                verbose=verbose,
                workers=2, wrap=wrap, multithread=False,
                requests_session=requests_session, **kwargs
            )

            if multithread:
                thread = threading.Thread(
                    target=load_and_save_vacancies_in_date_range,
                    args=args_, kwargs=kwargs_
                )

                thread.start()
                # thread.join()

            else:
                load_and_save_vacancies_in_date_range(*args_, **kwargs_)

    else:
        for page in range(response.pages):
            for vacancy_dict in find_vacancies(page=page, **find_vacancies_params).items:
                vacancy = get_vacancy(vacancy_dict['id'], requests_session=requests_session, wrap=wrap)
                vacancy.save()

                load_and_save_vacancies_in_date_range.saved += 1

                if verbose == 1:
                    print(f'Vacancy(id={vacancy.id}, published_at={vacancy.published_at})', end=' ')
                    print(f'----- saved (count: {load_and_save_vacancies_in_date_range.saved})')

                elif verbose > 1:
                    if load_and_save_vacancies_in_date_range.saved % verbose == 0:
                        print('saved: ', load_and_save_vacancies_in_date_range.saved)

    cov.save()


def main(db_host, db_port, db, proxy, proxy_file, **kwargs):
    connect(
        db=db,
        host=db_host,
        port=db_port,
    )

    if proxy or proxy_file:
        if proxy_file != '':
            with open(proxy_file, 'r') as proxy_file:
                proxies = list(map(str.strip, proxy_file.readlines()))

            # load_and_save_vacancies_in_date_range(
            #     requests_session=CaptchaDodger({'https': proxies}),
            #     **kwargs
            # )

            if kwargs['terminals']:

                date_to, date_from, workers = kwargs['date_to'], kwargs['date_from'], kwargs['workers']

                date_step = (date_to - date_from) / workers

                date_ranges = [
                    (date_from + date_step * step, date_from + date_step * (step + 1))
                    for step in range(workers)
                ]

                for proxy, date_range in zip(proxies, date_ranges):
                    os.system(f"C:\\Users\\uiqko\\projects\\jobviz\\venv\\Scripts\\python.exe -m "
                              f"src.data.load_vacancies "
                              f"--proxy-file=C:\\Users\\uiqko\\projects\\jobviz\\proxies.txt "
                              # f'--proxy={proxy} '
                              f'--date-from={date_range[0].isoformat()} '
                              f'--date-to={date_range[1].isoformat()}',
                              # close_fds=True,
                              # stdin=None, stdout=None, stderr=None,
                              # creationflags=subprocess.CREATE_NEW_CONSOLE
                              )
            else:
                load_and_save_vacancies_in_date_range(
                    requests_session=CaptchaDodger({'https': proxies}),
                    **kwargs
                )

        else:
            load_and_save_vacancies_in_date_range(
                requests_session=CaptchaDodger({'https': [proxy]}),
                **kwargs
            )

    else:
        load_and_save_vacancies_in_date_range(**kwargs)


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

    main(db_host=args.db_host,
         db_port=args.db_port,
         db=args.db,
         date_from=datetime.fromisoformat(args.date_from),
         date_to=datetime.fromisoformat(args.date_to),
         verbose=args.verbose,
         workers=args.workers,
         proxy=args.proxy,
         terminals=args.terminals,
         proxy_file=args.proxy_file)
