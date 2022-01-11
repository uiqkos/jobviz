from functools import partial
from typing import List, Tuple, Any

import pandas as pd
from mongoengine import BooleanField, DynamicDocument, DynamicEmbeddedDocument, QuerySet
from mongoengine import StringField, FloatField, IntField, EmbeddedDocumentField, ListField

from src.utils import expand_dict


class KeySkill(DynamicEmbeddedDocument):
    name: str = StringField()


class Schedule(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class Experience(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class Address(DynamicEmbeddedDocument):
    city: str = StringField()
    street: str = StringField()
    building: str = StringField()
    description: str = StringField()
    lat: float = FloatField()
    lng: float = FloatField()


class Employment(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class Salary(DynamicEmbeddedDocument):
    to: int = IntField(null=True)
    from_: int = IntField(db_field='from')
    currency: str = StringField()
    gross: bool = BooleanField()


class Area(DynamicEmbeddedDocument):
    id: str = StringField()
    url: str = StringField()
    name: str = StringField()


class Employer(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()
    url: str = StringField()
    alternate_url: str = StringField()
    trusted: bool = BooleanField()
    blacklisted: bool = BooleanField()


class Type(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class Specialization(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()
    profarea_id: str = StringField()
    profarea_name: str = StringField()


class WorkingDay(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class WorkingTimeInterval(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class WorkingTimeMode(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class ProfessorRole(DynamicEmbeddedDocument):
    id: str = StringField()
    name: str = StringField()


class VacancyQuerySet(QuerySet):
    def to_dataframe(self, include: List[str] = None, exclude: List[str] = None) -> pd.DataFrame:

        """
        Создает и возращает датафрейм, содержащий все вакансии из базы

        Parameters
        ----------
        include: поля Vacancy, включенные в датафрейм
        exclude: поля Vacancy, исключенные из датафрейма
        """

        exclude = exclude or []

        def item_filter(item: Tuple[str, Any]) -> bool:
            key = item[0]
            return \
                (not any([key.startswith(exclude_key + '.') or key == exclude_key for exclude_key in exclude])) \
                and (
                    not include or
                    any([key.startswith(include_key + '.') or key == include_key for include_key in include])
                )

        def expand_key_skills(vacancy: Vacancy):
            _vacancy = vacancy
            _vacancy.key_skills = [key_skill.name for key_skill in vacancy.key_skills]
            return _vacancy

        return pd.DataFrame(map(dict, map(
            partial(filter, item_filter),
            map(
                dict.items,
                map(
                    expand_dict,
                    map(Vacancy.to_mongo, map(
                        expand_key_skills, self
                    ))
                )
            )
        )))


class Vacancy(DynamicDocument):
    id: int = StringField(primary_key=True, db_field='id')
    description: str = StringField()
    key_skills: list[KeySkill] = ListField(EmbeddedDocumentField(KeySkill))
    schedule: Schedule = EmbeddedDocumentField(Schedule)
    # accept_handicapped
    # accept_kids
    experience: Experience = EmbeddedDocumentField(Experience)
    address: Address = EmbeddedDocumentField(Address)
    # alternate_url
    # apply_alternate_url
    # code
    # department
    employment: Employment = EmbeddedDocumentField(Employment)
    salary: Salary = EmbeddedDocumentField(Salary)
    archived: bool = BooleanField()
    name: str = StringField()
    # insider_interview
    area: Area = EmbeddedDocumentField(Area)
    created_at: str = StringField()
    published_at: str = StringField()
    employer: Employer = EmbeddedDocumentField(Employer)
    # response_letter_required
    type: Type = EmbeddedDocumentField(Type)
    # has_test
    # response_url
    # test
    specializations: list[Specialization] = ListField(EmbeddedDocumentField(Specialization))
    # contacts
    # billing_type
    # allow_messages
    # premium
    # driver_license_types
    # accept_incomplete_resumes
    working_days: list[WorkingDay] = ListField(EmbeddedDocumentField(WorkingDay))
    working_time_intervals: list[WorkingTimeInterval] = ListField(EmbeddedDocumentField(WorkingTimeInterval))
    working_time_modes: list[WorkingTimeMode] = ListField(EmbeddedDocumentField(WorkingTimeMode))
    # accept_temporary
    professional_roles: list[ProfessorRole] = ListField(EmbeddedDocumentField(ProfessorRole))

    meta = {'queryset_class': VacancyQuerySet}
