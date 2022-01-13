from functools import partial
from operator import attrgetter
from typing import List

from mongoengine import connect
from pymongo import MongoClient
from pymongo.database import Database
from spacy import load
from spacy.tokens import Doc

from src.data.utils import DefaultArgumentParser
from src.data.vacancy import Vacancy, ProcessedVacancy
from src.settings import (
    MAX_DESCRIPTION_WORD_COUNT,
    MAX_NAME_WORD_COUNT,
    MAX_KEY_SKILL_COUNT,
    MAX_SPECIALIZATION_COUNT,
    MAX_PROFESSIONALS_ROLE_COUNT,
    DEFAULT_CURRENCY_ID
)

nlp = load('ru_core_news_md')


def tokenize(doc: Doc, remove_punct: bool = True, remove_stop: bool = True) -> List[int]:
    return [
        tok.orth
        for tok in doc
        if not tok.is_stop or not remove_stop
        if not tok.is_punct or not remove_punct
    ]


def pad(seq, pad_len) -> List[int]:
    return seq[:pad_len] + [0] * (pad_len - len(seq))


def id_to_real(name, value, db: Database, id_field='id'):
    return db.get_collection(name).find_one({id_field: value})['real_id']


def process_vacancy(vacancy: Vacancy, db: Database) -> ProcessedVacancy:
    description = pad(tokenize(nlp(vacancy.description)), pad_len=MAX_DESCRIPTION_WORD_COUNT)
    name = pad(tokenize(nlp(vacancy.name)), pad_len=MAX_NAME_WORD_COUNT)
    experience_real_id = id_to_real('experience', vacancy.experience.id, db)
    schedule_real_id = id_to_real('schedule', vacancy.schedule.id, db)

    salary = (
        vacancy.salary.from_,
        vacancy.salary.to,
        id_to_real('currency', vacancy.salary.currency, db, id_field='code')
    ) if vacancy.salary else (0, 0, DEFAULT_CURRENCY_ID)

    address = (vacancy.address.lat, vacancy.address.lng) if vacancy.address else (0, 0)

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
        area_id=int(vacancy.area.id),
        employer_id=int(vacancy.employer.id),
        specializations=specializations,
        professional_roles=professional_roles,
        key_skills=key_skills,
    )


if __name__ == '__main__':
    parser = DefaultArgumentParser()
    args = parser.parse_args()

    mc = MongoClient(
        host=args.db_host,
        port=args.db_port,
    )

    connect(
        host=args.db_host,
        port=args.db_port,
        db=args.db
    )

    db = mc.get_database(args.db)

    print(list(map(len, map(
        attrgetter('vector'),
        map(partial(process_vacancy, db=db), Vacancy.objects().limit(10))
    ))))
