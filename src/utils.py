import argparse
from typing import Union, Dict, Any, List

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from src import settings


def expand_dict(
        d: Dict[str, Union[Any, Dict]],
        ignore_underscore=False
) -> Dict[str, Any]:
    """
    Распаковывает вложенный dict

    Examples
    -------
        >>> expand_dict(
        ...     {'key1': 'value1', 'key2':{'key3': 'value3', 'key4':{'_key5': 'value5', 'key6': 'value6'}}},
        ...     ignore_underscore=True
        ... )
        {'key1': 'value1', 'key2.key3': 'value3', 'key2.key4.key6': 'value6'}
    """

    new = {}

    for key, value in d.items():
        if not ignore_underscore or not key.startswith('_'):
            if isinstance(value, dict):
                value = expand_dict(value)
                for key2, value2 in value.items():
                    new[key + '.' + key2] = value2
            else:
                new[key] = value

    return new
