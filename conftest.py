import json
import pytest
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Union


def load_master_config() -> Dict[str, Any]:
    """Load the root master config (contains current_mode)."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r") as f:
        return json.load(f)


def load_mode_config(mode: str) -> Dict[str, Any]:
    """Load the config for the given mode from its folder."""
    config_path = Path(__file__).parent / mode / "config" / f"{mode}_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found for mode '{mode}': {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)


def load_dataframe(path: str, sheet: Optional[Union[str, int]] = None) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Read Excel into a DataFrame (one sheet) or dict of DataFrames (all sheets)."""
    file_path = Path.cwd() / Path(path)   # join with current working dir
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    if sheet is None:
        # Load all worksheets
        return pd.read_excel(file_path, sheet_name=None)
    else:
        # Load only the specified worksheet
        return pd.read_excel(file_path, sheet_name=sheet)


@pytest.fixture(scope="session")
def current_mode() -> str:
    """Get the current mode (solar, ev, etc.) from master config."""
    master_cfg = load_master_config()
    return master_cfg.get("current_mode", "solar")


@pytest.fixture(scope="session")
def dataframes(current_mode: str) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Load all worksheets for each dataset defined in the current mode’s config."""
    config = load_mode_config(current_mode)

    dfs: Dict[str, Dict[str, pd.DataFrame]] = {}
    for name, cfg in config.items():
        path = cfg.get("path")
        try:
            dfs[name] = load_dataframe(path, sheet=None)  # always load ALL sheets
            print(f"\n\n Loaded {name} (all sheets) from {Path.cwd() / path}")
        except Exception as e:
            print(f"Failed to load {name} from {Path.cwd() / path}: {e}")
            dfs[name] = {}

    return dfs


def pytest_configure(config):
    """Dynamically register dataset fixtures."""
    mode = load_master_config().get("current_mode", "solar")
    mode_config = load_mode_config(mode)

    for dataset_name in mode_config.keys():
        fixture_name = f"{dataset_name}_dataframe"

        def make_fixture(dataset=dataset_name):
            @pytest.fixture(scope="session", name=fixture_name)
            def _fixture(dataframes):
                """Auto-generated fixture for dataset {dataset}"""
                return dataframes.get(dataset)
            return _fixture

        globals()[fixture_name] = make_fixture()
