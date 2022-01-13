from typing import Any

from pymongo import MongoClient
from pymongo.database import Database

from src import settings
from src.data.api import find_dictionaries
from src.data.utils import DefaultArgumentParser


def save_dictionary(
        collection_name: str,
        values: Any,
        db: Database,
        drop_if_exists: bool = True,
        add_real_id: bool = False
) -> None:
    """Сохраняет словарь данных в бд"""
    if drop_if_exists:
        db.drop_collection(collection_name)

    if add_real_id:
        db.get_collection(collection_name).insert_many(
            [{**data, 'real_id': i} for i, data in enumerate(values)]
        )

    else:
        db.get_collection(collection_name).insert_many(values)


if __name__ == '__main__':
    parser = DefaultArgumentParser(
        description='Загружает и сохраняет все словари данных (https://api.hh.ru/dictionaries)'
    )

    parser.add_argument(
        '--update',
        action='store_true',
        help='Не удалять коллекции если они существуют'
    )

    parser.add_argument(
        '--add-real-id',
        action='store_true',
        help='Добавить id типа int'
    )

    args = parser.parse_args()

    for name, value in find_dictionaries():
        save_dictionary(
            collection_name=name,
            values=value,
            db=MongoClient(
                host=args.db_host,
                port=args.db_port
            ).get_database(args.db),
            drop_if_exists=not args.update,
            add_real_id=args.add_real_id
        )

