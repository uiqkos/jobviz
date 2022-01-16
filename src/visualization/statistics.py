from typing import Union

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure


def plot_value_counts(
        s: Union[pd.Series, pd.DataFrame],
        x_label: str,
        y_label: str,
        *args,
        **kwargs
) -> Figure:
    """Возращает график, показывающий количество обьектов для каждого значения набора данных"""
    value_counts = s.value_counts()

    return px.bar(
        *args,
        x=value_counts.index,
        y=value_counts,
        labels=dict(
            x=x_label,
            y=y_label
        ),
        **kwargs
    )

