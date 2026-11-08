"""Compatibility entry point for the complete village integrity audit.

The former per-piece wall checks are superseded by dense whole-ground coverage,
continuous perimeter joins, sealed architecture and matching collision checks.
Results: Documentation/village-integrity-checks.json.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('check_village_integrity.py')), run_name='__main__')
