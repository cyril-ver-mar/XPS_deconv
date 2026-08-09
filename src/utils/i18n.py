"""Minimal EN/RU i18n helper (Layer 1). Default language: Russian."""

from __future__ import annotations

from typing import Dict

DEFAULT_LANG = "ru"

# Key → {en, ru}
STRINGS: Dict[str, Dict[str, str]] = {
    "app_title": {"en": "XPS-Deconv", "ru": "XPS-Deconv"},
    "nav_home": {"en": "Home", "ru": "Главная"},
    "nav_import": {"en": "Import VGD", "ru": "Импорт VGD"},
    "nav_interactive": {"en": "Interactive", "ru": "Интерактив"},
    "nav_region": {"en": "Region crop", "ru": "Обрезка области"},
    "nav_baseline": {"en": "Baseline", "ru": "Базовая линия"},
    "nav_fit": {"en": "Deconvolution", "ru": "Деконволюция"},
    "nav_sequence": {"en": "Fit sequence", "ru": "Последовательность фитов"},
    "nav_peaks": {"en": "Peak library", "ru": "Библиотека пиков"},
    "nav_sessions": {"en": "Sessions / Export", "ru": "Сессии / Экспорт"},
    "nav_settings": {"en": "Settings", "ru": "Настройки"},
    "nav_docs": {"en": "Documentation", "ru": "Документация"},
    "docs_caption": {
        "en": "Standardized guide: install, every page, architecture, science notes, troubleshooting.",
        "ru": "Стандартное руководство: установка, все страницы, архитектура, наука, устранение проблем.",
    },
    "docs_full": {"en": "Overview", "ru": "Обзор"},
    "docs_more": {"en": "More…", "ru": "Ещё…"},
    "docs_footer": {
        "en": "Source files: `docs/USER_GUIDE.md` / `docs/USER_GUIDE_ru.md` · Decisions: `docs/DECISIONS.md`",
        "ru": "Исходники: `docs/USER_GUIDE.md` / `docs/USER_GUIDE_ru.md` · Решения: `docs/DECISIONS.md`",
    },
    "nav_group_main": {"en": "Main", "ru": "Главное"},
    "nav_group_analysis": {"en": "Analysis", "ru": "Анализ"},
    "nav_group_settings": {"en": "System", "ru": "Система"},
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
    "cancel_requested": {"en": "Cancel requested", "ru": "Запрошена отмена"},
    "exit_app": {"en": "Stop server", "ru": "Остановить сервер"},
    "stopping": {"en": "Stopping…", "ru": "Остановка…"},
    # Home
    "home_intro_en": {
        "en": "",
        "ru": "",
    },
    "workflow": {"en": "Workflow", "ru": "Порядок работы"},
    "helpers_hint": {
        "en": "Helpers: click ❔ next to parameters. Language: sidebar EN/RU.",
        "ru": "Подсказки: ❔ у параметров. Язык — в боковой панели (EN/RU).",
    },
    # Common
    "save": {"en": "Save", "ru": "Сохранить"},
    "delete": {"en": "Delete", "ru": "Удалить"},
    "create": {"en": "Create", "ru": "Создать"},
    "reset": {"en": "Reset", "ru": "Сбросить"},
    "apply": {"en": "Apply", "ru": "Применить"},
    "preview": {"en": "Preview", "ru": "Превью"},
    "method": {"en": "Method", "ru": "Метод"},
    "window": {"en": "Window", "ru": "Окно"},
    "core_level": {"en": "Core level", "ru": "Уровень (core level)"},
    "peak_name": {"en": "Peak name", "ru": "Имя пика"},
    "be_ev": {"en": "BE (eV)", "ru": "BE (эВ)"},
    "peaks": {"en": "Peaks", "ru": "Пики"},
    "constraints": {"en": "Constraints (on/off)", "ru": "Ограничения (вкл/выкл)"},
    "fit_stats": {"en": "Fit statistics", "ru": "Статистика фита"},
    "peak_table": {"en": "Peak table", "ru": "Таблица пиков"},
    "plot_settings": {"en": "Plot settings", "ru": "Настройки графика"},
    "invert_x": {"en": "Invert X axis", "ru": "Инвертировать ось X"},
    "fit_all_view": {"en": "Fit all data in view", "ru": "Показать все данные"},
    "reset_view": {"en": "Reset view", "ru": "Сбросить вид"},
    "fill_alpha": {"en": "Fill transparency", "ru": "Прозрачность заливки"},
    "show_traces": {"en": "Show / hide traces", "ru": "Показать / скрыть кривые"},
    "trace_raw": {"en": "Raw", "ru": "Сырой"},
    "trace_denoised": {"en": "Denoised", "ru": "Сглаженный"},
    "trace_baseline": {"en": "Baseline", "ru": "Базовая линия"},
    "trace_corrected": {"en": "Corrected", "ru": "После baseline"},
    "trace_total_fit": {"en": "Total fit", "ru": "Суммарный фит"},
    "trace_previous": {"en": "Previous fit (grey)", "ru": "Прошлый фит (серый)"},
    "trace_components": {"en": "Components", "ru": "Компоненты"},
    "trace_fills": {"en": "Integral fills", "ru": "Заливки площадей"},
    "x_min": {"en": "X min", "ru": "X мин"},
    "x_max": {"en": "X max", "ru": "X макс"},
    "y_min": {"en": "Y min", "ru": "Y мин"},
    "y_max": {"en": "Y max", "ru": "Y макс"},
    "empty_spectrum": {"en": "Empty spectrum — nothing to plot.", "ru": "Пустой спектр — нечего рисовать."},
    # Peak library
    "peak_lib_caption": {
        "en": "Edit peak types (core levels) and peaks (name + BE). Restore defaults anytime.",
        "ru": "Редактируйте типы пиков (уровни) и сами пики (имя + BE). В любой момент можно восстановить библиотеку по умолчанию.",
    },
    "new_core_level": {"en": "New core level name", "ru": "Имя нового уровня"},
    "create_core": {"en": "Create core level", "ru": "Создать уровень"},
    "delete_core": {"en": "Delete this core level", "ru": "Удалить этот уровень"},
    "save_core": {"en": "Save core level", "ru": "Сохранить уровень"},
    "reset_core_defaults": {"en": "Reset this core to defaults", "ru": "Сбросить уровень к умолчанию"},
    "reset_lib_defaults": {"en": "Restore entire library to defaults", "ru": "Восстановить всю библиотеку по умолчанию"},
    "core_saved": {"en": "Saved {n} peak(s) for {core}", "ru": "Сохранено пиков: {n} для {core}"},
    "core_deleted": {"en": "Deleted core level {core}", "ru": "Удалён уровень {core}"},
    "lib_restored": {"en": "Library restored to defaults", "ru": "Библиотека восстановлена по умолчанию"},
    "add_option_new": {"en": "— new core level —", "ru": "— новый уровень —"},
    "confirm_delete_core": {
        "en": "Really delete this core level and all its peaks?",
        "ru": "Точно удалить этот уровень и все его пики?",
    },
    "confirm_restore_lib": {
        "en": "Replace the whole library with built-in defaults?",
        "ru": "Заменить всю библиотеку встроенными значениями по умолчанию?",
    },
    # Uncertainty panel
    "uncert_title": {
        "en": "Local mean / uncertainty + selected PseudoVoigt sum",
        "ru": "Локальное среднее / неопределённость + сумма выбранных PseudoVoigt",
    },
    "uncert_caption": {
        "en": "Black = original · Red = rolling mean · Green = ± local σ · Dotted = peaks · Purple = selected sum · Dashed = total fit.",
        "ru": "Чёрный = исходный · Красный = скользящее среднее · Зелёный = ± локальная σ · Пунктир = пики · Фиолетовый = сумма выбранных · Штрих = полный фит.",
    },
    "uncert_peaks_sum": {"en": "Peaks included in sum", "ru": "Пики в сумме"},
    "uncert_no_sel": {
        "en": "No peaks selected — purple sum is zero.",
        "ru": "Пики не выбраны — фиолетовая сумма равна нулю.",
    },
    "uncert_add_peaks": {
        "en": "Add peaks (and optionally run a fit) to overlay PseudoVoigt components.",
        "ru": "Добавьте пики (и при желании запустите фит), чтобы наложить PseudoVoigt.",
    },
    "uncert_window": {"en": "Adjacent-point window", "ru": "Окно соседних точек"},
    "uncert_nsigma": {"en": "Uncertainty band (± n·σ)", "ru": "Полоса неопределённости (± n·σ)"},
    "uncert_metric": {
        "en": "|data − selected sum| ≤ ±{n}σ",
        "ru": "|данные − сумма выбранных| ≤ ±{n}σ",
    },
    "uncert_count": {"en": "Count", "ru": "Число точек"},
    # Import / interactive / common workflow
    "projects_spectra": {"en": "Projects & spectra", "ru": "Проекты и спектры"},
    "project_section": {"en": "1. Project", "ru": "1. Проект"},
    "new_project_name": {"en": "New project name", "ru": "Имя нового проекта"},
    "create_project": {"en": "Create project", "ru": "Создать проект"},
    "load_existing": {"en": "Load existing", "ru": "Загрузить существующий"},
    "load_project": {"en": "Load project", "ru": "Загрузить проект"},
    "delete_project": {"en": "Delete project", "ru": "Удалить проект"},
    "no_projects": {"en": "No saved projects yet.", "ru": "Пока нет сохранённых проектов."},
    "need_project": {
        "en": "Create or load a project to upload spectra.",
        "ru": "Создайте или загрузите проект, чтобы добавить спектры.",
    },
    "project_notes": {"en": "Project notes", "ru": "Заметки проекта"},
    "save_notes": {"en": "Save project notes", "ru": "Сохранить заметки"},
    "upload_section": {"en": "2. Upload VGD files (many allowed)", "ru": "2. Загрузка VGD (можно несколько)"},
    "vgd_files": {"en": "VGD files", "ru": "Файлы VGD"},
    "or_paths": {"en": "Or paste local paths (one per line)", "ru": "Или пути на диске (по одному в строке)"},
    "add_files": {"en": "Add files to project", "ru": "Добавить файлы в проект"},
    "pick_spectrum": {"en": "3. Pick active spectrum", "ru": "3. Выбрать активный спектр"},
    "active_spectrum": {"en": "Active spectrum", "ru": "Активный спектр"},
    "set_active": {"en": "Set as active", "ru": "Сделать активным"},
    "lib_levels_list": {"en": "Core levels in library", "ru": "Уровни в библиотеке"},
    "n_peaks_col": {"en": "n_peaks", "ru": "число_пиков"},
    "fit_sequence_title": {"en": "Fit sequence compare", "ru": "Сравнение последовательности фитов"},
    "fit_sequence_caption": {
        "en": "Each Run on the Deconvolution page appends a snapshot. Compare graphs and tables here.",
        "ru": "Каждый запуск на странице деконволюции добавляет снимок. Сравнивайте графики и таблицы здесь.",
    },
    "no_fits_yet": {
        "en": "No fits in the sequence yet. Run deconvolution at least once.",
        "ru": "В последовательности ещё нет фитов. Запустите деконволюцию хотя бы раз.",
    },
    "load_spectrum_first": {"en": "Load a spectrum first.", "ru": "Сначала загрузите спектр."},
    "project_root": {"en": "Project root", "ru": "Корень проекта"},
    "data_dir": {"en": "Data dir", "ru": "Каталог данных"},
    "exports_dir": {"en": "Exports dir", "ru": "Каталог экспорта"},
    "interactive_title": {
        "en": "Interactive deconvolution workspace",
        "ru": "Интерактивное рабочее пространство",
    },
    "interactive_caption": {
        "en": "Tune denoise, baseline, peaks and constraints in one place.",
        "ru": "Настройка denoise, baseline, пиков и ограничений в одном месте.",
    },
    "select_spectrum_import": {
        "en": "Select an active spectrum in Projects & Import first.",
        "ru": "Сначала выберите активный спектр на странице импорта.",
    },
    "denoise": {"en": "Denoise", "ru": "Сглаживание"},
    "baseline": {"en": "Baseline", "ru": "Базовая линия"},
    "model": {"en": "Model", "ru": "Модель"},
    "peak_model": {"en": "Peak model", "ru": "Модель пика"},
    "add_lib_peaks": {"en": "Add selected library peaks", "ru": "Добавить выбранные из библиотеки"},
    "add_blank_peak": {"en": "Add blank peak", "ru": "Добавить пустой пик"},
    "run_fit": {"en": "Run deconvolution", "ru": "Запустить деконволюцию"},
    "apply_refit": {"en": "Apply / Refit now", "ru": "Применить / Пересчитать"},
    "save_named_fit": {"en": "Save named fit", "ru": "Сохранить именованный фит"},
    "settings_paths": {"en": "Paths", "ru": "Пути"},
    "language_label": {"en": "Language", "ru": "Язык"},
    "save_session": {"en": "Save session", "ru": "Сохранить сессию"},
    "session_name": {"en": "Session name", "ru": "Имя сессии"},
    "notes": {"en": "Notes", "ru": "Заметки"},
    "save_current_session": {"en": "Save current session", "ru": "Сохранить текущую сессию"},
    "load_session": {"en": "Load session", "ru": "Загрузить сессию"},
    "no_sessions": {"en": "No indexed sessions yet.", "ru": "Пока нет сессий в индексе."},
    "export": {"en": "Export", "ru": "Экспорт"},
}



def t(key: str, lang: str | None = None, **fmt) -> str:
    """Translate ``key`` for ``lang`` (default Russian). Optional ``.format`` kwargs."""
    if lang is None:
        lang = DEFAULT_LANG
    entry = STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("en") or key
    if fmt:
        try:
            return text.format(**fmt)
        except (KeyError, ValueError):
            return text
    return text
