"""Compatibility entry point for recorded independent evidence."""
import pathlib,runpy
runpy.run_path(str(pathlib.Path(__file__).resolve().parents[2]/"tests"/"independent_checks.py"),run_name="__main__")
