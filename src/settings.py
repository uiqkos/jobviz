import pathlib
from os.path import join

import dotenv
from pymongo.database import Database
from pymongo import MongoClient


SRC_PATH = pathlib.Path(__file__).parent.absolute()
ROOT_PATH = pathlib.Path(__file__).parent.parent.absolute()

_dotenv_path = dotenv.find_dotenv()

db_host = dotenv.get_key(_dotenv_path, 'db.host')
db_port = int(dotenv.get_key(_dotenv_path, 'db.port'))
db_name = dotenv.get_key(_dotenv_path, 'db.name')

MAX_DESCRIPTION_WORD_COUNT = 1200
MAX_NAME_WORD_COUNT = 30
MAX_SPECIALIZATION_COUNT = 30
MAX_KEY_SKILL_COUNT = 30
MAX_PROFESSIONALS_ROLE_COUNT = 30
DEFAULT_CURRENCY_ID = 6  # RUR

db = MongoClient(
    host=db_host,
    port=db_port
).get_database(db_name)

# def get_mongo_client() -> MongoClient:
#     return MongoClient(
#         host=db_host,
#         port=db_port
#     )
#
#
# def get_db() -> Database:
#     mc = get_mongo_client()
#     return mc.get_database(db_name)
