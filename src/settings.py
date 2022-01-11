import dotenv
from pymongo.database import Database
from pymongo import MongoClient


_dotenv_path = dotenv.find_dotenv()

db_host = dotenv.get_key(_dotenv_path, 'db.host')
db_port = int(dotenv.get_key(_dotenv_path, 'db.port'))
db_name = dotenv.get_key(_dotenv_path, 'db.name')


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
