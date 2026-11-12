; import os / import sys, json
(import_statement name: (dotted_name) @modul)
; import os.path as osp
(import_statement name: (aliased_import name: (dotted_name) @modul))
; from pathlib import Path / from . import utils (module_name bisa dotted_name atau relative_import)
(import_from_statement module_name: (_) @modul)
