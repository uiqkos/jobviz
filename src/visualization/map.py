from dataclasses import dataclass, field
from functools import partial
from math import *
from operator import attrgetter
from typing import List

import numpy as np

MAX_DISTANCE_KM = 300.


@dataclass
class Point:
    profarea: str
    lat: float
    lng: float

    @classmethod
    def from_tuple(cls, tup):
        return Point(*tup)


def distance_lat_lng(p1: Point, p2: Point) -> 'km':
    """Дистанция между 2 точками (широта, долгота) в км"""
    R = 6371e3  # m

    # to rad
    lat1 = p1.lat * pi / 180
    lat2 = p2.lat * pi / 180
    lng1 = p1.lng * pi / 180
    lng2 = p2.lng * pi / 180

    delta_lat = abs(lat2 - lat1)
    delta_lng = abs(lng2 - lng1)
    a = pow(sin(delta_lat / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(delta_lng / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c

    return d / 1000  # km


@dataclass
class Area:
    profarea: str
    points: List[Point] = field(default_factory=list)

    def __iand__(self, other: 'Point') -> bool:
        if other.profarea != self.profarea:
            return False

        if all(map(MAX_DISTANCE_KM.__ge__, map(partial(distance_lat_lng, other), self.points))):
            self.points.append(other)
            return True

        return False

    @property
    def count(self):
        return len(self.points)

    @property
    def center_lat(self):
        return np.mean(list(map(attrgetter('lat'), self.points)))

    @property
    def center_lng(self):
        return np.mean(list(map(attrgetter('lng'), self.points)))
