"""Tests for Plotly figure raster export (matplotlib, no Chrome)."""

from __future__ import annotations

import plotly.graph_objects as go
import pytest

from src.ui.components.plot_export import figure_to_image_bytes, inches_to_pixels, rasterize_figure
from src.ui.components.plots import PlotStyle, PlotViewState, spectrum_figure


def test_inches_to_pixels() -> None:
    assert inches_to_pixels(8.0, 300) == 2400
    assert inches_to_pixels(0.1, 72) >= 100


def _tiny_fig() -> go.Figure:
    fig = go.Figure(data=[go.Scatter(x=[1.0, 2.0, 3.0], y=[1.0, 4.0, 2.0], name="y")])
    fig.update_layout(width=320, height=240, title="test", xaxis_title="BE", yaxis_title="I")
    return fig


@pytest.mark.parametrize("fmt", ["png", "jpeg", "tif"])
def test_figure_to_image_bytes_formats(fmt: str) -> None:
    data = figure_to_image_bytes(
        _tiny_fig(),
        fmt=fmt,  # type: ignore[arg-type]
        width_px=320,
        height_px=240,
        scale=1.0,
        dpi=100,
        width_in=3.2,
        height_in=2.4,
    )
    assert isinstance(data, (bytes, bytearray))
    assert len(data) > 100
    if fmt == "png":
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
    elif fmt == "jpeg":
        assert data[:2] == b"\xff\xd8"
    else:
        assert data[:2] in (b"II", b"MM")


def test_rasterize_uses_matplotlib_only() -> None:
    result = rasterize_figure(
        _tiny_fig(), width_px=320, height_px=240, dpi=100, width_in=3.2, height_in=2.4
    )
    assert result.engine == "matplotlib"
    assert result.warning == ""
    assert result.data[:8] == b"\x89PNG\r\n\x1a\n"


def test_plot_style_axis_names_and_colors() -> None:
    import numpy as np

    be = np.array([290.0, 285.0, 280.0])
    y = np.array([1.0, 3.0, 1.2])
    view = PlotViewState(
        invert_x=True,
        style=PlotStyle(
            title="C 1s",
            x_title="BE / eV",
            y_title="Counts",
            raw_color="#ff00aa",
            raw_width=3.5,
            axis_color="#003366",
            font_family="Times New Roman",
            grid_on=True,
        ),
    )
    fig = spectrum_figure(be, y, view=view)
    assert fig.layout.xaxis.title.text == "BE / eV"
    assert fig.layout.yaxis.title.text == "Counts"
    assert fig.data[0].line.color == "#ff00aa"
    assert fig.data[0].line.width == 3.5
    assert fig.layout.font.color == "#003366"
    assert fig.layout.xaxis.showgrid is True
    assert fig.layout.xaxis.minor.showgrid is True
    assert (fig.layout.yaxis.exponentformat or "none") != "SI"


def test_legend_and_axis_titles_follow_language() -> None:
    import numpy as np

    be = np.array([290.0, 285.0, 280.0])
    y = np.array([1.0, 3.0, 1.2])
    fig_ru = spectrum_figure(be, y, lang="ru")
    names_ru = [tr.name for tr in fig_ru.data]
    assert "Сырой" in names_ru
    assert fig_ru.layout.xaxis.title.text == "Энергия связи (эВ)"
    assert fig_ru.layout.yaxis.title.text == "Интенсивность"
    fig_en = spectrum_figure(be, y, lang="en")
    names_en = [tr.name for tr in fig_en.data]
    assert "Raw" in names_en
    assert fig_en.layout.xaxis.title.text == "Binding energy (eV)"
    assert fig_en.layout.yaxis.title.text == "Intensity"


def test_mismatched_baseline_is_dropped() -> None:
    import numpy as np

    be = np.array([290.0, 285.0, 280.0])
    y = np.array([1.0, 3.0, 1.2])
    old_baseline = np.ones(50) * 0.4
    fig = spectrum_figure(be, y, baseline=old_baseline, lang="en")
    names = [tr.name for tr in fig.data]
    assert "Baseline" not in names


def test_peak_be_labels_use_component_maximum() -> None:
    import numpy as np

    be = np.array([286.0, 285.0, 284.0, 283.0])
    y = np.array([1.0, 2.0, 8.0, 1.5])
    comp = np.array([0.2, 1.0, 7.5, 0.4])
    view = PlotViewState(
        show_peak_be_labels=True,
        peak_be_digits=2,
        style=PlotStyle(show_legend=False),
    )
    fig = spectrum_figure(be, y, components=[comp], view=view, lang="en")
    texts = [str(a.text) for a in fig.layout.annotations]
    assert "284.00" in texts


def test_compact_y_ticks_optional() -> None:
    import numpy as np

    be = np.array([290.0, 285.0, 280.0])
    y = np.array([1000.0, 25000.0, 5000.0])
    view = PlotViewState(
        style=PlotStyle(compact_y_ticks=True, show_legend=False),
    )
    fig = spectrum_figure(be, y, view=view)
    assert fig.layout.yaxis.exponentformat == "SI"


def test_element_bands_add_headers() -> None:
    import numpy as np

    from src.core.models import ELEMENT_BE_BANDS

    be = np.linspace(400.0, 250.0, 80)
    y = np.ones(80)
    c1s = next(b for b in ELEMENT_BE_BANDS if b.label == "C1s")
    view = PlotViewState(
        invert_x=True,
        style=PlotStyle(show_legend=False),
        element_bands=[c1s],
    )
    fig = spectrum_figure(be, y, view=view)
    texts = [str(a.text) for a in fig.layout.annotations]
    assert "C1s" in texts
    assert any(abs(float(s.x0) - c1s.x0) < 1e-6 for s in fig.layout.shapes)


def test_matplotlib_export_keeps_grid_and_serif_ticks() -> None:
    import numpy as np
    import matplotlib.pyplot as plt

    from src.ui.components.plot_export import build_matplotlib_figure

    be = np.linspace(1200.0, 0.0, 50)
    y = np.linspace(0.0, 25000.0, 50)
    view = PlotViewState(
        invert_x=True,
        x_min=0.0,
        x_max=1200.0,
        y_min=0.0,
        y_max=25000.0,
        style=PlotStyle(
            title="РФЭС - скан-спектр",
            x_title="Энергия связи (эВ)",
            y_title="Интенсивность",
            font_family="Times New Roman",
            font_size=14,
            title_size=16,
            tick_size=12,
            grid_on=True,
            show_legend=False,
        ),
    )
    fig = spectrum_figure(be, y, view=view)
    mpl_fig = build_matplotlib_figure(fig, width_in=8.0, height_in=5.0, dpi=100)
    try:
        ax = mpl_fig.axes[0]
        assert ax.xaxis.get_gridlines()[0].get_visible()
        minor = ax.xaxis.get_minorticklocs()
        assert len(minor) > 0
        tick_name = ax.xaxis.get_label().get_fontname().lower()
        assert "times" in tick_name or "serif" in tick_name or "roman" in tick_name
        # Tick labels use the same family (not default DejaVu Sans-only)
        sample = ax.get_xticklabels()[0].get_fontname().lower()
        assert "times" in sample or "serif" in sample or "roman" in sample or "stix" in sample
    finally:
        plt.close(mpl_fig)
