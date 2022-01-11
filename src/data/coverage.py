from datetime import datetime
from functools import reduce

from mongoengine import Document, DateField, connect


class Coverage(Document):
    start: datetime = DateField()
    end: datetime = DateField()

    def is_subset(self, other):
        return self.start >= other.start and self.end <= other.end
