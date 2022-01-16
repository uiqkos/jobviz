from src.models.base_model import BaseModel
from src.models.specializations_to_salary.basic import BasicModel

_models = {
    'basic': BasicModel
}


def get(identifier):
    if isinstance(identifier, BaseModel):
        return identifier

    if isinstance(identifier, str):
        return _models.get(identifier)()

    raise Exception(f'Could not interpret model identifier: {identifier}')
