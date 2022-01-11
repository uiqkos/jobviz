from datetime import datetime
from functools import reduce

from mongoengine import Document, DateField, connect


class Coverage(Document):
    start: datetime = DateField()
    end: datetime = DateField()

    def is_subset(self, other):
        return self.start >= other.start and self.end <= other.end


def total_coverage():
    """
    Возращает список дат, показывающий изменение покрытия. 1 -> 2, 3 -> 4, 5 -> 6... даты покрываются, остальные - нет

    """
    covs: list[Coverage] = Coverage.objects.order_by('start')

    res = [covs[0]]

    for cov in covs[1:]:
        if res[-1].end > cov.start:
            res[-1].end = cov.end

        else:
            res.append(cov)

    return covs


