from typing import Dict, List, Union

import numpy as np
import spacy
import tensorflow as tf
from pymongo.database import Database
from tensorflow.keras.initializers import Constant
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

from src import settings

nlp = spacy.load('ru_core_news_md')
embedding_matrix: np.ndarray = np.array([nlp.vocab.vectors[orth] for orth in nlp.vocab.vectors])
strings: List[str] = [nlp.vocab.strings[orth] for orth in nlp.vocab.vectors]
orth_to_idx: Dict[int, int] = dict(map(tuple, map(reversed, enumerate(nlp.vocab.vectors))))
_stop_words_regex = ' ' + ' | '.join(nlp.Defaults.stop_words) + ' '


def standardize_text(input_string):
    lower = tf.strings.lower(input_string, encoding='utf-8')
    no_html = tf.strings.regex_replace(lower, r'<.*?>', '')
    no_numbers = tf.strings.regex_replace(no_html, r'\d+', '')
    no_stop_words = tf.strings.regex_replace(' ' + no_numbers + ' ', _stop_words_regex, ' ')

    return no_stop_words


def get_text_vectorization():
    return TextVectorization(
        output_sequence_length=settings.MAX_DESCRIPTION_WORD_COUNT,
        standardize=standardize_text,
        vocabulary=strings,
    )


def get_embedding():
    return Embedding(
        input_dim=embedding_matrix.shape[0],
        output_dim=embedding_matrix.shape[1],
        embeddings_initializer=Constant(embedding_matrix),
        trainable=False
    )


def convert_salary(
        salary: Union[float, int],
        from_currency: str,
        db: Database,
        to_currency: str = 'RUR'):

    if not hasattr(convert_salary, '_currency_collection'):
        convert_salary.rate_by_code = {
            currency['code']: currency['rate']
            for currency in db.get_collection('currency').find()
        }

    from_rate = convert_salary.rate_by_code[from_currency]
    to_rate = convert_salary.rate_by_code[to_currency]
    in_rur = salary / from_rate
    return in_rur * to_rate


def vectorize_key_skills(key_skills: List[str], db: Database = settings.db) -> List[int]:
    vec = []
    for key_skill in key_skills:
        vec.append(db.get_collection('key_skills').find_one({'name': key_skill}))

    return vec
