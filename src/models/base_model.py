import abc
import pathlib
from typing import Optional

from tensorflow.keras import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential

from src.settings import ROOT_PATH


class BaseModel(Sequential, abc.ABC):
    _path: Optional[pathlib.Path] = None

    @classmethod
    def load(cls) -> 'BaseModel':
        return load_model(cls._path)
