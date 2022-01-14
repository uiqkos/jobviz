from functools import partial
from typing import List, Tuple, Any

import pandas as pd
from mongoengine import BooleanField, DynamicDocument, DynamicEmbeddedDocument, QuerySet, Document, EmbeddedDocument
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
    blackListed: bool = BooleanField()


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


class ProcessedVacancy(EmbeddedDocument):
    experience_real_id: int = IntField()
    schedule_real_id: int = IntField()
    area_id: int = IntField()
    employer_id: int = IntField()
    specializations: List[int] = ListField(IntField())
    professional_roles: List[int] = ListField(IntField())
    key_skills: List[int] = ListField(IntField())
    salary: List[int] = ListField(IntField())
    address: List[int] = ListField(IntField())
    name: List[int] = ListField(IntField())
    description: List[int] = ListField(IntField())

    @property
    def vector(self) -> List[int]:
        return [
            self.experience_real_id,
            self.schedule_real_id,
            self.area_id,
            self.employer_id,
            *self.specializations,
            *self.professional_roles,
            *self.key_skills,
            *self.salary,
            *self.address,
            *self.description,
            *self.name,
        ]


class VacancyQuerySet(QuerySet):
    def to_dataframe(self, include: List[str] = None, exclude: List[str] = None) -> pd.DataFrame:
        """
        Создает и возращает датафрейм вакансий

        Parameters
        ----------
            include:
                поля Vacancy, включенные в датафрейм
            exclude:
                поля Vacancy, исключенные из датафрейма
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
    key_skills: List[KeySkill] = ListField(EmbeddedDocumentField(KeySkill))
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
    specializations: List[Specialization] = ListField(EmbeddedDocumentField(Specialization))
    # contacts
    # billing_type
    # allow_messages
    # premium
    # driver_license_types
    # accept_incomplete_resumes
    working_days: List[WorkingDay] = ListField(EmbeddedDocumentField(WorkingDay))
    working_time_intervals: List[WorkingTimeInterval] = ListField(EmbeddedDocumentField(WorkingTimeInterval))
    working_time_modes: List[WorkingTimeMode] = ListField(EmbeddedDocumentField(WorkingTimeMode))
    # accept_temporary
    professional_roles: List[ProfessorRole] = ListField(EmbeddedDocumentField(ProfessorRole))

    processed: ProcessedVacancy = EmbeddedDocumentField(ProcessedVacancy, null=True, required=False)

    meta = {'queryset_class': VacancyQuerySet}
