import json, os, logging
import pytest
import pandas as pd
from pathlib import Path
from typing import Dict, Any


def pytest_addoption(parser):
    parser.addoption(
        "--mode",
        action="store",
        default=None,
        help="Module name to run (e.g. solar or EV)",
    )


def pytest_collection_modifyitems(config, items):
    module = config.getoption("--mode")
    if not module:
        # No mode passed → do not filter
        return

    selected = []
    deselected = []

    selected_dir = (Path(__file__).parent / module / "tests").resolve()

    for item in items:
        item_path = Path(str(item.fspath)).resolve()
        try:
            item_path.relative_to(selected_dir)
            selected.append(item)
        except Exception:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected

    logging.info(f"[MODE] {module} → {selected_dir}")