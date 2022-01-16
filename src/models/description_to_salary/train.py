import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from pymongo import MongoClient

from src import settings
from src.data.vacancy import Vacancy
from src.models.utils import ModelTrainArgumentParser

import plotly.express as px

from src.models.description_to_salary.trainer import DescToSalaryTrainer


if __name__ == '__main__':
    parser = ModelTrainArgumentParser(description='Обучает модель для предсказания зарплаты по описанию')

    parser.add_argument(
        '--show-loss',
        action='store_true',
        help='Открыть график изменения loss'
    )

    args = parser.parse_args()

    trainer = DescToSalaryTrainer(
        args.db_host,
        args.db_port,
        args.db,
        model=args.model,
    ).prepare_dataset(
        limit=args.limit,
    ).train(
        verbose=args.verbose,
        epochs=args.epochs,
        test_size=args.test_size
    )

    if args.save:
        trainer.save()

    history = trainer.history.history

    if args.show_loss:
        px.line(history, title='Loss', labels={'index': 'epoch', 'value': 'mse'}).show()

    db = MongoClient(
        host=args.db_host,
        port=args.db_port,
    ).get_database(settings.db_name)

    # for vacancy in Vacancy.objects()[10_000:11_000]:
    #     if not vacancy.salary or not vacancy.salary.to or not vacancy.salary.from_:
    #         continue

        # print('Description:', vacancy.description)
        # print('Salary:', (vacancy.salary.from_ + vacancy.salary.to) / 2)
        # print('Predicted salary:', trainer.predict_interpret([vacancy.description])[0])