# src/config/parser_options.py

from typing import Final

# Всё относительно папки src/
PROJECT_STRUCTURE_OPTIONS: Final[dict[str, dict[str, bool]]] = {
  #  "configs":             {"emit_code": False,  "emit_md": False},
  #  "config":              {"emit_code": True,  "emit_md": True},
    "domain":              {"emit_code": True,  "emit_md": True},
    "domain/geometry":     {"emit_code": True,  "emit_md": True},
    "domain/core":         {"emit_code": True,  "emit_md": True},
    "domain/rules":        {"emit_code": True,  "emit_md": True},
    "domain/engine":       {"emit_code": True,  "emit_md": True},
    "domain/heroes":       {"emit_code": False,  "emit_md": True},
    "application":         {"emit_code": True,  "emit_md": True},
    "interfaces":          {"emit_code": True,  "emit_md": True},
 #   "ui":                   {"emit_code": True,  "emit_md": True},
  #  "tests":               {"emit_code": False,  "emit_md": True},
  #  "tests/config":        {"emit_code": False,  "emit_md": True},
   # "tests/application":   {"emit_code": False,  "emit_md": True},
}
