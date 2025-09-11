import os
import pytest
from typing import List, Optional, Union

from tests.utils.excel_reader import read_excel_as_dataframe


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default=os.getenv("BASE_URL", "http://localhost:8000"),
        help="Base URL for the application under test",
    )
    parser.addoption(
        "--excel-path",
        action="store",
        default=os.getenv("EXCEL_PATH"),
        help="Path to an Excel file to load (e.g., C:/data/file.xlsx)",
    )
    parser.addoption(
        "--excel-sheet",
        action="store",
        default=os.getenv("EXCEL_SHEET", "0"),
        help="Sheet name or index (default 0). Use name like 'Sheet1' or index like 0",
    )
    parser.addoption(
        "--excel-usecols",
        action="store",
        default=os.getenv("EXCEL_USECOLS"),
        help="Optional comma-separated list of columns to load (names or 0-based indexes)",
    )
    parser.addoption(
        "--excel-rows",
        action="store",
        default=os.getenv("EXCEL_ROWS"),
        help="Optional row slice like '0:100' (start:end) to limit rows",
    )
    parser.addoption(
        "--excel-header",
        action="store",
        default=os.getenv("EXCEL_HEADER", "0"),
        help="Header row index (0-based) or 'None' for no header",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    return str(pytestconfig.getoption("base_url"))


def _parse_sheet(value: str) -> Union[str, int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _parse_usecols(value: Optional[str]) -> Optional[List[Union[str, int]]]:
    if not value:
        return None
    parts = [p.strip() for p in value.split(",") if p.strip()]
    parsed: List[Union[str, int]] = []
    for p in parts:
        try:
            parsed.append(int(p))
        except ValueError:
            parsed.append(p)
    return parsed or None


def _parse_rows(value: Optional[str]) -> Optional[slice]:
    if not value:
        return None
    if ":" in value:
        start_s, end_s = value.split(":", 1)
        start = int(start_s) if start_s.strip() != "" else None
        end = int(end_s) if end_s.strip() != "" else None
        return slice(start, end)
    # single number
    idx = int(value)
    return slice(idx, idx + 1)


def _parse_header(value: str) -> Optional[int]:
    if value is None:
        return 0
    v = value.strip()
    if v.lower() == "none":
        return None
    return int(v)


@pytest.fixture(scope="session")
def excel_dataframe(pytestconfig: pytest.Config):
    path = pytestconfig.getoption("excel_path")
    if not path:
        pytest.skip("--excel-path not provided; skipping excel_dataframe-dependent tests")

    sheet = _parse_sheet(pytestconfig.getoption("excel_sheet"))
    usecols = _parse_usecols(pytestconfig.getoption("excel_usecols"))
    rows = _parse_rows(pytestconfig.getoption("excel_rows"))
    header = _parse_header(pytestconfig.getoption("excel_header"))

    df = read_excel_as_dataframe(
        file_path=path,
        sheet=sheet,
        use_columns=usecols,
        row_slice=rows,
        header=header,
    )
    return df
