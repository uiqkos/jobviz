import os
import pickle
from abc import ABC, abstractmethod
from typing import List

from tensorflow.keras.layers import Embedding, Layer

from src.models.base_model import BaseModel
from src.settings import ROOT_PATH


class EmbeddingModel(BaseModel, ABC):
    @property
    @abstractmethod
    def embedding(self) -> Embedding:
        pass

    @property
    @abstractmethod
    def trainable_layers(self) -> List[Layer]:
        pass

    @classmethod
    def load(cls) -> 'EmbeddingModel':
        model = cls()
        with open(cls._path.joinpath('layers.pickle'), 'rb') as f:
            layers = pickle.load(f)
            for layer in model.trainable_layers:
                layer.set_weights(layers[layer.name])

        return model

    def save(
            self,
            name,
            **kwargs
    ):
        os.makedirs(self._path, exist_ok=True)

        layers = {}

        for layer in self.trainable_layers:
            layers[layer.name] = layer.get_weights()

        with open(self._path.joinpath('layers.pickle'), 'wb') as f:
            pickle.dump(layers, f)
