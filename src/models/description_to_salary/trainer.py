from functools import partial
from typing import Union

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

import src.models.description_to_salary as models
from src.data.vacancy import Vacancy
from src.features.preprocessing import convert_salary
from src.models.base_model import BaseModel
from src.models.base_trainer import BaseTrainer
from src.settings import ROOT_PATH


class DescToSalaryTrainer(BaseTrainer):

    def __init__(self, db_host: str, db_port: str, db: str, model: Union[str, BaseModel]):
        super().__init__(db_host, db_port, db)

        self.df = None

        self._scaler: MinMaxScaler = None
        self._model = models.get(model)

        self._model.compile()

        self._history = None

    @property
    def model(self) -> BaseModel:
        return self._model

    @property
    def history(self) -> BaseModel:
        return self._history

    def prepare_dataset(self, limit: int = 10_000):
        df: pd.DataFrame = (
            Vacancy
                .objects()
                .limit(limit)
                .to_dataframe(include=['description', 'salary.to', 'salary.from', 'salary.currency'])
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

    def train(
            self,
            epochs: int,
            verbose: int = 1,
            test_size=0.2,
            *args,
            **kwargs,
    ):
        X = np.array(self.df['description'].values)
        y = self.df['salary'].values.reshape(-1, 1)

        if verbose:
            print('Данные загружены. Размер X:', X.shape, ', y:', y.shape)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

        if verbose:
            print(self._model.summary())

        self._history = self._model.fit(
            X_train, y_train,
            epochs=epochs, batch_size=32,
            verbose=verbose, *args, **kwargs
        )

        print('Loss on test set:', self._model.evaluate(X_test, y_test))

        # predictions = self.model.predict(X_test, batch_size=32)

        # for pred, true in zip(predictions, y_test):
        #     print('Actual:', pred, 'True:', true, 'Error:', abs(pred - true))

        return self

    def save(self):
        self._model.save('basic')
