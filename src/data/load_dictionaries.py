from functools import partial

import dotenv
import requests
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Any

from src.data.api import find_dictionaries
from src.env import get_db


def save_dictionary(
        collection_name: str,
        values: Any,
        db: Database,
        drop_if_exists: bool = True
) -> None:
    """Сохраняет словарь данных в бд"""
    if drop_if_exists:
        db.drop_collection(collection_name)

    db.get_collection(collection_name).insert_many(values)


if __name__ == '__main__':
    for name, value in find_dictionaries():
        save_dictionary(name, value, get_db())

