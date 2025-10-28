from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Tuple, Optional, Iterable

from .config import PlotTheme
from . import config as _config

_PALETTES: Dict[str, Tuple[str, ...]] = {
    "qualibrate": PlotTheme().colorway,
    "deep": (
        "#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b2", "#937860", "#da8bc3", "#8c8c8c", "#ccb974", "#64b5cd"),
    "muted": (
        "#4878d0", "#ee854a", "#6acc64", "#d65f5f", "#b47cc7", "#82c6e2", "#d5bb67", "#8c8c8c", "#ff9da6", "#9d755d"),
}

_FIT_PALETTES: Dict[str, Tuple[str, ...]] = {
    "qualibrate_fit": PlotTheme().fit_colorway,
    "deep_fit": (
        "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"),
    "muted_fit": (
        "#cc5500", "#228b22", "#ff8c00", "#8a2be2", "#a0522d", "#da70d6", "#696969", "#9acd32"),
}


def set_theme(
    theme: Optional[PlotTheme] = None, *,
    palette: Optional[str | Iterable[str]] = None,
    fit_palette: Optional[str | Iterable[str]] = None,
    rc: Optional[dict] = None
) -> None:
    if theme is not None:
        # Mutate existing theme object in-place so all modules holding a reference see updates
        for k, v in theme.__dict__.items():
            setattr(_config.CURRENT_THEME, k, v)
    if palette is not None:
        if isinstance(palette, str):
            _config.CURRENT_PALETTE = _PALETTES.get(palette, PlotTheme().colorway)
        else:
            _config.CURRENT_PALETTE = tuple(palette)
    if fit_palette is not None:
        if isinstance(fit_palette, str):
            _config.CURRENT_FIT_PALETTE = _FIT_PALETTES.get(fit_palette, PlotTheme().fit_colorway)
        else:
            _config.CURRENT_FIT_PALETTE = tuple(fit_palette)
    if rc is not None:
        _config.CURRENT_RC.values.update(rc)


def set_palette(palette: str | Iterable[str]) -> None:
    if isinstance(palette, str):
        _config.CURRENT_PALETTE = _PALETTES.get(palette, PlotTheme().colorway)
    else:
        _config.CURRENT_PALETTE = tuple(palette)


def set_fit_palette(fit_palette: str | Iterable[str]) -> None:
    """Set the color palette for fit lines and reference lines.
    
    Args:
        fit_palette: Either a string name of a built-in fit palette 
                    ("qualibrate_fit", "deep_fit", "muted_fit") or 
                    an iterable of color strings.
    """
    if isinstance(fit_palette, str):
        _config.CURRENT_FIT_PALETTE = _FIT_PALETTES.get(fit_palette, PlotTheme().fit_colorway)
    else:
        _config.CURRENT_FIT_PALETTE = tuple(fit_palette)


@contextmanager
def theme_context(
    theme: Optional[PlotTheme] = None, *,
    palette: Optional[str | Iterable[str]] = None,
    fit_palette: Optional[str | Iterable[str]] = None,
    rc: Optional[dict] = None
):
    # Snapshot current theme values to restore later
    orig_theme = PlotTheme(**_config.CURRENT_THEME.__dict__)
    orig_palette = _config.CURRENT_PALETTE
    orig_fit_palette = _config.CURRENT_FIT_PALETTE
    orig_rc = dict(_config.CURRENT_RC.values)
    try:
        set_theme(theme, palette=palette, fit_palette=fit_palette, rc=rc)
        yield
    finally:
        # Restore theme values in-place
        for k, v in orig_theme.__dict__.items():
            setattr(_config.CURRENT_THEME, k, v)
        _config.CURRENT_PALETTE = orig_palette
        _config.CURRENT_FIT_PALETTE = orig_fit_palette
        _config.CURRENT_RC.values.clear()
        _config.CURRENT_RC.values.update(orig_rc)
