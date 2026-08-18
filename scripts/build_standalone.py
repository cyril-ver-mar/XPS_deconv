#!/usr/bin/env python3
"""Build a distributable standalone copy of XPS-Deconv (end-user only).

Usage (from project root):
  python scripts/build_standalone.py

Output:
  standalone/XPS-Deconv/
"""

from __future__ import annotations

import shutil
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "standalone" / "XPS-Deconv"

# Relative paths only — never absolute machine paths.
COPY_TREES = [
    "pages",
    "src",
]
COPY_FILES = [
    "app.py",
    "launch.py",
    "install.sh",
    "install.bat",
    "run.sh",
    "run.bat",
    ".gitignore",
    "VERSION",
    "CHANGELOG.md",
    "GITHUB_REPO.example",
]

SKIP_NAME_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".DS_Store",
}

USER_README = """# XPS-Deconv

Деконволюция XPS-спектров из файлов Thermo Scientific **VGD**.

## Установка и запуск

### macOS / Linux

```bash
./install.sh
./run.sh
```

### Windows

```bat
install.bat
run.bat
```

Откройте в браузере: http://localhost:8501  
Если браузер не открылся сам — вставьте адрес вручную (или http://127.0.0.1:8501).

## Быстрый сценарий

1. **Импорт** — создайте проект, загрузите VGD, выберите спектр  
2. **Интерактив** или пошаговые страницы — обрезка, baseline, пики, фит  
3. **Экспорт** — таблицы и рисунки  

Подробности — страница **Документация** в приложении.

Требуется **Python 3.11**.
"""

USER_GUIDE_RU = """# XPS-Deconv — Руководство пользователя

## 1. Назначение

Приложение для деконволюции XPS из файлов Thermo Scientific **VGD**: проект со многими спектрами, обрезка области, baseline, сглаживание, фит пиков, сравнение и экспорт.

## 2. Установка и запуск

### macOS / Linux

```bash
./install.sh
./run.sh
```

### Windows

```bat
install.bat
run.bat
```

Если браузер не открылся сам, откройте http://localhost:8501 или http://127.0.0.1:8501.

## 3. Страницы

| Страница | Назначение |
|----------|------------|
| Главная | Обзор |
| Импорт VGD | Проект и выбор спектра |
| Интерактив | Всё в одном окне |
| Обрезка | Область энергии связи |
| Базовая линия | Превью и применение baseline |
| Деконволюция | Пики и фит |
| Последовательность | Сравнение фитов |
| Библиотека пиков | Справочник пиков |
| Сессии / Экспорт | Сохранение и выгрузка |
| Документация | Это руководство |
| Настройки | Пути и язык |

## 4. Типичный сценарий

1. Импорт → активный спектр  
2. Обрезка ROI  
3. Baseline (Превью → Применить)  
4. Пики и фит (Интерактив или Деконволюция)  
5. Экспорт  

Подсказки — кнопки ❔ рядом с параметрами.

## 5. Если что-то не работает

| Проблема | Что сделать |
|----------|-------------|
| Нет Python 3.11 | Установите Python 3.11 и повторите install |
| Нет venv | Сначала install.sh / install.bat |
| Порт 8501 занят | Закройте другой Streamlit |
| Браузер не открылся | Откройте http://localhost:8501 вручную |
| Есть обновление | Баннер на главной; или Настройки → Обновления |
| Не удалось проверить GitHub | Баннер с причиной (нет сети / таймаут / SSL / HTTP); Настройки → Обновления → Проверить сейчас |
| Оформление графика | Настройки графика → Оформление (шрифты, оси, цвета, толщины — сразу на графике) |
"""

USER_GUIDE_EN = """# XPS-Deconv — User guide

## 1. Purpose

Deconvolution of Thermo Scientific **VGD** XPS spectra: multi-spectrum projects, ROI crop, baseline, denoise, peak fitting, compare, and export.

## 2. Install & run

### macOS / Linux

```bash
./install.sh
./run.sh
```

### Windows

```bat
install.bat
run.bat
```

If the browser does not open automatically, open http://localhost:8501 or http://127.0.0.1:8501.

## 3. Pages

| Page | Role |
|------|------|
| Home | Overview |
| Import VGD | Project and active spectrum |
| Interactive | All-in-one workspace |
| Region crop | Binding-energy ROI |
| Baseline | Preview and apply |
| Deconvolution | Peaks and fit |
| Fit sequence | Compare fits |
| Peak library | Known peaks |
| Sessions / Export | Save and export |
| Documentation | This guide |
| Settings | Paths and language |

## 4. Typical workflow

1. Import → pick spectrum  
2. Crop ROI  
3. Baseline (Preview → Apply)  
4. Fit peaks  
5. Export  

Use ❔ helpers next to parameters.

## 5. Troubleshooting

| Issue | Fix |
|-------|-----|
| No Python 3.11 | Install 3.11, re-run install |
| No venv | Run install first |
| Port 8501 busy | Stop other Streamlit |
| Browser did not open | Open http://localhost:8501 manually |
| Update available | Banner on launch; or Settings → Updates |
| Cannot check GitHub | Banner names the reason (no network / timeout / SSL / HTTP); Settings → Updates → Check now |
| Plot style | Plot settings → Style (fonts, axis names, colors, widths — live preview) |
"""


def _should_skip(path: Path) -> bool:
    return any(part in SKIP_NAME_PARTS for part in path.parts)


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns(*SKIP_NAME_PARTS, "*.pyc"),
    )


def _chmod_exec(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _strip_dev_from_docs_page(text: str) -> str:
    # Keep page; guides are replaced with user-only markdown.
    return text


def _strip_home_dev_blurb(app_text: str) -> str:
    # Remove nothing critical — home text is already user-facing.
    return app_text


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for rel in COPY_TREES:
        _copy_tree(ROOT / rel, OUT / rel)

    for rel in COPY_FILES:
        src = ROOT / rel
        if not src.exists():
            raise SystemExit(f"Missing required file: {rel}")
        shutil.copy2(src, OUT / rel)

    # Optional: bake release-check repo id into the distributable
    github_repo = ROOT / "GITHUB_REPO"
    if github_repo.is_file():
        shutil.copy2(github_repo, OUT / "GITHUB_REPO")

    # Slim requirements for end users (no test tooling)
    req_lines = [
        ln
        for ln in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("pytest")
    ]
    (OUT / "requirements.txt").write_text("\n".join(req_lines) + "\n", encoding="utf-8")

    for script in ("install.sh", "run.sh"):
        _chmod_exec(OUT / script)

    docs = OUT / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "USER_GUIDE_ru.md").write_text(USER_GUIDE_RU, encoding="utf-8")
    (docs / "USER_GUIDE.md").write_text(USER_GUIDE_EN, encoding="utf-8")
    (OUT / "README.md").write_text(USER_README, encoding="utf-8")

    # Optional Streamlit config (relative, no secrets)
    st_dir = OUT / ".streamlit"
    st_dir.mkdir(exist_ok=True)
    (st_dir / "config.toml").write_text(
        "[browser]\n"
        "gatherUsageStats = false\n"
        "\n"
        "[server]\n"
        "showEmailPrompt = false\n"
        "headless = false\n",
        encoding="utf-8",
    )

    # Empty runtime dirs (no sample secrets / no absolute paths)
    for rel in ("data/projects", "data/sessions", "exports"):
        (OUT / rel).mkdir(parents=True, exist_ok=True)
        (OUT / rel / ".gitkeep").write_text("", encoding="utf-8")

    # Ensure no machine-absolute paths leaked into copied text files
    bad: list[str] = []
    for path in OUT.rglob("*"):
        if not path.is_file() or _should_skip(path):
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".toml", ".sh", ".bat", ".mdc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "/Users/" in text or "C:\\Users\\" in text or "kirillverbilo" in text:
            bad.append(str(path.relative_to(OUT)))
    if bad:
        raise SystemExit("Hardcoded user paths found in standalone build:\n  " + "\n  ".join(bad))

    print(f"Standalone build ready: {OUT}")
    print("Distribute the XPS-Deconv folder (zip it). Recipients run install then run.")


if __name__ == "__main__":
    main()
