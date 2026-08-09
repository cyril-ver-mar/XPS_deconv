"""Tests for Plotly figure raster export."""

from __future__ import annotations

import pytest
import plotly.graph_objects as go

from src.ui.components.plot_export import figure_to_image_bytes, inches_to_pixels


def test_inches_to_pixels() -> None:
    assert inches_to_pixels(8.0, 300) == 2400
    assert inches_to_pixels(0.1, 72) >= 100


def _tiny_fig() -> go.Figure:
    fig = go.Figure(data=[go.Scatter(x=[1.0, 2.0, 3.0], y=[1.0, 4.0, 2.0], name="y")])
    fig.update_layout(width=320, height=240, title="test")
    return fig


@pytest.mark.parametrize("fmt", ["png", "jpeg", "tif"])
def test_figure_to_image_bytes_formats(fmt: str) -> None:
    pytest.importorskip("kaleido")
    data = figure_to_image_bytes(
        _tiny_fig(),
        fmt=fmt,  # type: ignore[arg-type]
        width_px=320,
        height_px=240,
        scale=1.0,
    )
    assert isinstance(data, (bytes, bytearray))
    assert len(data) > 100
    if fmt == "png":
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
    elif fmt == "jpeg":
        assert data[:2] == b"\xff\xd8"
    else:
        assert data[:2] in (b"II", b"MM")
