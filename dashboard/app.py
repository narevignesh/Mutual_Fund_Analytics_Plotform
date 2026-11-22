"""
Mutual Fund Analytics Platform
Entry Point: dashboard/app.py (Redirects to simplified root app.py)
"""

import os
import sys
import runpy

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Execute main simplified app.py in root directory
app_path = os.path.join(ROOT_DIR, "app.py")
runpy.run_path(app_path, run_name="__main__")
