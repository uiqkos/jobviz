from typing import Union

from sklearn.preprocessing import MinMaxScaler
from tensorflow.python.keras.callbacks import History

import src.models.specializations_to_salary as models
from src.data.vacancy import Vacancy
from src.models.base_model import BaseModel
from src.models.base_trainer import BaseTrainer


class SpecToSalaryTrainer(BaseTrainer):

    def __init__(self, db_host: str, db_port: str, db: str, model: Union[str, BaseModel]):
        super().__init__(db_host, db_port, db)

        self._model = models.get(model)
        self._history = None
        self._scaler = None
        self.df = None

    @property
    def model(self) -> BaseModel:
        return self._model

    @property
    def history(self) -> History:
        return self._history

    def prepare_dataset(self, limit: int = 10_000) -> 'SpecToSalaryTrainer':
        df = (
            Vacancy
                .objects()
                .limit(limit)
                .to_dataframe(include=['professional_roles', 'salary.to', 'salary.from'])
        )

        df['salary.to'] = df['salary.to'].fillna(df['salary.from'])
        df.dropna(inplace=True)

        df['salary'] = (df['salary.from'] + df['salary.to']) / 2

        # df['salary'].apply(partial(convert_salary, from_), inplace=True)

        df.drop(['salary.from', 'salary.to'], inplace=True, axis=1)

        self._scaler = MinMaxScaler()
        df['salary'] = self._scaler.fit_transform(df[['salary']])

        self.df = df

        return self

    def predict_interpret(self, x, *args, **kwargs):
        predictions = self._model.predict(x, *args, **kwargs)
        return self._scaler.inverse_transform(predictions)

    def train(self, epochs: int, verbose: int = 1, test_size: float = 0.2) -> 'BaseTrainer':
        pass

    def save(self):
        pass