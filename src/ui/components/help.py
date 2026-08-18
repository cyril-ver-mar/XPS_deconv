"""Help texts and ❔ popover helper (Layer 5)."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from src.utils.i18n import DEFAULT_LANG

HELP: dict[str, dict[str, str]] = {
    "invert_x": {
        "en": "Reverse the binding-energy axis. XPS is usually plotted high→low BE (right to left).",
        "ru": "Инвертировать ось энергии связи. В XPS обычно рисуют от высоких BE к низким.",
    },
    "axis_x": {
        "en": "Set the visible Binding Energy window (eV). Use Reset view to restore the full data range.",
        "ru": "Видимый диапазон энергии связи (эВ). «Сбросить вид» возвращает полный диапазон данных.",
    },
    "axis_y": {
        "en": "Set the visible intensity range. Use Reset view to restore autoscaling from the data.",
        "ru": "Видимый диапазон интенсивности. «Сбросить вид» возвращает авто-масштаб по данным.",
    },
    "region_crop": {
        "en": "Crop to one ROI for fitting. Only points inside BE min–max are kept as the active spectrum.",
        "ru": "Обрезка одной области для фита. В активный спектр попадают только точки внутри BE min–max.",
    },
    "region_preset": {
        "en": "Quick BE windows for common core levels (C1s, O1s, …). Still editable after apply.",
        "ru": "Быстрые окна BE для типичных уровней (C1s, O1s, …). После применения можно править.",
    },
    "baseline_method": {
        "en": "How the background under the peaks is estimated and subtracted. See demo plots for each method.",
        "ru": "Как оценивается и вычитается фон под пиками. Смотрите демо-графики для каждого метода.",
    },
    "edge_fraction": {
        "en": "For median baselines: fraction of the spectrum at each end treated as peak-free noise windows.",
        "ru": "Для медианных baseline: доля спектра на каждом краю как окно шума без пиков.",
    },
    "manual_bg": {
        "en": "Extra BE intervals that contain only background. Medians inside these windows define the noise floor.",
        "ru": "Доп. интервалы BE только с фоном. Медианы в них задают уровень шума.",
    },
    "poly_degree": {
        "en": "Polynomial order when fitting only the spectral edges (polynomial_edges method).",
        "ru": "Степень полинома при фите только по краям спектра (метод polynomial_edges).",
    },
    "rolling_window": {
        "en": "Odd window length for rolling-median / related smooth baselines. Larger = smoother background.",
        "ru": "Нечётный размер окна для rolling-median. Больше — более гладкий фон.",
    },
    "shirley": {
        "en": "Shirley: iterative step background that grows with integrated peak area — classic XPS for metallic edges.",
        "ru": "Shirley: итерационный ступенчатый фон, растущий с площадью пика — классика XPS.",
    },
    "tougaard": {
        "en": "Tougaard: inelastic-loss inspired background. B and C shape the loss function.",
        "ru": "Tougaard: фон по модели неупругих потерь. B и C задают форму функции потерь.",
    },
    "denoise_method": {
        "en": "Optional smoothing before baseline/fit. Does not replace baseline — it only reduces point noise.",
        "ru": "Опциональное сглаживание до baseline/фита. Не заменяет baseline — только убирает точечный шум.",
    },
    "denoise_window": {
        "en": "Odd kernel size. Too large blurs real peaks; too small leaves noise.",
        "ru": "Нечётный размер ядра. Слишком большой размывает пики; слишком малый оставляет шум.",
    },
    "denoise_savgol_poly": {
        "en": "Savitzky–Golay polynomial order (must be < window). 2–3 is typical.",
        "ru": "Порядок полинома Savitzky–Golay (должен быть < окна). Обычно 2–3.",
    },
    "peak_model": {
        "en": "Line shape for each peak: Gaussian, Lorentzian, Voigt (convolution), or PseudoVoigt (GL mix).",
        "ru": "Форма линии: Gaussian, Lorentzian, Voigt (свёртка) или PseudoVoigt (смесь GL).",
    },
    "tolerance": {
        "en": "Allowed shift of peak center during fit (±eV). 0 means the center is fixed (not floated).",
        "ru": "Допустимый сдвиг центра пика при фите (±эВ). 0 — центр зафиксирован.",
    },
    "fix_center": {
        "en": "If on, peak position does not move in the fit (same as tolerance = 0).",
        "ru": "Если включено, положение пика не двигается при фите (как tolerance = 0).",
    },
    "fix_fwhm": {
        "en": "If on, peak width (via sigma/FWHM) is held at the guess and not optimized.",
        "ru": "Если включено, ширина пика (sigma/FWHM) остаётся на начальном значении.",
    },
    "shared_sigma": {
        "en": "Force all peaks to share the same sigma (common width constraint).",
        "ru": "Все пики делят одну и ту же sigma (общая ширина).",
    },
    "link_group": {
        "en": "Peaks with the same group id are linked as a doublet/multiplet for constraints.",
        "ru": "Пики с одним id группы связываются как дублет/мультиплет.",
    },
    "link_delta": {
        "en": "Fixed binding-energy splitting (eV) between linked peaks (e.g. Ag 3d ≈ 6.0 eV).",
        "ru": "Фиксированное расщепление по BE (эВ) между связанными пиками (напр. Ag 3d ≈ 6.0 эВ).",
    },
    "gl_fraction": {
        "en": "PseudoVoigt mix: 0 ≈ Gaussian, 1 ≈ Lorentzian (GL(m)-like).",
        "ru": "Смесь PseudoVoigt: 0 ≈ Gaussian, 1 ≈ Lorentzian (аналог GL(m)).",
    },
    "show_traces": {
        "en": "Toggle which curves are drawn: raw, denoised, baseline, corrected, total fit, components, fills.",
        "ru": "Какие кривые рисовать: сырой, сглаженный, базовая линия, после baseline, суммарный фит, компоненты, заливки.",
    },
    "fill_alpha": {
        "en": "Transparency of filled peak areas (0 = invisible, 1 = opaque).",
        "ru": "Прозрачность заливки площадей пиков (0 — не видно, 1 — непрозрачно).",
    },
    "plot_style": {
        "en": "Fonts, axis names, colors, line widths, and grid (including minor grid) update the plot above immediately. Export uses the same style. Compact Y ticks (25k) are optional — off by default (full numbers).",
        "ru": "Шрифты, подписи осей, цвета, толщины линий и сетка сразу меняют график выше. Экспорт использует то же оформление. Сокращение интенсивности (25k) — по желанию; по умолчанию полные числа.",
    },
    "element_bands": {
        "en": "Shaded typical binding-energy windows for common core levels (same ranges as region presets). Enable each line and pick a color. The label sits above the band.",
        "ru": "Типичные окна энергии связи для уровней (те же диапазоны, что у пресетов области). Включите нужные и выберите цвет. Подпись — над полосой.",
    },
    "peak_be_labels": {
        "en": "Label each fitted component at the binding energy of its intensity maximum. Choose how many decimal digits to show.",
        "ru": "Подписать каждый компонент в энергии связи его максимума интенсивности. Число знаков после запятой задаётся отдельно.",
    },
    "project": {
        "en": "A project stores many uploaded VGD spectra and your analysis state so you can reload and continue later.",
        "ru": "Проект хранит много загруженных VGD-спектров и состояние анализа — можно продолжить позже.",
    },
}


def help_mark(key: str, lang: str = DEFAULT_LANG, label: str = "❔") -> None:
    """Inline ❔ popover with help text."""
    text = HELP.get(key, {}).get(lang) or HELP.get(key, {}).get("en") or key
    with st.popover(label, help=text[:80] if text else None):
        st.markdown(text)


def labeled_help(title: str, key: str, lang: str = DEFAULT_LANG) -> None:
    c1, c2 = st.columns([0.82, 0.18])
    with c1:
        st.markdown(f"**{title}**")
    with c2:
        help_mark(key, lang)
