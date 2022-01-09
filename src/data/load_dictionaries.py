from functools import partial

import dotenv
import requests
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.data.api import get_dictionaries


def save_dictionary(name, values, db: Database, drop_if_exists=True):
    if drop_if_exists:
        db.drop_collection(name)

    db.get_collection(name).insert_many(values)


if __name__ == '__main__':
    #     get_dictionaries()
    #
    # else:
    dotenv_path = dotenv.find_dotenv()

    dbname = dotenv.get_key(dotenv_path, 'db.name')

    mc = MongoClient(
        host=dotenv.get_key(dotenv_path, 'db.host'),
        port=int(dotenv.get_key(dotenv_path, 'db.port')),
    )

    db = mc.get_database(dbname)

    for name, value in get_dictionaries():
        save_dictionary(name, value, db)

