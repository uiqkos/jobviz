import os
import os
import pickle
from typing import List

import tensorflow as tf
from keras.layers import Flatten
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling1D, Input
from tensorflow.python.keras.engine.base_layer import Layer
from tensorflow.python.keras.layers import Embedding

from src.features.preprocessing import get_embedding, get_text_vectorization
from src.models.base_model import BaseModel
from src.models.embedding_model import EmbeddingModel
from src.settings import ROOT_PATH


class BasicModel(EmbeddingModel):
    """Простая модель для предсказания средней зарплаты по описанию"""
    _path = ROOT_PATH.joinpath('models', 'basic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._vectorize_layer = get_text_vectorization()
        self._embedding = get_embedding()

        self._trainable_layers = [
            Flatten(),
            Dense(5_000, activation='leaky_relu'),
            Dropout(.5),
            Dense(1_000, activation='leaky_relu'),
            Dropout(.5),
            Dense(500, activation='leaky_relu'),
            Dropout(.5),
            Dense(100, activation='leaky_relu'),
            Dropout(.5),
            Dense(1, activation='sigmoid'),
        ]

        self.initialize_layers()

    @property
    def embedding(self) -> Embedding:
        return self._embedding

    @property
    def trainable_layers(self) -> List[Layer]:
        return self._trainable_layers

    def initialize_layers(self):
        self.add(Input(shape=(1,), dtype=tf.string))
        self.add(self._vectorize_layer)
        self.add(self._embedding)

        list(map(
            self.add,
            self._trainable_layers
        ))

    def compile(self, optimizer='adam', loss='mse', metrics=None, **kwargs):
        super(BasicModel, self).compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics or ['mse'],
            **kwargs
        )



