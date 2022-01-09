from datetime import datetime

from bson import ObjectId
from mongoengine import BooleanField, DateTimeField, DynamicDocument, DynamicEmbeddedDocument as MongoDynamicEmbeddedDocument
from mongoengine import StringField, FloatField, IntField, EmbeddedDocumentField, ListField, ObjectIdField


class DynamicEmbeddedDocument(MongoDynamicEmbeddedDocument):
    # _id = StringField(unique=True, primary_key=True)
    meta = {'allow_inheritance': True}


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
    from_: int = IntField()
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


class Vacancy(DynamicDocument):
    _id = StringField(default=ObjectId, primary_key=True)
    id: int = StringField(unique=True, primary_key=False)
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
