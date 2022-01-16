from abc import abstractmethod, ABC
from typing import Union

from tensorflow.keras.callbacks import History
from mongoengine import connect

from src.models.base_model import BaseModel


class BaseTrainer(ABC):
    def __init__(
            self,
            db_host: str,
            db_port: str,
            db: str
    ):
        self.db_host = db_host
        self.db_port = db_port
        self.db = db

        connect(host=db_host, port=db_port, db=db)

    @property
    @abstractmethod
    def model(self) -> BaseModel:
        pass

    @property
    @abstractmethod
    def history(self) -> History:
        pass

    @abstractmethod
    def prepare_dataset(self, limit: int = 10_000) -> 'BaseTrainer':
        pass

    @abstractmethod
    def predict_interpret(self, x, *args, **kwargs):
        pass

    @abstractmethod
    def train(self, epochs: int, verbose: int = 1, test_size: float = 0.2) -> 'BaseTrainer':
        pass

    @abstractmethod
    def save(self):
        pass
