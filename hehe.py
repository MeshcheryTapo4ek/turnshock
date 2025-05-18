# tools/build_tree.py

import os, json
from pathlib import Path
from src.config.parser_options import PROJECT_STRUCTURE_OPTIONS

IGNORE_DIRS       = {"venv", ".venv", ".git", "__pycache__", ".idea", ".mypy_cache"}
IGNORE_FILE_EXTS  = {".json", ".pyc", ".pyo", ".log", ".DS_Store"}
IGNORE_FILE_PREFIXES = {".", "~"}

def get_folder_options(path: Path, root: Path) -> dict[str, bool]:
    abs_path = path.resolve()
    abs_root = root.resolve()
    rel = str(abs_path.relative_to(abs_root)).replace("\\", "/")
    # ищем самый длинный ключ
    while rel:
        if rel in PROJECT_STRUCTURE_OPTIONS:
            return PROJECT_STRUCTURE_OPTIONS[rel]
        rel = rel.rpartition('/')[0]
    return {"emit_code": False, "emit_md": False}

def should_ignore_dir(d): return d in IGNORE_DIRS or d.startswith(".")
def should_ignore_file(f):
    return any(f.startswith(pref) for pref in IGNORE_FILE_PREFIXES) \
       or any(f.endswith(ext) for ext in IGNORE_FILE_EXTS)

def build_structured_tree(root: Path, show_options=True) -> dict:
    tree = {}
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d)]
        rel_dir = str(Path(dirpath).relative_to(root)).replace("\\","/")
        # get pointer in tree
        ptr = tree
        if rel_dir != ".":
            for part in rel_dir.split("/"):
                ptr = ptr.setdefault(part, {})
        if show_options:
            ptr["_options"] = get_folder_options(Path(dirpath), root)
        # files
        for f in sorted(filenames):
            if should_ignore_file(f): continue
            opts = get_folder_options(Path(dirpath), root)
            need = (opts["emit_code"] and f.endswith(".py")) \
                or (opts["emit_md"] and f.endswith(".md"))
            try:
                content = (Path(dirpath)/f).read_text() if need else None
            except Exception as e:
                content = f"[ERROR: {e}]"
            ptr[f] = {"path": str(Path(dirpath)/f), "content": content}
    return tree

if __name__ == "__main__":
    # 1) дерево src
    src_root = Path("src")
    tree_src = build_structured_tree(src_root)

    # 2) дерево configs (для cli_start.json)
    cfg_root = Path("configs")
    tree_cfg = build_structured_tree(cfg_root)

    # merge two под одним JSON
    full = {"src": tree_src, "configs": tree_cfg}
    with open("project_struct_with_options.json","w", encoding="utf-8") as f:
        json.dump(full, f, indent=2, ensure_ascii=False)
    print("Done: project_struct_with_options.json")
