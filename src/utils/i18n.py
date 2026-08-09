"""Minimal EN/RU i18n helper (Layer 1)."""

from __future__ import annotations

from typing import Dict

# Key → {en, ru}
STRINGS: Dict[str, Dict[str, str]] = {
    "app_title": {"en": "XPS-Deconv", "ru": "XPS-Deconv"},
    "nav_home": {"en": "Home", "ru": "Главная"},
    "nav_import": {"en": "Import VGD", "ru": "Импорт VGD"},
    "nav_region": {"en": "Region crop", "ru": "Обрезка области"},
    "nav_baseline": {"en": "Baseline", "ru": "Базовая линия"},
    "nav_fit": {"en": "Deconvolution", "ru": "Деконволюция"},
    "nav_peaks": {"en": "Peak library", "ru": "Библиотека пиков"},
    "nav_sessions": {"en": "Sessions / Export", "ru": "Сессии / Экспорт"},
    "nav_settings": {"en": "Settings", "ru": "Настройки"},
    "lang": {"en": "Language", "ru": "Язык"},
    "need_spectrum": {
        "en": "Load a VGD spectrum on the Import page first.",
        "ru": "Сначала загрузите спектр VGD на странице импорта.",
    },
    "need_region": {
        "en": "Set an active region on the Region crop page first.",
        "ru": "Сначала задайте активную область на странице обрезки.",
    },
    "baseline_help_median": {
        "en": (
            "Noise-floor median: estimate background in peak-free windows "
            "(auto edges and/or manual), take the median intensity, then build "
            "a baseline and subtract it. Robust to outliers unlike the mean."
        ),
        "ru": (
            "Медиана шума: оценить фон в окнах без пиков (авто края и/или вручную), "
            "взять медиану интенсивности и построить базовую линию. Устойчивее среднего."
        ),
    },
    "shirley_help": {
        "en": "Shirley: background rises with integrated peak area (classic XPS step).",
        "ru": "Shirley: фон растёт пропорционально накопленной площади пика (классика XPS).",
    },
    "tougaard_help": {
        "en": "Tougaard: inelastic-loss inspired background; tune B and C parameters.",
        "ru": "Tougaard: фон по модели неупругих потерь; параметры B и C настраиваются.",
    },
    "cancel": {"en": "Cancel long job", "ru": "Отменить долгую задачу"},
    "exit_app": {"en": "Stop server", "ru": "Остановить сервер"},
}


def t(key: str, lang: str = "en") -> str:
    entry = STRINGS.get(key, {})
    return entry.get(lang) or entry.get("en") or key
