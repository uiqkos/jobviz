from tensorflow.keras.layers import Input, Dense, Dropout

from src.models.base_model import BaseModel
from src.settings import MAX_SPECIALIZATION_COUNT


class BasicModel(BaseModel):
    def __init__(self):
        super().__init__()

        self._layers = [
            Input(shape=(MAX_SPECIALIZATION_COUNT,)),
            Dense(100, activation='relu'),
            Dense(50, activation='relu'),
            Dense(10, activation='relu'),
            Dense(1)
        ]

        list(map(
            self.add,
            self._layers
        ))
