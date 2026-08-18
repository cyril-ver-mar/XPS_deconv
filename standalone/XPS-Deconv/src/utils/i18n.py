"""Minimal EN/RU i18n helper (Layer 1). Default language: Russian."""

from __future__ import annotations

from typing import Dict

DEFAULT_LANG = "ru"

# Key → {en, ru}
STRINGS: Dict[str, Dict[str, str]] = {
    "app_title": {"en": "XPS-Deconv", "ru": "XPS-Deconv"},
    "app_version": {"en": "Version", "ru": "Версия"},
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
        "en": "Source files: `docs/USER_GUIDE.md` / `docs/USER_GUIDE_ru.md`",
        "ru": "Исходники: `docs/USER_GUIDE.md` / `docs/USER_GUIDE_ru.md`",
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
    "export_graph": {"en": "Export graph", "ru": "Экспорт графика"},
    "export_graph_help": {
        "en": "Raster export for papers/slides (matplotlib, no browser). Size in inches × DPI → pixel resolution.",
        "ru": "Растровый экспорт для статей/слайдов (matplotlib, без браузера). Размер в дюймах × DPI → разрешение в пикселях.",
    },
    "export_format": {"en": "Format", "ru": "Формат"},
    "export_width_in": {"en": "Width (in)", "ru": "Ширина (дюйм)"},
    "export_height_in": {"en": "Height (in)", "ru": "Высота (дюйм)"},
    "export_dpi": {"en": "DPI (resolution)", "ru": "DPI (разрешение)"},
    "export_jpeg_quality": {"en": "JPEG quality", "ru": "Качество JPEG"},
    "export_pixels_hint": {
        "en": "Output size: {w} × {h} px at {dpi} DPI",
        "ru": "Размер файла: {w} × {h} пикс. при {dpi} DPI",
    },
    "export_prepare": {"en": "Prepare image", "ru": "Подготовить изображение"},
    "export_download": {"en": "Download image", "ru": "Скачать изображение"},
    "export_ready": {"en": "Ready ({n} bytes). Click Download.", "ru": "Готово ({n} байт). Нажмите «Скачать»."},
    "export_failed": {"en": "Export failed: {err}", "ru": "Ошибка экспорта: {err}"},
    "plot_tab_view": {"en": "View", "ru": "Вид"},
    "plot_tab_style": {"en": "Style", "ru": "Оформление"},
    "plot_tab_export": {"en": "Export", "ru": "Экспорт"},
    "plot_style_preview_hint": {
        "en": "Changes apply to the plot above immediately (preview).",
        "ru": "Изменения сразу видны на графике выше (превью).",
    },
    "plot_appearance": {"en": "Appearance", "ru": "Внешний вид"},
    "plot_title": {"en": "Plot title", "ru": "Заголовок графика"},
    "plot_x_title": {"en": "X axis name", "ru": "Подпись оси X"},
    "plot_y_title": {"en": "Y axis name", "ru": "Подпись оси Y"},
    "plot_font": {"en": "Font", "ru": "Шрифт"},
    "plot_font_size": {"en": "Font size", "ru": "Размер шрифта"},
    "plot_title_size": {"en": "Title size", "ru": "Размер заголовка"},
    "plot_tick_size": {"en": "Tick size", "ru": "Размер подписей делений"},
    "plot_legend_size": {"en": "Legend size", "ru": "Размер легенды"},
    "plot_axis_color": {"en": "Axis color", "ru": "Цвет осей"},
    "plot_paper_bg": {"en": "Page background", "ru": "Фон страницы"},
    "plot_plot_bg": {"en": "Plot background", "ru": "Фон графика"},
    "plot_grid_color": {"en": "Grid color", "ru": "Цвет сетки"},
    "plot_grid": {"en": "Show grid (major + minor)", "ru": "Показать сетку (основная + дополнительная)"},
    "plot_show_legend": {"en": "Show legend", "ru": "Показать легенду"},
    "plot_compact_y": {
        "en": "Compact intensity ticks (25k)",
        "ru": "Сокращать интенсивность (25k)",
    },
    "plot_element_bands": {
        "en": "Element BE regions",
        "ru": "Области элементов (BE)",
    },
    "plot_element_bands_show": {
        "en": "Show typical core-level windows",
        "ru": "Показать типичные окна уровней",
    },
    "plot_band_color": {"en": "Color", "ru": "Цвет"},
    "plot_line_styles": {"en": "Line colors and widths", "ru": "Цвета и толщины линий"},
    "plot_line_width": {"en": "Width", "ru": "Толщина"},
    "plot_component_width": {"en": "Component line width", "ru": "Толщина линий компонентов"},
    "plot_component_colors": {"en": "Component colors", "ru": "Цвета компонентов"},
    "plot_reset_style": {"en": "Reset style to defaults", "ru": "Сбросить оформление"},
    "plot_peak_be_labels": {
        "en": "Show BE at peak maximum",
        "ru": "Подписать BE в максимуме пика",
    },
    "plot_peak_be_digits": {
        "en": "BE digits",
        "ru": "Знаков BE",
    },
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
    # GitHub updates
    "update_available": {
        "en": "**{new}** is available (you have {old}).",
        "ru": "Доступна версия **{new}** (у вас {old}).",
    },
    "update_open_release": {"en": "Open release on GitHub", "ru": "Открыть релиз на GitHub"},
    "update_install_expander": {
        "en": "Download & install update",
        "ru": "Скачать и установить обновление",
    },
    "update_install_help": {
        "en": "Replaces app files from the release zip. Keeps your data/, exports/, and venv/. Restart the app afterward; re-run install if dependencies changed.",
        "ru": "Заменяет файлы приложения из zip-релиза. Сохраняет data/, exports/ и venv/. После этого перезапустите приложение; при смене зависимостей снова запустите install.",
    },
    "update_confirm": {
        "en": "I understand app files will be overwritten (projects/data kept).",
        "ru": "Понимаю: файлы приложения будут перезаписаны (проекты/данные сохранятся).",
    },
    "update_download_install": {
        "en": "Download & install now",
        "ru": "Скачать и установить сейчас",
    },
    "update_working": {"en": "Downloading and installing…", "ru": "Скачивание и установка…"},
    "update_installed": {
        "en": "Update installed. Please stop and restart the app.",
        "ru": "Обновление установлено. Остановите и перезапустите приложение.",
    },
    "update_restart_hint": {
        "en": "Use Stop server in the sidebar, then run again.",
        "ru": "Нажмите «Остановить сервер» в боковой панели, затем запустите снова.",
    },
    "update_failed": {"en": "Update failed: {err}", "ru": "Ошибка обновления: {err}"},
    "update_no_zip": {
        "en": "This release has no standalone .zip asset — open the release page and download manually.",
        "ru": "У этого релиза нет standalone .zip — откройте страницу релиза и скачайте вручную.",
    },
    "update_dismiss": {"en": "Dismiss", "ru": "Скрыть"},
    "update_section": {"en": "Updates", "ru": "Обновления"},
    "update_not_configured": {
        "en": "GitHub repo not set. Put `owner/name` in the `GITHUB_REPO` file (or set XPS_DECONV_GITHUB_REPO).",
        "ru": "Репозиторий GitHub не задан. Укажите `owner/name` в файле `GITHUB_REPO` (или переменной XPS_DECONV_GITHUB_REPO).",
    },
    "update_repo": {"en": "Repository: `{repo}`", "ru": "Репозиторий: `{repo}`"},
    "update_local_remote": {
        "en": "Local: **{local}** · Latest on GitHub: **{remote}**",
        "ru": "Локально: **{local}** · На GitHub: **{remote}**",
    },
    "update_up_to_date": {"en": "You are on the latest release.", "ru": "У вас последняя версия."},
    "update_check_now": {"en": "Check for updates now", "ru": "Проверить обновления сейчас"},
    "update_check_settings_hint": {
        "en": "Open **Settings → Updates** for status and retry.",
        "ru": "Откройте **Настройки → Обновления**, чтобы увидеть статус и повторить проверку.",
    },
    "update_check_detail": {
        "en": "Technical detail: `{detail}`",
        "ru": "Техническая деталь: `{detail}`",
    },
    "update_local_only": {
        "en": "Installed version: **{local}** (latest on GitHub unknown).",
        "ru": "Установленная версия: **{local}** (последняя на GitHub неизвестна).",
    },
    "update_check_network": {
        "en": "Could not connect to GitHub to check for updates. Check internet, proxy, or firewall. ({detail})",
        "ru": "Не удалось подключиться к GitHub для проверки обновлений. Проверьте интернет, прокси или брандмауэр. ({detail})",
    },
    "update_check_timeout": {
        "en": "GitHub did not respond in time while checking for updates. Try again later. ({detail})",
        "ru": "GitHub не ответил вовремя при проверке обновлений. Попробуйте позже. ({detail})",
    },
    "update_check_ssl": {
        "en": "Secure connection to GitHub failed (SSL/certificate). A corporate proxy may intercept HTTPS. ({detail})",
        "ru": "Не удалось установить защищённое соединение с GitHub (SSL/сертификат). Корпоративный прокси может перехватывать HTTPS. ({detail})",
    },
    "update_check_no_releases": {
        "en": "GitHub has no latest release for `{repo}` (repository missing or no releases). ({detail})",
        "ru": "На GitHub нет последнего релиза для `{repo}` (репозиторий не найден или нет релизов). ({detail})",
    },
    "update_check_rate_limit": {
        "en": "GitHub refused the update check (rate limit or access denied). Try again later. ({detail})",
        "ru": "GitHub отклонил проверку обновлений (лимит запросов или нет доступа). Попробуйте позже. ({detail})",
    },
    "update_check_http": {
        "en": "GitHub returned an HTTP error during the update check. ({detail})",
        "ru": "GitHub вернул HTTP-ошибку при проверке обновлений. ({detail})",
    },
    "update_check_bad_response": {
        "en": "GitHub returned an unexpected response during the update check. ({detail})",
        "ru": "GitHub вернул неожиданный ответ при проверке обновлений. ({detail})",
    },
    "update_check_unexpected": {
        "en": "Update check failed with an unexpected error. ({detail})",
        "ru": "Проверка обновлений завершилась неожиданной ошибкой. ({detail})",
    },
    "settings_paths_caption": {
        "en": "Paths are resolved relative to the app folder (no hardcoded machine paths).",
        "ru": "Пути вычисляются относительно папки приложения (без жёстко прошитых абсолютных адресов).",
    },
    # Plot defaults / legend
    "plot_default_x": {"en": "Binding energy (eV)", "ru": "Энергия связи (эВ)"},
    "plot_default_y": {"en": "Intensity", "ru": "Интенсивность"},
    "invert_x_help": {
        "en": "XPS is usually plotted high → low BE",
        "ru": "В XPS обычно рисуют от высоких BE к низким",
    },
    "x_range_label": {"en": "X range (BE, eV)", "ru": "Диапазон X (BE, эВ)"},
    "y_range_label": {"en": "Y range (intensity)", "ru": "Диапазон Y (интенсивность)"},
    "unit_ev": {"en": "eV", "ru": "эВ"},
    "plot_band_range": {
        "en": "{label}  ({x0}–{x1} {unit})",
        "ru": "{label}  ({x0}–{x1} {unit})",
    },
    "trace_full_spectrum": {"en": "Full spectrum", "ru": "Полный спектр"},
    "trace_component_n": {"en": "Component {n}", "ru": "Компонент {n}"},
    "trace_spectrum": {"en": "Spectrum", "ru": "Спектр"},
    # Import
    "what_is_project": {"en": "What is a project?", "ru": "Что такое проект?"},
    "created_project": {"en": "Created {name}", "ru": "Создан проект {name}"},
    "project_loaded": {"en": "Project loaded", "ru": "Проект загружен"},
    "deleted_ok": {"en": "Deleted", "ru": "Удалено"},
    "saved_ok": {"en": "Saved", "ru": "Сохранено"},
    "project_list_item": {
        "en": "{name} ({n} spectra) — {updated}",
        "ru": "{name} ({n} спектров) — {updated}",
    },
    "active_project": {
        "en": "Active project: **{name}** (`{id}`) — {n} spectra",
        "ru": "Активный проект: **{name}** (`{id}`) — спектров: {n}",
    },
    "added_spectra": {"en": "Added {n} spectrum(s)", "ru": "Добавлено спектров: {n}"},
    "no_spectra_yet": {"en": "No spectra in this project yet.", "ru": "В этом проекте пока нет спектров."},
    "active_spectrum_set": {
        "en": "Active spectrum set — continue on Region / Baseline / Deconvolution / Workspace",
        "ru": "Активный спектр выбран — дальше: Обрезка / Базовая линия / Деконволюция / Интерактив",
    },
    # Region crop
    "need_spectrum_import_hint": {
        "en": " Open Projects & Import first.",
        "ru": " Сначала откройте «Проекты и спектры» (импорт).",
    },
    "presets": {"en": "Presets", "ru": "Пресеты"},
    "preset": {"en": "Preset", "ru": "Пресет"},
    "apply_preset": {"en": "Apply preset", "ru": "Применить пресет"},
    "be_min": {"en": "BE min (eV)", "ru": "BE мин (эВ)"},
    "be_max": {"en": "BE max (eV)", "ru": "BE макс (эВ)"},
    "be_min_help": {"en": "Lower BE bound of the ROI", "ru": "Нижняя граница области по BE"},
    "be_max_help": {"en": "Upper BE bound of the ROI", "ru": "Верхняя граница области по BE"},
    "numeric_be_min": {"en": "Numeric BE min", "ru": "BE мин (число)"},
    "numeric_be_max": {"en": "Numeric BE max", "ru": "BE макс (число)"},
    "apply_numeric_range": {"en": "Apply numeric range", "ru": "Применить числовой диапазон"},
    "apply_region": {"en": "Apply region (set active spectrum)", "ru": "Применить область (сделать спектр активным)"},
    "full_spectrum_roi": {"en": "Full spectrum — select ROI", "ru": "Полный спектр — выберите область"},
    "active_region_title": {"en": "Active region", "ru": "Активная область"},
    "region_applied": {
        "en": "Active region {lo:.2f}–{hi:.2f} eV ({n} pts)",
        "ru": "Активная область {lo:.2f}–{hi:.2f} эВ ({n} точек)",
    },
    # Baseline / denoise
    "baseline_demo_expander": {
        "en": "Graphical examples of baseline methods (demo spectrum)",
        "ru": "Примеры методов базовой линии (демо-спектр)",
    },
    "baseline_demo_title": {
        "en": "Baseline methods on a synthetic demo spectrum (blue = data, red = baseline)",
        "ru": "Методы базовой линии на синтетическом спектре (синий — данные, красный — фон)",
    },
    "denoise_method": {"en": "Denoise method", "ru": "Метод сглаживания"},
    "window_size": {"en": "Window size", "ru": "Размер окна"},
    "savgol_poly": {"en": "Savitzky–Golay poly order", "ru": "Порядок полинома Savitzky–Golay"},
    "savgol_poly_short": {"en": "Savgol poly", "ru": "Полином Savgol"},
    "baseline_method": {"en": "Baseline method", "ru": "Метод базовой линии"},
    "auto_edge_fraction": {"en": "Auto edge fraction", "ru": "Доля краёв (авто)"},
    "edge_fraction": {"en": "Edge fraction", "ru": "Доля краёв"},
    "poly_degree": {"en": "Poly degree", "ru": "Степень полинома"},
    "rolling_window": {"en": "Rolling window", "ru": "Скользящее окно"},
    "tougaard_b": {"en": "Tougaard B", "ru": "Tougaard B"},
    "tougaard_c": {"en": "Tougaard C", "ru": "Tougaard C"},
    "manual_bg_windows": {"en": "Manual background windows", "ru": "Ручные окна фона"},
    "n_manual_windows": {"en": "Number of manual windows", "ru": "Число ручных окон"},
    "window_n_min": {"en": "Window {n} min", "ru": "Окно {n} мин"},
    "window_n_max": {"en": "Window {n} max", "ru": "Окно {n} макс"},
    "apply_to_session": {"en": "Apply to session", "ru": "Применить к сессии"},
    "clear_preview": {"en": "Clear preview", "ru": "Сбросить превью"},
    "showing_preview": {
        "en": "Showing **preview** (`{method}`) — not locked until Apply",
        "ru": "Показано **превью** (`{method}`) — не зафиксировано, пока не нажмёте «Применить»",
    },
    "showing_applied": {"en": "Showing **applied** (`{method}`)", "ru": "Показана **применённая** линия (`{method}`)"},
    "no_preview_yet": {
        "en": "No preview/applied baseline yet — click **Preview**",
        "ru": "Превью/применённой базовой линии ещё нет — нажмите **Превью**",
    },
    "baseline_denoise_title": {"en": "Baseline / denoise", "ru": "Базовая линия / сглаживание"},
    "denoise_help_none": {"en": "No smoothing — use raw counts/intensity.", "ru": "Без сглаживания — исходная интенсивность."},
    "denoise_help_median": {
        "en": "Median filter: robust to spikes/outliers; good first choice for XPS noise.",
        "ru": "Медианный фильтр: устойчив к выбросам; хороший старт для шума XPS.",
    },
    "denoise_help_moving_average": {
        "en": "Boxcar average: strong smoothing, can broaden peaks if window is large.",
        "ru": "Скользящее среднее: сильное сглаживание, большое окно уширяет пики.",
    },
    "denoise_help_savgol": {
        "en": "Savitzky–Golay: polynomial smooth that preserves peak shape better than a plain average.",
        "ru": "Savitzky–Golay: полиномиальное сглаживание, лучше сохраняет форму пиков.",
    },
    "denoise_help_wiener": {
        "en": "Wiener filter: adaptive smooth based on local variance (can help mixed noise).",
        "ru": "Фильтр Винера: адаптивное сглаживание по локальной дисперсии.",
    },
    "blurb_none": {"en": "No baseline subtraction.", "ru": "Без вычитания фона."},
    "blurb_median_horizontal": {
        "en": "Median of background windows → flat line (noise floor).",
        "ru": "Медиана окон фона → горизонтальная линия (уровень шума).",
    },
    "blurb_median_linear": {
        "en": "Medians of left/right (or manual) windows → straight baseline (recommended default).",
        "ru": "Медианы левого/правого (или ручных) окон → прямая базовая линия (рекомендуется).",
    },
    "blurb_rolling_median": {
        "en": "Sliding median across the whole curve — smooth under peaks if window is large.",
        "ru": "Скользящая медиана по всей кривой — сглаживает фон под пиками при большом окне.",
    },
    "blurb_asls": {
        "en": "Asymmetric least squares — flexible smooth background.",
        "ru": "Асимметричные наименьшие квадраты — гибкий гладкий фон.",
    },
    "blurb_snip": {
        "en": "SNIP clipping — iteratively peels peaks to reveal background.",
        "ru": "SNIP: итеративно «срезает» пики, оставляя фон.",
    },
    "blurb_linear_endpoints": {
        "en": "Straight line from first to last point (notebook-style).",
        "ru": "Прямая от первой точки к последней.",
    },
    "blurb_polynomial_edges": {
        "en": "Polynomial fit using only edge points.",
        "ru": "Полином только по краевым точкам.",
    },
    "blurb_shirley": {
        "en": "Classic XPS Shirley step under the peak envelope.",
        "ru": "Классический ступенчатый фон Shirley под огибающей пиков.",
    },
    "blurb_tougaard": {
        "en": "Inelastic-loss style Tougaard background (tune B, C).",
        "ru": "Фон Tougaard (неупругие потери); параметры B и C.",
    },
    # Peaks / fit widgets
    "fix_fwhm": {"en": "Fix FWHM", "ru": "Фиксировать FWHM"},
    "fix_fwhm_all": {"en": "Fix FWHM (all peaks)", "ru": "Фиксировать FWHM (все пики)"},
    "fix_fwhm_this": {"en": "Fix FWHM (this peak)", "ru": "Фиксировать FWHM (этот пик)"},
    "shared_sigma": {"en": "Shared sigma", "ru": "Общая sigma"},
    "doublet_links": {"en": "Doublet links", "ru": "Связи дублетов"},
    "enable_doublet_links": {"en": "Enable doublet links", "ru": "Включить связи дублетов"},
    "library_core_level": {"en": "Library core level", "ru": "Уровень из библиотеки"},
    "core_level_library": {"en": "Core level for library", "ru": "Уровень для библиотеки"},
    "add_from_library": {"en": "Add from library", "ru": "Добавить из библиотеки"},
    "add_selected_lib": {"en": "Add selected from library", "ru": "Добавить выбранные из библиотеки"},
    "peak_name_label": {"en": "Name", "ru": "Имя"},
    "center": {"en": "Center", "ru": "Центр"},
    "center_ev": {"en": "Center (eV)", "ru": "Центр (эВ)"},
    "tolerance": {"en": "Tolerance", "ru": "Допуск"},
    "tolerance_pos": {"en": "Tolerance / pos_error", "ru": "Допуск / pos_error"},
    "tolerance_ev": {"en": "Tolerance ±eV (0 = fix center)", "ru": "Допуск ±эВ (0 — зафиксировать центр)"},
    "sigma": {"en": "Sigma", "ru": "Sigma"},
    "sigma_guess": {"en": "Sigma guess", "ru": "Начальная sigma"},
    "fix_center": {"en": "Fix center", "ru": "Фиксировать центр"},
    "gl_fraction": {"en": "GL fraction (pseudovoigt)", "ru": "Доля GL (pseudovoigt)"},
    "link_group": {"en": "Link group", "ru": "Группа связи"},
    "link_group_id": {"en": "Link group id (optional)", "ru": "Id группы связи (необязательно)"},
    "link_dbe": {"en": "Link ΔBE (eV)", "ru": "Связь ΔBE (эВ)"},
    "auto_refit": {"en": "Auto-refit when clicking Apply", "ru": "Автопересчёт при «Применить»"},
    "save_current_fit_as": {"en": "Save current fit as", "ru": "Сохранить текущий фит как"},
    "saved_fit_ok": {"en": "Saved fit `{name}`", "ru": "Фит `{name}` сохранён"},
    "show_saved_fit": {
        "en": "Show saved fit (overlay as previous/grey via load)",
        "ru": "Показать сохранённый фит (серый оверлей через загрузку)",
    },
    "overlay_saved_grey": {"en": "Overlay saved fit (grey)", "ru": "Наложить сохранённый фит (серый)"},
    "load_saved_as_current": {"en": "Load saved fit as current", "ru": "Загрузить сохранённый фит как текущий"},
    "active_peaks_caption": {
        "en": "Active peaks: **{n}**. Default tolerance = 0 (fixed center). Use Delete / Clear all as needed.",
        "ru": "Активных пиков: **{n}**. Допуск по умолчанию = 0 (центр зафиксирован). При необходимости удалите или очистите список.",
    },
    "save_peak_edits": {"en": "Save peak edits", "ru": "Сохранить правки пиков"},
    "clear_all_peaks": {"en": "Clear all peaks", "ru": "Удалить все пики"},
    "no_peaks_yet": {
        "en": "No peaks yet. Add from the library or use **Add blank peak**.",
        "ru": "Пиков ещё нет. Добавьте из библиотеки или **Добавить пустой пик**.",
    },
    "peak_n_header": {"en": "Peak {n}: {name}", "ru": "Пик {n}: {name}"},
    "fit_sequence_label": {"en": "Label for this fit in the sequence", "ru": "Метка этого фита в последовательности"},
    "also_store_named": {"en": "Also store as named saved fit", "ru": "Также сохранить как именованный фит"},
    "fit_starting": {"en": "Starting…", "ru": "Запуск…"},
    "fit_complete": {
        "en": "Fit complete — R={r:.4f}, R²={r2:.4f}",
        "ru": "Фит завершён — R={r:.4f}, R²={r2:.4f}",
    },
    # Fit sequence page
    "show_fits_on_plot": {"en": "Show fits on plot", "ru": "Показать фиты на графике"},
    "selected_fits_overlay": {"en": "Selected fits overlay", "ru": "Наложение выбранных фитов"},
    "peak_table_for": {"en": "Peak table for", "ru": "Таблица пиков для"},
    "load_fit_workspace": {
        "en": "Load this fit into workspace (curves + peaks)",
        "ru": "Загрузить этот фит в рабочее пространство (кривые + пики)",
    },
    "loaded_into_session": {
        "en": "Loaded into session — open Deconvolution or Interactive workspace",
        "ru": "Загружено в сессию — откройте Деконволюцию или Интерактив",
    },
    # Sessions / export page
    "indexed_sessions": {"en": "Indexed sessions", "ru": "Сессии в индексе"},
    "load_selected": {"en": "Load selected", "ru": "Загрузить выбранное"},
    "delete_selected": {"en": "Delete selected", "ru": "Удалить выбранное"},
    "session_loaded": {"en": "Session loaded into memory", "ru": "Сессия загружена в память"},
    "or_load_json": {"en": "Or load JSON path", "ru": "Или путь к JSON"},
    "load_json_path": {"en": "Load JSON path", "ru": "Загрузить JSON"},
    "loaded_ok": {"en": "Loaded", "ru": "Загружено"},
    "saved_path": {"en": "Saved {path}", "ru": "Сохранено: {path}"},
    "export_basename": {"en": "Export basename", "ru": "Имя файла экспорта"},
    "excel_xlsx": {"en": "Excel (.xlsx)", "ru": "Excel (.xlsx)"},
    "peaks_csv": {"en": "Peaks CSV", "ru": "Пики CSV"},
    "png_figure": {"en": "PNG figure", "ru": "Рисунок PNG"},
    "no_spectrum": {"en": "No spectrum", "ru": "Нет спектра"},
    # Uncertainty plot traces
    "uncert_upper": {"en": "Upper (+{n}σ local)", "ru": "Верх (+{n}σ лок.)"},
    "uncert_lower": {"en": "Lower (−{n}σ local)", "ru": "Низ (−{n}σ лок.)"},
    "uncert_original": {"en": "Original", "ru": "Исходный"},
    "uncert_local_mean": {"en": "Local mean", "ru": "Локальное среднее"},
    "uncert_sum_selected": {"en": "Sum of selected peaks", "ru": "Сумма выбранных пиков"},
    "uncert_total_fit": {"en": "Total fit (deconv)", "ru": "Суммарный фит (деконв.)"},
    "uncert_peak_at": {
        "en": "{i}: {name} @ {center:.2f} {unit}",
        "ru": "{i}: {name} @ {center:.2f} {unit}",
    },
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
