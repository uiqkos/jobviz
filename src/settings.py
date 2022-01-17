import pathlib

import dotenv
from pymongo import MongoClient

SRC_PATH = pathlib.Path(__file__).parent.absolute()
ROOT_PATH = pathlib.Path(__file__).parent.parent.absolute()

_dotenv_path = dotenv.find_dotenv()

DB_HOST = dotenv.get_key(_dotenv_path, 'db.host')
DB_PORT = int(dotenv.get_key(_dotenv_path, 'db.port'))
DB_NAME = dotenv.get_key(_dotenv_path, 'db.name')

MAX_DESCRIPTION_WORD_COUNT = int(dotenv.get_key(_dotenv_path, "max-description-word-count"))
MAX_NAME_WORD_COUNT = int(dotenv.get_key(_dotenv_path, "max-name-word-count"))
MAX_SPECIALIZATION_COUNT = int(dotenv.get_key(_dotenv_path, "max-specialization-count"))
MAX_KEY_SKILL_COUNT = int(dotenv.get_key(_dotenv_path, "max-key-skill-count"))
MAX_PROFESSIONALS_ROLE_COUNT = int(dotenv.get_key(_dotenv_path, "max-professionals-role-count"))
DEFAULT_CURRENCY_ID = int(dotenv.get_key(_dotenv_path, 'default-currency-id'))

db = MongoClient(
    host=DB_HOST,
    port=DB_PORT
).get_database(DB_NAME)
