import html
import re

from mongoengine import connect

from src.data.vacancy import Vacancy


def remove_html_from_description():
    tagr = re.compile('<.*?>')

    for vacancy in Vacancy.objects:
        vacancy.description = re.sub(tagr, '', html.unescape(vacancy.description))
        vacancy.save()


if __name__ == '__main__':
    connect('jobviz')
    remove_html_from_description()
