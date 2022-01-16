import unittest

from tensorflow.keras import Sequential

from src.features.preprocessing import get_text_vectorization, strings, standardize_text


class TestTextPreprocessing(unittest.TestCase):
    def setUp(self) -> None:
        self.text = 'Обязанности: Своевременная подача автомобиля; Организация поездок; Планирование оптимального ' \
                    'маршрута передвижения с учетом особенностей дорожной ситуации; Поддержание чистоты в салоне ' \
                    'автомобиля; Поддержание и контроль исправного состояния автомобиля. '
        self.processed_text = 'обязанности своевременная подача автомобиля организация поездок планирование ' \
                              'оптимального маршрута передвижения с учетом особенностей дорожной ситуации ' \
                              'поддержание чистоты в салоне автомобиля поддержание и контроль исправного ' \
                              'состояния автомобиля '

        self.text2 = ' '.join(strings[:10])

        self.text_vectorization_seq = Sequential([get_text_vectorization()])
        self.text_vectorization_seq.compile()

    def test_text_vectorization(self):
        self.assertListEqual(
            list(self.text_vectorization_seq.predict([self.text2])[0]),
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )
