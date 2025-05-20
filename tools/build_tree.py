# tools/build_tree.py

import os
import json
from pathlib import Path
from config.config_loader import load_structure_config


use_test = True
# 1) загрузка секций и их опций из configs/parse.json
STRUCTURE_CONFIG = load_structure_config("configs/parse.json")
# теперь у нас в STRUCTURE_CONFIG есть поля adapters, application, config, domain, interfaces

# 2) какие разделы мы хотим обрабатывать
SECTIONS = ["adapters", "application", "config", "domain", "interfaces"]

# 3) игнорируем системные файлы/директории
IGNORE_DIRS = {"venv", ".venv", ".git", "__pycache__", ".idea", ".mypy_cache"}
IGNORE_FILE_PREFIXES = {".", "~"}
IGNORE_FILE_EXTS = {".pyc", ".pyo", ".log", ".DS_Store"}

def should_ignore_dir(name: str) -> bool:
    return name in IGNORE_DIRS or name.startswith(".")

def should_ignore_file(name: str) -> bool:
    if any(name.startswith(pref) for pref in IGNORE_FILE_PREFIXES):
        return True
    if any(name.endswith(ext) for ext in IGNORE_FILE_EXTS):
        return True
    return False

def build_section_tree(section: str, root: Path, opts) -> dict:
    """
    Рекурсивно обходит папку root, но показывает только
    .py если opts.emit_code, и только .md если opts.emit_md.
    """
    tree: dict = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # фильтруем системные папки
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d)]
        # вычисляем относительный путь внутри раздела
        rel = Path(dirpath).relative_to(root)
        # находим узел в итоговом дереве
        ptr = tree
        for part in rel.parts:
            ptr = ptr.setdefault(part, {})
        # проходим по файлам
        for fn in sorted(filenames):
            if should_ignore_file(fn):
                continue
            path = Path(dirpath) / fn
            if fn.endswith(".py") and opts.emit_code:
                try:
                   txt = path.read_text(encoding="utf-8")
                except Exception as e:
                    txt = f"[ERROR reading file: {e}]"
                if not use_test:
                    txt = None
                ptr[fn] = {"path": str(path), "content": txt}

            elif fn.endswith(".md") and opts.emit_md:
                # показываем путь + содержимое
                try:
                    txt = path.read_text(encoding="utf-8")
                except Exception as e:
                    txt = f"[ERROR reading file: {e}]"
                ptr[fn] = {"path": str(path), "content": txt}
            # иначе — пропустить
    return tree

def build_full_tree() -> dict:
    """
    Собирает по-отдельности для каждого раздела секцию из SECTIONS.
    Если раздела нет в проекте — пропускаем.
    """
    project_root = Path("src")
    full: dict = {}
    for section in SECTIONS:
        section_root = project_root / section
        if not section_root.exists():
            continue
        opts = getattr(STRUCTURE_CONFIG, section)
        full[section] = build_section_tree(section, section_root, opts)
    return full

if __name__ == "__main__":
    tree = build_full_tree()
    with open("project_struct_by_section.json", "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print("Done: project_struct_by_section.json")
