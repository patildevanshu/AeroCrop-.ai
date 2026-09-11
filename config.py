"""
AeroCrop.ai — Root Configuration Bridge
Re-exports all settings from backend.config for backward compatibility.
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

for path in [PROJECT_ROOT, BACKEND_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.config import *
