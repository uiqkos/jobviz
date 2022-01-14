from typing import Any

from pymongo import MongoClient
from pymongo.database import Database

from src.data.api import find_dictionaries
from src.utils import DefaultArgumentParser


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


def load_dictionaries(
        db_host: str,
        db_port: str,
        db: str,
        update: bool = False,
        add_real_id: bool = False
):
    """Сохраняет все словари данных в бд"""
    for name, value in find_dictionaries():
        save_dictionary(
            collection_name=name,
            values=value,
            db=MongoClient(
                host=db_host,
                port=db_port
            ).get_database(db),
            drop_if_exists=not update,
            add_real_id=add_real_id
        )


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

    load_dictionaries(
        db_host=args.db_host,
        db_port=args.db_port,
        db=args.db,
        update=args.update,
        add_real_id=args.add_real_id
    )

