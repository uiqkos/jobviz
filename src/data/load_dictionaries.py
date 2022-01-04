import dotenv
import requests
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

BASE_URL = 'https://api.hh.ru/'


def get_dictionaries():
    url = BASE_URL + 'dictionaries'
    response = requests.get(url)

    if response.ok:
        for name, value in response.json().items():
            yield name, value

    else:
        raise Exception('Failed to load dictionaries from %s' % url)


def save_dictionaries(name, values, db: Database):
    db.get_collection(name).insert_many(values)


if __name__ == '__main__':
    #     get_dictionaries()
    #
    # else:
    dotenv_path = dotenv.find_dotenv()

    dbname = dotenv.get_key(dotenv_path, 'db.name')

    mc = MongoClient(
        host=dotenv.get_key(dotenv_path, 'db.host'),
        port=dotenv.get_key(dotenv_path, 'db.port'),
    )

    db = mc.get_database(dbname)

    list(
        map(save_dictionaries, get_dictionaries())
    )

