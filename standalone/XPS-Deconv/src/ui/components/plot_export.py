"""Export Plotly figures to PNG / JPEG / TIFF with adjustable size and DPI."""

from __future__ import annotations

import io
from typing import Literal

import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from src.utils.i18n import t

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


def figure_to_image_bytes(
    fig: go.Figure,
    *,
    fmt: ExportFormat,
    width_px: int,
    height_px: int,
    scale: float = 1.0,
    jpeg_quality: int = 95,
) -> bytes:
    """Rasterize ``fig`` via Kaleido; convert to TIFF/JPEG with Pillow when needed.

    ``width_px`` / ``height_px`` are the base layout size; ``scale`` multiplies
    resolution (e.g. scale=2 → 2× pixels for publication DPI).
    """
    width_px = max(100, int(width_px))
    height_px = max(100, int(height_px))
    scale = max(0.5, float(scale))
    jpeg_quality = max(40, min(100, int(jpeg_quality)))

    export_fig = go.Figure(fig)
    export_fig.update_layout(
        width=width_px,
        height=height_px,
        autosize=False,
        # Drop Streamlit-friendly margins that waste print space
        margin=dict(l=60, r=20, t=40, b=60),
    )

    try:
        png_bytes = export_fig.to_image(
            format="png",
            width=width_px,
            height=height_px,
            scale=scale,
        )
    except Exception as exc:  # kaleido missing or engine failure
        raise RuntimeError(
            "Image export requires the kaleido package. "
            "Install with: pip install kaleido"
        ) from exc

    if fmt == "png":
        return bytes(png_bytes)

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

    # TIFF (lossless)
    if img.mode == "P":
        img = img.convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="TIFF", compression="tiff_lzw")
    return buf.getvalue()


def inches_to_pixels(inches: float, dpi: int) -> int:
    return max(100, int(round(float(inches) * float(dpi))))


def render_plot_export_controls(
    fig: go.Figure,
    *,
    key: str,
    lang: str = "en",
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

    if st.button(t("export_prepare", lang), key=f"{key}_exp_prep"):
        try:
            data = figure_to_image_bytes(
                fig,
                fmt=fmt_key,  # type: ignore[arg-type]
                width_px=width_px,
                height_px=height_px,
                scale=1.0,
                jpeg_quality=jpeg_q,
            )
            stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in default_stem).strip("_") or "spectrum"
            st.session_state[bytes_key] = data
            st.session_state[name_key] = f"{stem}.{_EXT[fmt_key]}"
            st.session_state[mime_key] = _MIME[fmt_key]
            st.session_state.pop(err_key, None)
            st.success(t("export_ready", lang).format(n=len(data)))
        except Exception as exc:
            st.session_state.pop(bytes_key, None)
            st.session_state[err_key] = str(exc)
            st.error(t("export_failed", lang).format(err=exc))

    if st.session_state.get(err_key) and bytes_key not in st.session_state:
        st.error(t("export_failed", lang).format(err=st.session_state[err_key]))

    payload = st.session_state.get(bytes_key)
    if payload:
        st.download_button(
            label=t("export_download", lang),
            data=payload,
            file_name=st.session_state.get(name_key, f"{default_stem}.png"),
            mime=st.session_state.get(mime_key, "image/png"),
            key=f"{key}_exp_dl",
        )
