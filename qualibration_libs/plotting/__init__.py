from .grid import QubitGrid
from .figure import QualibrationFigure
from .api import set_theme, set_palette, theme_context
from .accessors import XrQualPlotAccessor
from .utils import grid_iter, make_qubit_grid_from_locations


def register_accessors() -> str:
    _ = XrQualPlotAccessor  # keep linter quiet; side-effect already applied
    return "qplot"


__all__ = [
    "QubitGrid",
    "QualibrationFigure",
    "set_theme",
    "set_palette",
    "theme_context",
    "register_accessors",
    "grid_iter",
    "make_qubit_grid_from_locations",
]