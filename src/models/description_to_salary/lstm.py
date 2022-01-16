from typing import List

import tensorflow as tf
from tensorflow.keras.layers import Embedding, Layer, LSTM, Input

from src.features.preprocessing import get_embedding, get_text_vectorization
from src.models.embedding_model import EmbeddingModel


class LSTMModel(EmbeddingModel):
    def __init__(self):
        super().__init__()

        self._embedding = get_embedding()
        self._text_vectorization = get_text_vectorization()

        self._trainable_layers = [
            Input(shape=(1,), dtype=tf.string),
            LSTM()
        ]

    @property
    def embedding(self) -> Embedding:
        return self._embedding

    @property
    def trainable_layers(self) -> List[Layer]:
        return self._trainable_layers
