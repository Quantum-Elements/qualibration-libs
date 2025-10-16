from __future__ import annotations

from typing import Tuple, Any, Mapping, Iterable, Sequence, Iterator

import xarray as xr
from .grid import QubitGrid


def get_axis_label(ds: xr.Dataset, coord: str) -> str:
    if coord not in ds.coords:
        return coord
    attrs = ds.coords[coord].attrs or {}
    name = attrs.get("long_name", coord)
    units = attrs.get("units")
    return f"{name} [{units}]" if units else name


def get_qubit_title(qubit_name: str) -> str:
    return f"{qubit_name}"


def parse_grid_location(loc: str) -> tuple[int, int]:
    col_str, row_str = loc.split(",")
    col = int(col_str)
    row = int(row_str)
    return row, col


def label_from_attrs(name: str, attrs: Mapping[str, Any]) -> str:
    long_name = attrs.get("long_name")
    units = attrs.get("units")
    base = long_name or name
    return f"{base} [{units}]" if units else base


def map_hue_value(dim_name: str, value: Any) -> str:
    if dim_name.lower() in ("detuning_signs", "sign"):
        if value in ("+", "+1", 1, True):
            return "Δ = +"
        if value in ("-", "-1", -1, False):
            return "Δ = −"
    return f"{dim_name} = {value}"


def compute_secondary_ticks(
    primary_vals: Iterable[float],
    secondary_vals: Iterable[float]
) -> Tuple[list, list]:
    p = list(primary_vals)
    s = list(secondary_vals)
    if not p or not s or len(p) != len(s):
        return [], []
    n = len(p)
    step = max(1, n // 6)
    idxs = list(range(0, n, step))
    if idxs[-1] != n - 1:
        idxs.append(n - 1)
    tickvals = [p[i] for i in idxs]
    ticktext = [str(s[i]) for i in idxs]
    return tickvals, ticktext


def grid_iter(ds: xr.Dataset, grid: QubitGrid, qubit_dim: str = "qubit") -> Iterator[Tuple[Tuple[int, int], dict]]:
    names: Sequence[str]
    if qubit_dim in ds.dims:
        names = list(map(str, ds.coords[qubit_dim].values))
    else:
        names = ["qubit"]
    _, _, positions = grid.resolve(names)
    for name in names:
        if name not in positions:
            continue
        row, col = positions[name]
        yield (row, col), {"qubit": name}


def make_qubit_grid_from_locations(ds: xr.Dataset, qubits: Sequence[Any], qubit_dim: str = "qubit") -> QubitGrid:
    names: Sequence[str] = list(map(str, ds.coords[qubit_dim].values)) if qubit_dim in ds.dims else []
    coords: dict[str, Tuple[int, int]] = {}

    def _get_name(idx: int, q: Any) -> str:
        if isinstance(q, dict):
            return str(q.get("qubit") or q.get("name") or (names[idx] if idx < len(names) else idx))
        return str(getattr(q, "qubit", None) or getattr(q, "name", None) or (names[idx] if idx < len(names) else idx))

    def _get_location(q: Any) -> Any:
        if isinstance(q, dict):
            return q.get("grid_location")
        return getattr(q, "grid_location", None)

    for i, q in enumerate(qubits):
        loc = _get_location(q)
        if not loc:
            continue
        row, col = parse_grid_location(str(loc))
        name = _get_name(i, q)
        coords[name] = (row, col)

    return QubitGrid(coords=coords)
