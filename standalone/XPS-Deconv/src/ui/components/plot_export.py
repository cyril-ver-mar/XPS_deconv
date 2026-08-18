"""Export Plotly figures to PNG / JPEG / TIFF via matplotlib (no Chrome/Kaleido)."""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Literal, Optional

import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from src.utils.i18n import DEFAULT_LANG, t

ExportFormat = Literal["png", "jpeg", "tif"]

_MIME = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "tif": "image/tiff",
}

_EXT = {
    "png": "png",
    "jpeg": "jpg",
    "tif": "tif",
}

_DASH = {
    "solid": "-",
    "dot": ":",
    "dash": "--",
    "longdash": "--",
    "dashdot": "-.",
    "longdashdot": "-.",
}


@dataclass(frozen=True)
class RasterResult:
    data: bytes
    engine: str
    warning: str = ""


def inches_to_pixels(inches: float, dpi: int) -> int:
    return max(100, int(round(float(inches) * float(dpi))))


def _mpl_color(value: object) -> object:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("rgba"):
        inner = text[text.find("(") + 1 : text.rfind(")")]
        parts = [p.strip() for p in inner.split(",")]
        if len(parts) >= 3:
            r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
            a = float(parts[3]) if len(parts) > 3 else 1.0
            if r > 1 or g > 1 or b > 1:
                r, g, b = r / 255.0, g / 255.0, b / 255.0
            return (r, g, b, a)
    if text.startswith("rgb"):
        inner = text[text.find("(") + 1 : text.rfind(")")]
        parts = [p.strip() for p in inner.split(",")]
        if len(parts) >= 3:
            r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
            if r > 1 or g > 1 or b > 1:
                r, g, b = r / 255.0, g / 255.0, b / 255.0
            return (r, g, b)
    return text


# Plotly font sizes are CSS pixels on a ~560px-tall figure. Matplotlib uses points.
# 1 CSS px ≈ 0.75 pt, which keeps label/plot proportions close to the Streamlit preview.
_PX_TO_PT = 72.0 / 96.0

_SERIF_HINTS = ("times", "georgia", "stix", "serif", "roman", "computer modern", "cmr")


def _px_to_pt(value: object, default_px: float) -> float:
    try:
        px = float(value) if value is not None else default_px
    except (TypeError, ValueError):
        px = default_px
    return max(5.0, px * _PX_TO_PT)


def _layout_size(obj: object, default: float) -> float:
    try:
        size = getattr(obj, "size", None)
        if size is not None:
            return float(size)
    except (TypeError, ValueError):
        pass
    return default


def _layout_family(obj: object, fallback: str) -> str:
    family = getattr(obj, "family", None) if obj is not None else None
    if family:
        return str(family).split(",")[0].strip()
    return fallback


def _is_serif(name: str) -> bool:
    low = (name or "").lower()
    return any(h in low for h in _SERIF_HINTS)


def _si_tick(value: float, _pos: object) -> str:
    if value == 0 or abs(value) < 1e-12:
        return "0"
    sign = "-" if value < 0 else ""
    av = abs(value)
    if av >= 1_000_000:
        scaled = av / 1_000_000
        body = f"{scaled:.0f}" if abs(scaled - round(scaled)) < 1e-9 else f"{scaled:g}"
        return f"{sign}{body}M"
    if av >= 1000:
        scaled = av / 1000
        body = f"{int(round(scaled))}" if abs(scaled - round(scaled)) < 1e-9 else f"{scaled:g}"
        return f"{sign}{body}k"
    if abs(value - round(value)) < 1e-9 and av >= 10:
        return f"{sign}{int(round(av))}"
    return f"{value:g}"


def _show_grid(axis) -> bool:
    if axis is None:
        return False
    flag = getattr(axis, "showgrid", None)
    return bool(flag)


def _show_minor_grid(axis) -> bool:
    if axis is None:
        return False
    minor = getattr(axis, "minor", None)
    if minor is None:
        return _show_grid(axis)
    flag = getattr(minor, "showgrid", None)
    if flag is None:
        return _show_grid(axis)
    return bool(flag)


def build_matplotlib_figure(fig: go.Figure, width_in: float, height_in: float, dpi: int):
    """Build a matplotlib Figure that mirrors Plotly fonts, grid, and proportions."""
    import matplotlib

    matplotlib.use("Agg", force=True)
    from matplotlib import font_manager
    from matplotlib.ticker import AutoMinorLocator, FuncFormatter, ScalarFormatter
    import matplotlib.pyplot as plt

    layout = fig.layout
    family = _layout_family(layout.font, "DejaVu Sans")
    if layout.xaxis and layout.xaxis.tickfont:
        family = _layout_family(layout.xaxis.tickfont, family)

    base_px = _layout_size(layout.font, 14)
    title_px = base_px + 2
    if layout.title and layout.title.font:
        title_px = _layout_size(layout.title.font, title_px)
    tick_px = base_px - 2
    if layout.xaxis and layout.xaxis.tickfont:
        tick_px = _layout_size(layout.xaxis.tickfont, tick_px)
    axis_title_px = base_px
    if layout.xaxis and layout.xaxis.title and layout.xaxis.title.font:
        axis_title_px = _layout_size(layout.xaxis.title.font, axis_title_px)
    legend_px = base_px - 3
    if layout.legend and layout.legend.font:
        legend_px = _layout_size(layout.legend.font, legend_px)

    axis_color = "#111111"
    if layout.font and layout.font.color:
        axis_color = str(layout.font.color)
    grid_color = "#cccccc"
    if layout.xaxis and layout.xaxis.gridcolor:
        grid_color = str(layout.xaxis.gridcolor)

    serif = _is_serif(family)
    rc = {
        "font.size": _px_to_pt(base_px, 14),
        "axes.unicode_minus": False,
        "axes.linewidth": 0.8,
    }
    if serif:
        rc["font.family"] = "serif"
        rc["font.serif"] = [family, "Times New Roman", "Times", "DejaVu Serif"]
        rc["mathtext.fontset"] = "stix"
    else:
        rc["font.family"] = "sans-serif"
        rc["font.sans-serif"] = [family, "Arial", "Helvetica", "DejaVu Sans"]

    with plt.rc_context(rc):
        mpl_fig, ax = plt.subplots(
            figsize=(max(1.0, width_in), max(1.0, height_in)),
            dpi=max(72, int(dpi)),
        )
        for tr in fig.data:
            tname = getattr(tr, "type", None) or ""
            if tname not in ("scatter", "scattergl"):
                continue
            x = list(tr.x) if tr.x is not None else []
            y = list(tr.y) if tr.y is not None else []
            if not x or not y:
                continue
            line = tr.line if hasattr(tr, "line") else None
            color = _mpl_color(line.color if line is not None else None)
            width = float(line.width) if line is not None and line.width else 1.5
            dash = str(line.dash) if line is not None and line.dash else "solid"
            ls = _DASH.get(dash, "-")
            fill = str(getattr(tr, "fill", None) or "")
            label = tr.name if getattr(tr, "showlegend", True) else None
            lw = max(0.4, width * _PX_TO_PT)
            if fill == "tozeroy":
                fc = _mpl_color(getattr(tr, "fillcolor", None)) or color
                ax.fill_between(x, y, color=fc, linewidth=0, zorder=1)
            ax.plot(x, y, color=color, lw=lw, linestyle=ls, label=label, zorder=2, solid_capstyle="round")

        x_title = ""
        y_title = ""
        if layout.xaxis and layout.xaxis.title:
            x_title = str(layout.xaxis.title.text or "")
        if layout.yaxis and layout.yaxis.title:
            y_title = str(layout.yaxis.title.text or "")

        title_pt = _px_to_pt(title_px, 16)
        axis_pt = _px_to_pt(axis_title_px, 14)
        tick_pt = _px_to_pt(tick_px, 12)
        legend_pt = _px_to_pt(legend_px, 11)

        try:
            resolved = font_manager.findfont(
                font_manager.FontProperties(family=family),
                fallback_to_default=True,
            )
            tick_fp = font_manager.FontProperties(fname=resolved, size=tick_pt)
            axis_fp = font_manager.FontProperties(fname=resolved, size=axis_pt)
            title_fp = font_manager.FontProperties(fname=resolved, size=title_pt)
            legend_fp = font_manager.FontProperties(fname=resolved, size=legend_pt)
        except Exception:
            tick_fp = font_manager.FontProperties(family=family, size=tick_pt)
            axis_fp = font_manager.FontProperties(family=family, size=axis_pt)
            title_fp = font_manager.FontProperties(family=family, size=title_pt)
            legend_fp = font_manager.FontProperties(family=family, size=legend_pt)

        ax.set_xlabel(x_title, fontproperties=axis_fp, color=axis_color)
        ax.set_ylabel(y_title, fontproperties=axis_fp, color=axis_color)
        if layout.title and layout.title.text:
            ax.set_title(str(layout.title.text), fontproperties=title_fp, color=axis_color, pad=8)

        if layout.xaxis and layout.xaxis.range:
            ax.set_xlim(layout.xaxis.range[0], layout.xaxis.range[1])
        if layout.yaxis and layout.yaxis.range:
            ax.set_ylim(layout.yaxis.range[0], layout.yaxis.range[1])

        for shape in layout.shapes or []:
            stype = str(getattr(shape, "type", "") or "")
            if stype != "rect":
                continue
            try:
                x0 = float(shape.x0)
                x1 = float(shape.x1)
            except (TypeError, ValueError):
                continue
            opacity = float(getattr(shape, "opacity", None) or 0.16)
            fc = _mpl_color(getattr(shape, "fillcolor", None)) or "#6aa6de"
            ax.axvspan(min(x0, x1), max(x0, x1), facecolor=fc, alpha=opacity, linewidth=0, zorder=0)

        for ann in layout.annotations or []:
            text = str(getattr(ann, "text", "") or "")
            if not text:
                continue
            try:
                x = float(ann.x)
            except (TypeError, ValueError):
                continue
            yref = str(getattr(ann, "yref", "") or "paper")
            yshift = float(getattr(ann, "yshift", None) or 0.0)
            if yref == "paper":
                y_axes = 1.0 + (yshift / 400.0)
                ax.text(
                    x,
                    y_axes,
                    text,
                    transform=ax.get_xaxis_transform(),
                    ha="center",
                    va="bottom",
                    fontproperties=tick_fp,
                    color=axis_color,
                    clip_on=False,
                    zorder=4,
                )
            else:
                try:
                    y_data = float(ann.y)
                except (TypeError, ValueError):
                    continue
                ax.annotate(
                    text,
                    xy=(x, y_data),
                    xytext=(0, max(6.0, yshift or 8.0)),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontproperties=tick_fp,
                    color=_mpl_color(getattr(getattr(ann, "font", None), "color", None)) or axis_color,
                    clip_on=False,
                    zorder=5,
                )

        paper = str(layout.paper_bgcolor or "#ffffff")
        plot_bg = str(layout.plot_bgcolor or "#ffffff")
        mpl_fig.patch.set_facecolor(_mpl_color(paper) or "white")
        ax.set_facecolor(_mpl_color(plot_bg) or "white")
        for spine in ax.spines.values():
            spine.set_color(axis_color)
            spine.set_linewidth(0.8)
        ax.tick_params(
            colors=axis_color,
            labelsize=tick_pt,
            direction="out",
            length=4,
            width=0.8,
            which="major",
            top=True,
            right=True,
        )
        ax.tick_params(which="minor", length=2, width=0.6, colors=axis_color, top=True, right=True)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(tick_fp)
            label.set_color(axis_color)

        y0, y1 = ax.get_ylim()
        exp_fmt = ""
        if layout.yaxis:
            exp_fmt = str(getattr(layout.yaxis, "exponentformat", None) or "")
        if exp_fmt.lower() == "si" and max(abs(y0), abs(y1)) >= 1000:
            ax.yaxis.set_major_formatter(FuncFormatter(_si_tick))
        else:
            yfmt = ScalarFormatter(useOffset=False, useMathText=False)
            yfmt.set_scientific(False)
            ax.yaxis.set_major_formatter(yfmt)

        show_major = _show_grid(layout.xaxis) or _show_grid(layout.yaxis)
        show_minor = _show_minor_grid(layout.xaxis) or _show_minor_grid(layout.yaxis)
        ax.set_axisbelow(True)
        if show_major:
            ax.grid(True, which="major", color=_mpl_color(grid_color) or "#cccccc", linewidth=0.6, alpha=0.85)
        else:
            ax.grid(False, which="major")
        if show_minor or show_major:
            ax.xaxis.set_minor_locator(AutoMinorLocator(5))
            ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        if show_minor:
            ax.grid(
                True,
                which="minor",
                color=_mpl_color(grid_color) or "#cccccc",
                linewidth=0.35,
                alpha=0.45,
                linestyle=":",
            )

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(tick_fp)
            label.set_color(axis_color)

        show_legend = bool(layout.showlegend) if layout.showlegend is not None else True
        handles, labels = ax.get_legend_handles_labels()
        if show_legend and labels:
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(0.0, -0.18),
                ncol=min(4, max(1, len(labels))),
                frameon=False,
                prop=legend_fp,
                borderaxespad=0.0,
            )
            mpl_fig.subplots_adjust(left=0.12, right=0.96, top=0.90, bottom=0.22)
        else:
            mpl_fig.tight_layout()
        return mpl_fig


def _matplotlib_png(fig: go.Figure, width_in: float, height_in: float, dpi: int) -> bytes:
    import matplotlib.pyplot as plt

    mpl_fig = build_matplotlib_figure(fig, width_in, height_in, dpi)
    buf = io.BytesIO()
    mpl_fig.savefig(buf, format="png", dpi=max(72, int(dpi)), facecolor=mpl_fig.get_facecolor())
    plt.close(mpl_fig)
    return buf.getvalue()


def rasterize_figure(
    fig: go.Figure,
    *,
    width_px: int,
    height_px: int,
    scale: float = 1.0,
    dpi: int = 300,
    width_in: Optional[float] = None,
    height_in: Optional[float] = None,
) -> RasterResult:
    """PNG bytes via matplotlib Agg — never launches Chrome/Kaleido."""
    width_px = max(100, int(width_px))
    height_px = max(100, int(height_px))
    scale = max(0.5, float(scale))
    dpi = max(72, int(round(int(dpi) * scale)))
    w_in = float(width_in) if width_in else width_px / float(dpi)
    h_in = float(height_in) if height_in else height_px / float(dpi)
    try:
        png = _matplotlib_png(fig, w_in, h_in, dpi)
    except Exception as mpl_exc:
        raise RuntimeError(
            f"Image export failed (matplotlib): {type(mpl_exc).__name__}: {mpl_exc}"
        ) from mpl_exc
    return RasterResult(png, "matplotlib")


def _encode_from_png(png_bytes: bytes, fmt: ExportFormat, jpeg_quality: int) -> bytes:
    if fmt == "png":
        return png_bytes
    img = Image.open(io.BytesIO(png_bytes))
    if fmt == "jpeg":
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            background.paste(rgba, mask=rgba.split()[-1])
            img = background
        else:
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
        return buf.getvalue()
    if img.mode == "P":
        img = img.convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="TIFF", compression="tiff_lzw")
    return buf.getvalue()


def figure_to_image_bytes(
    fig: go.Figure,
    *,
    fmt: ExportFormat,
    width_px: int,
    height_px: int,
    scale: float = 1.0,
    jpeg_quality: int = 95,
    dpi: int = 300,
    width_in: Optional[float] = None,
    height_in: Optional[float] = None,
) -> bytes:
    """Rasterize ``fig`` with matplotlib, then convert JPEG/TIFF with Pillow."""
    jpeg_quality = max(40, min(100, int(jpeg_quality)))
    result = rasterize_figure(
        fig,
        width_px=width_px,
        height_px=height_px,
        scale=scale,
        dpi=dpi,
        width_in=width_in,
        height_in=height_in,
    )
    return _encode_from_png(result.data, fmt, jpeg_quality)


def render_plot_export_controls(
    fig: go.Figure,
    *,
    key: str,
    lang: str = DEFAULT_LANG,
    default_stem: str = "spectrum",
) -> None:
    """Collapsed-friendly export block for Plot settings expanders."""
    st.markdown(f"**{t('export_graph', lang)}**")
    labeled = t("export_graph_help", lang)
    if labeled:
        st.caption(labeled)

    fmt_labels = {
        "png": "PNG",
        "jpeg": "JPEG",
        "tif": "TIFF",
    }
    c1, c2, c3 = st.columns(3)
    with c1:
        fmt_key = st.selectbox(
            t("export_format", lang),
            options=list(fmt_labels.keys()),
            format_func=lambda k: fmt_labels[k],
            key=f"{key}_exp_fmt",
        )
    with c2:
        width_in = st.number_input(
            t("export_width_in", lang),
            min_value=1.0,
            max_value=20.0,
            value=8.0,
            step=0.5,
            key=f"{key}_exp_win",
        )
    with c3:
        height_in = st.number_input(
            t("export_height_in", lang),
            min_value=1.0,
            max_value=16.0,
            value=5.0,
            step=0.5,
            key=f"{key}_exp_hin",
        )

    d1, d2 = st.columns(2)
    with d1:
        dpi = st.number_input(
            t("export_dpi", lang),
            min_value=72,
            max_value=600,
            value=300,
            step=50,
            key=f"{key}_exp_dpi",
        )
    with d2:
        jpeg_q = 95
        if fmt_key == "jpeg":
            jpeg_q = int(
                st.slider(
                    t("export_jpeg_quality", lang),
                    min_value=50,
                    max_value=100,
                    value=95,
                    key=f"{key}_exp_jq",
                )
            )

    width_px = inches_to_pixels(width_in, int(dpi))
    height_px = inches_to_pixels(height_in, int(dpi))
    st.caption(
        t("export_pixels_hint", lang).format(w=width_px, h=height_px, dpi=int(dpi))
    )

    bytes_key = f"{key}_export_bytes"
    name_key = f"{key}_export_name"
    mime_key = f"{key}_export_mime"
    err_key = f"{key}_export_error"
    warn_key = f"{key}_export_warn"

    if st.button(t("export_prepare", lang), key=f"{key}_exp_prep"):
        try:
            result = rasterize_figure(
                fig,
                width_px=width_px,
                height_px=height_px,
                scale=1.0,
                dpi=int(dpi),
                width_in=float(width_in),
                height_in=float(height_in),
            )
            data = _encode_from_png(result.data, fmt_key, jpeg_q)  # type: ignore[arg-type]
            stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in default_stem).strip("_") or "spectrum"
            st.session_state[bytes_key] = data
            st.session_state[name_key] = f"{stem}.{_EXT[fmt_key]}"
            st.session_state[mime_key] = _MIME[fmt_key]
            st.session_state.pop(err_key, None)
            if result.warning:
                st.session_state[warn_key] = result.warning
            else:
                st.session_state.pop(warn_key, None)
            st.success(t("export_ready", lang).format(n=len(data)))
        except Exception as exc:
            st.session_state.pop(bytes_key, None)
            st.session_state[err_key] = str(exc)
            st.session_state.pop(warn_key, None)
            st.error(t("export_failed", lang).format(err=exc))

    if st.session_state.get(err_key) and bytes_key not in st.session_state:
        st.error(t("export_failed", lang).format(err=st.session_state[err_key]))
    if st.session_state.get(warn_key):
        st.warning(st.session_state[warn_key])

    payload = st.session_state.get(bytes_key)
    if payload:
        st.download_button(
            label=t("export_download", lang),
            data=payload,
            file_name=st.session_state.get(name_key, f"{default_stem}.png"),
            mime=st.session_state.get(mime_key, "image/png"),
            key=f"{key}_exp_dl",
        )
