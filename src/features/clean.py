import html
import re

from mongoengine import connect

from src.data.utils import DefaultArgumentParser
from src.data.vacancy import Vacancy


def remove_html(text: str) -> str:
    tagr = re.compile('<.*?>')

    return re.sub(tagr, '', html.unescape(text))


def remove_unicode(text: str) -> str:
    return text.encode('ascii', 'ignore').decode()


if __name__ == '__main__':
    parser = DefaultArgumentParser(description='Чистка данных')

    parser.add_argument(
        '--disable-html-remover',
        action='store_true',
        help='Не убирать html из описания вакансии'
    )

    args = parser.parse_args()

    connect(
        db=args.db,
        host=args.db_host,
        port=args.db_port,
    )

    for vacancy in Vacancy.objects:
        vacancy.description = remove_html(vacancy.description)
        vacancy.save()
