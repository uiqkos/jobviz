from operator import attrgetter
from typing import List

from mongoengine import connect
from pymongo import MongoClient
from pymongo.database import Database
from spacy.tokens import Doc

from src.data.vacancy import Vacancy, ProcessedVacancy
from src.embeddings import orth_to_idx, nlp
from src.settings import (
    MAX_DESCRIPTION_WORD_COUNT,
    MAX_NAME_WORD_COUNT,
    MAX_KEY_SKILL_COUNT,
    MAX_SPECIALIZATION_COUNT,
    MAX_PROFESSIONALS_ROLE_COUNT,
    DEFAULT_CURRENCY_ID
)
from src.utils import DefaultArgumentParser


def tokenize(doc: Doc, remove_punct: bool = True, remove_stop: bool = True) -> List[int]:
    return [
        orth_to_idx[tok.orth]
        for tok in doc
        if not tok.is_stop or not remove_stop
        if not tok.is_punct or not remove_punct
        if tok.orth in orth_to_idx
    ]


def pad(seq, pad_len=None) -> List[int]:
    return seq[:pad_len] + [0] * (pad_len - len(seq))


def id_to_real(name, value, db: Database, id_field='id'):
    return db.get_collection(name).find_one({id_field: value})['real_id']


def process_vacancy(vacancy: Vacancy, db: Database) -> ProcessedVacancy:
    description = pad(tokenize(nlp(vacancy.description)), pad_len=MAX_DESCRIPTION_WORD_COUNT)
    name = pad(tokenize(nlp(vacancy.name)), pad_len=MAX_NAME_WORD_COUNT)
    experience_real_id = id_to_real('experience', vacancy.experience.id, db)
    schedule_real_id = id_to_real('schedule', vacancy.schedule.id, db)

    if vacancy.salary:
        salary_from = vacancy.salary.from_ or 0
        salary_to = vacancy.salary.to or salary_from

        salary = (
            salary_from,
            salary_to,
            id_to_real('currency', vacancy.salary.currency, db, id_field='code')
        )

    else:
        salary = (0, 0, DEFAULT_CURRENCY_ID)

    address = (
        vacancy.address.lat,
        vacancy.address.lng
    ) if vacancy.address and vacancy.address.lat and vacancy.address.lng else (0, 0)

    specializations = pad(
        list(map(float, map(attrgetter('id'), vacancy.specializations))),
        pad_len=MAX_SPECIALIZATION_COUNT
    )

    professional_roles = pad(
        list(map(int, map(attrgetter('id'), vacancy.professional_roles))),
        pad_len=MAX_PROFESSIONALS_ROLE_COUNT
    )

    key_skills = pad(
        list(),
        pad_len=MAX_KEY_SKILL_COUNT
    )  # todo

    return ProcessedVacancy(
        name=name,
        description=description,
        experience_real_id=experience_real_id,
        schedule_real_id=schedule_real_id,
        salary=salary,
        address=address,
        area_id=int(vacancy.area.id or 0),
        employer_id=int(vacancy.employer.id or 0),
        specializations=specializations,
        professional_roles=professional_roles,
        key_skills=key_skills,
    )


def process_all_vacancies(db_host, db_port, db) -> None:
    mc = MongoClient(
        host=db_host,
        port=db_port,
    )

    connect(
        host=db_host,
        port=db_port,
        db=db
    )

    db = mc.get_database(db)

    for i, vacancy in enumerate(Vacancy.objects.limit(10_000)):
        processed = process_vacancy(vacancy, db)
        vacancy.processed = processed
        print(vacancy.id)
        vacancy.save()


if __name__ == '__main__':
    parser = DefaultArgumentParser()
    args = parser.parse_args()

    process_all_vacancies(args.db_host, args.db_port, args.db)


    # print(list(map(len, map(
    #     attrgetter('vector'),
    #     map(partial(process_vacancy, db=db), Vacancy.objects().limit(10))
    # ))))
