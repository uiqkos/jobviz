from src.utils import DefaultArgumentParser


class ModelTrainArgumentParser(DefaultArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_argument(
            '--limit', '-l',
            type=int,
            default=10_000,
            help='Количество данных, загружаемых из базы (default: 10000)'
        )

        self.add_argument(
            '--verbose', '-v',
            type=int,
            default=1,
            help='Уровень многословности (default: 1)'
        )

        self.add_argument(
            '--epochs', '-e',
            type=int,
            default=20,
            help='Количество эпох'
        )

        self.add_argument(
            '--model', '-m',
            default='basic',
            help="Название модели (default: 'basic')"
        )

        self.add_argument(
            '--test-size',
            type=float,
            default=.2,
            help='Размер тестовой выборки (default: 0.2)'
        )

        self.add_argument(
            '--save',
            action='store_true',
            help='Сохранить модель после обучение в папку models'
        )

