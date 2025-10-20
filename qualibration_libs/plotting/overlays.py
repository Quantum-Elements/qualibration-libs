from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Callable, Mapping, Any

import numpy as np
import plotly.graph_objects as go


class Overlay:
    """Adds itself to a subplot (row, col) on a Plotly Figure."""
    def add_to(self, fig, *, row: int, col: int, theme, **style):
        raise NotImplementedError


@dataclass
class LineOverlay(Overlay):
    x: np.ndarray
    y: np.ndarray
    name: Optional[str] = None
    dash: Optional[str] = "dash"
    width: Optional[float] = None
    show_legend: bool = True

    def add_to(self, fig: go.Figure, *, row: int, col: int, theme, **style):
        fig.add_trace(
            go.Scatter(
                x=self.x,
                y=self.y,
                name=self.name,
                mode="lines",
                line={"dash": self.dash, "width": self.width or theme.line_width, **style.get("line", {})},
                showlegend=self.show_legend,
            ),
            row=row,
            col=col,
        )


@dataclass
class RefLine(Overlay):
    x: Optional[float] = None
    y: Optional[float] = None
    name: Optional[str] = None
    dash: str = "dot"
    width: Optional[float] = None
    color: Optional[str] = None

    def __post_init__(self):
        if self.color is not None:
            if not isinstance(self.color, str) or len(self.color) != 7 or not self.color.startswith("#") or not all(ch in "0123456789abcdefABCDEF" for ch in self.color[1:]):
                raise ValueError("RefLine.color must be a 6-digit hex string like '#RRGGBB'.")

    def add_to(self, fig: go.Figure, *, row: int, col: int, theme, **style):
        if self.x is not None:
            line_style = {"dash": self.dash, "width": self.width or theme.line_width}
            if self.color:
                line_style["color"] = self.color
            line_style.update(style.get("line", {}))
            fig.add_shape(
                type="line",
                x0=self.x,
                y0=0,
                x1=self.x,
                y1=1,
                xref="x",
                yref="paper",
                line=line_style,
                row=row,
                col=col,
            )
        if self.y is not None:
            line_style = {"dash": self.dash, "width": self.width or theme.line_width}
            if self.color:
                line_style["color"] = self.color
            line_style.update(style.get("line", {}))
            fig.add_shape(
                type="line",
                x0=0,
                y0=self.y,
                x1=1,
                y1=self.y,
                xref="paper",
                yref="y",
                line=line_style,
                row=row,
                col=col,
            )


@dataclass
class ScatterOverlay(Overlay):
    x: np.ndarray
    y: np.ndarray
    name: Optional[str] = None
    marker_size: Optional[float] = None

    def add_to(self, fig: go.Figure, *, row: int, col: int, theme, **style):
        fig.add_trace(
            go.Scatter(
                x=self.x,
                y=self.y,
                name=self.name,
                mode="markers",
                marker={"size": self.marker_size or theme.marker_size, **style.get("marker", {})},
            ),
            row=row,
            col=col,
        )


@dataclass
class TextBoxOverlay(Overlay):
    text: str
    anchor: str = "top right"

    def add_to(self, fig: go.Figure, *, row: int, col: int, theme, **style):
        x = 1.0 if "right" in self.anchor else 0.0
        y = 1.0 if "top" in self.anchor else 0.0
        fig.add_annotation(text=self.text, x=x, y=y, xref="paper", yref="paper", showarrow=False, xanchor="right" if "right" in self.anchor else "left", yanchor="top" if "top" in self.anchor else "bottom", row=row, col=col)


@dataclass
class FitOverlay(Overlay):
    y_fit: Optional[np.ndarray] = None
    params: Optional[Mapping[str, Any]] = None
    formatter: Optional[Callable[[Mapping[str, Any]], str]] = None
    name: str = "fit"
    dash: str = "dash"
    width: Optional[float] = None

    def add_to(self, fig: go.Figure, *, row: int, col: int, theme, x=None, **style):
        if self.y_fit is not None and x is not None:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=self.y_fit,
                    name=self.name,
                    mode="lines",
                    line={"dash": self.dash, "width": self.width or theme.line_width, **style.get("line", {})},
                ),
                row=row,
                col=col,
            )
        if self.params is not None and self.formatter is not None:
            text = self.formatter(self.params)
            TextBoxOverlay(text=text).add_to(fig, row=row, col=col, theme=theme)