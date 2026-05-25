"""
BAAS Pro - Reverse engineered from PyInstaller binary.
Lazy loader: when a decompiled .py source is absent, imports from the original .pyc.
"""
import os
import sys
import marshal
import importlib
import importlib.util
import importlib.abc
import types

_PYC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baas_extracted", "PYZ.pyz_extracted")


class _PycLoader(importlib.abc.Loader):
    """Load a module from a .pyc file if the .py source is not available."""

    def __init__(self, pyc_path, fullname):
        self.pyc_path = pyc_path
        self.fullname = fullname

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        with open(self.pyc_path, "rb") as f:
            f.seek(16)  # PEP 552 header
            code = marshal.load(f)
        exec(code, module.__dict__)


class _PycFinder(importlib.abc.MetaPathFinder):
    """Fallback finder: if a .py file doesn't exist for a module, try .pyc."""

    def __init__(self, pyc_root):
        self.pyc_root = pyc_root

    def find_spec(self, fullname, path, target=None):
        parts = fullname.split(".")
        rel_path = os.path.join(self.pyc_root, *parts[:-1], parts[-1] + ".pyc")
        init_path = os.path.join(self.pyc_root, *parts, "__init__.pyc")
        for p in (rel_path, init_path):
            if os.path.exists(p):
                return importlib.util.spec_from_loader(
                    fullname,
                    _PycLoader(p, fullname),
                    origin=p,
                )
        return None


def install():
    """Install pyc fallback loader. Call before importing app modules."""
    finder = _PycFinder(_PYC_ROOT)
    if finder not in sys.meta_path:
        sys.meta_path.insert(0, finder)
