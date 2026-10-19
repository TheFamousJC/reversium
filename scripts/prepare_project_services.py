"""Compatibility entry for the fixed reviewed example profile, not arbitrary ZIP execution."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("prepare_tudela_services.py")), run_name="__main__")
