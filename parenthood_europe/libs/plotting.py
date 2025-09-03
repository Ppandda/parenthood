# libs/plotting.py
"""
Pure plotting helpers (Plotly) – no dependency on survey classes.

Each function expects tidy inputs and returns a Plotly figure.
"""

import textwrap
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Sequence


# ---------- tiny text utilities -------------------------------------------
def _wrap_text(text: str, width: int = 60) -> str:
    return "<br>".join(textwrap.wrap(text, width)) if text else ""


def _wrap_label(label: str, width: int = 20) -> str:
    return "<br>".join(textwrap.wrap(str(label), width))


def _truncate_after_first_period(text: str) -> str:
    if not text:
        return "<MISSING TITLE>"
    if "?" in text:
        return text.split("?", 1)[0].strip() + "?"
    if "." in text:
        return text.split(".", 1)[0].strip() + "."
    return text.strip()


# ---------- plot helpers ---------------------------------------------------
def bar(
    labels: Sequence[str],
    values: Sequence[int | float],
    *,
    title: str,
    orientation: str = "v",
    palette: Sequence[str] | None = None,
):
    """
    Simple bar / column chart of percentages or counts.
    """
    if not values or sum(values) == 0:
        return None

    wrapped_title = _wrap_text(_truncate_after_first_period(title), 80)
    wrapped_labels = (
        labels if orientation == "h" else [_wrap_label(lbl, 20) for lbl in labels]
    )

    if palette is None:
        palette = ["#4876AE"] * len(labels)

    if orientation == "h":
        fig = px.bar(
            y=wrapped_labels,
            x=values,
            orientation="h",
            color_discrete_sequence=palette,
            text=[f"{v:.1f}%" if isinstance(v, float) else v for v in values],
            title=wrapped_title,
        )
    else:
        fig = px.bar(
            x=wrapped_labels,
            y=values,
            orientation="v",
            color_discrete_sequence=palette,
            text=[f"{v:.1f}%" if isinstance(v, float) else v for v in values],
            title=wrapped_title,
        )

    fig.update_layout(
        width=1000,
        height=500,
        margin=dict(r=200),
        xaxis_title="" if orientation == "h" else "Value",
        yaxis_title="Value" if orientation == "h" else "",
    )
    fig.update_traces(marker_line_color=None, marker_line_width=1)
    return fig


def hist(values: pd.Series, *, title: str, x_label: str = "Value"):
    """
    Histogram (actually a bar chart of exact values) for numeric questions.
    """
    values = pd.to_numeric(values, errors="coerce").dropna()
    if values.empty:
        return None

    counts = values.value_counts().sort_index()
    percentages = counts / counts.sum() * 100
    customdata = list(zip(counts.index, counts))

    fig = go.Figure(
        data=[
            go.Bar(
                x=counts.index,
                y=percentages,
                customdata=customdata,
                hovertemplate=f"{x_label}: %{{customdata[0]}}<br>Total: %{{customdata[1]}}<extra></extra>",
                marker_color="#4876AE",
                marker_line_color="black",
                marker_line_width=1,
            )
        ]
    )
    fig.update_layout(
        title=_wrap_text(_truncate_after_first_period(title), 60),
        width=1000,
        height=500,
        margin=dict(r=200),
        xaxis_title=x_label,
        yaxis_title="Percentage (%)",
    )
    return fig


def grouped_bar(
    df: pd.DataFrame,
    *,
    x: str,
    y: str,
    hue: str | None,
    title: str,
    palette: Sequence[str] | None = None,
    category_orders: dict | None = None,
):
    """
    Grouped bar chart from a tidy DataFrame.
    """
    if df.empty:
        return None

    if palette is None:
        palette = [
            "#D7D9B1",
            "#3A6992",
            "#BB4430",
            "#795663",
            "#B89685",
            "#808F85",
        ]

    if hue is None:
        # single-trace chart; still color bars by x using our palette
        fig = px.bar(
            df,
            x=x,
            y=y,
            text=df[y].apply(lambda v: f"{v:.1f}%" if isinstance(v, float) else v),
            title=_wrap_text(_truncate_after_first_period(title), 60),
            category_orders=category_orders,
        )
        # map categories → colors using provided order if available
        order = (category_orders or {}).get(x, list(dict.fromkeys(df[x].dropna())))
        color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(order)}
        if len(fig.data) == 1:
            fig.data[0].marker.color = [color_map.get(v, palette[0]) for v in df[x]]

        wrapped = [_wrap_label(v, 20) for v in order]
        fig.update_xaxes(
            tickmode="array", tickvals=order, ticktext=wrapped, tickangle=0
        )

        for lab in order:
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(
                        color=color_map[lab],
                        symbol="square",
                        size=12,
                        line=dict(width=0),
                    ),
                    name=str(lab),
                    showlegend=True,
                    hoverinfo="skip",
                )
            )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=hue,
            barmode="group",
            text=df[y].apply(lambda v: f"{v:.1f}%" if isinstance(v, float) else v),
            title=_wrap_text(_truncate_after_first_period(title), 60),
            category_orders=category_orders,
            color_discrete_sequence=palette,
        )

    order = (category_orders or {}).get(x, list(dict.fromkeys(df[x].dropna())))
    wrapped = [_wrap_label(v, 20) for v in order]
    fig.update_xaxes(tickmode="array", tickvals=order, ticktext=wrapped, tickangle=0)

    fig.update_layout(width=1000, height=500, margin=dict(r=200))
    fig.update_traces(
        marker_line_color=None, marker_line_width=1, selector=dict(type="bar")
    )
    return fig
