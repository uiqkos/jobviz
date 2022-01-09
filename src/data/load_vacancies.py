from mongoengine import connect

from src.data.api import get_vacancy
from vacancy import Vacancy


if __name__ == '__main__':
    vacancy_id = '50456373'
    connect('jobviz')

    vacancy = get_vacancy(vacancy_id)

    vacancy.save()

    # print(vacancy.to_json())

