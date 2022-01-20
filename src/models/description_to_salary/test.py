from mongoengine import connect
from tensorflow.keras.backend import clear_session

from src import settings
from src.data.vacancy import Vacancy
from src.models.description_to_salary import BasicModel
from src.models.description_to_salary.trainer import DescToSalaryTrainer

if __name__ == '__main__':
    bm = BasicModel.load()

    connect('jobviz')

    trainer = DescToSalaryTrainer(
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_NAME,
        model=bm,
    ).prepare_dataset(
        limit=50_000,
    )

    for vacancy in Vacancy.objects()[50_001:51_000]:
        if not vacancy.salary or not vacancy.salary.to or not vacancy.salary.from_:
            continue

        print('Description:', vacancy.description)
        print('Salary:', (vacancy.salary.from_ + vacancy.salary.to) / 2)
        print('Predicted salary:', trainer.predict_interpret([vacancy.description]))
