from typing import Iterable, Optional, Sequence, Union

import pandas as pd


def read_excel_as_dataframe(
    file_path: str,
    sheet: Union[str, int, None] = 0,
    use_columns: Optional[Union[Sequence[str], Sequence[int]]] = None,
    row_slice: Optional[slice] = None,
    header: Union[int, None] = 0,
) -> pd.DataFrame:
    """
    Read an Excel file into a pandas DataFrame with flexible options.

    - file_path: Path to the Excel file (xlsx, xls, etc.)
    - sheet: Sheet name, index (0-based), or None to read all sheets (dict of DataFrames)
    - use_columns: Column names or indices to select specific columns. None for all.
    - row_slice: Python slice for rows, e.g., slice(0, 10) for first 10 rows. None for all.
    - header: Row number to use as column names (0-based), or None for no header.

    Returns a DataFrame. If sheet=None, returns the first sheet after concatenation.
    """
    df = pd.read_excel(
        file_path,
        sheet_name=sheet,
        header=header,
        usecols=use_columns,  # pandas handles both labels and indices
        engine="openpyxl",
    )

    if isinstance(df, dict):
        # If multiple sheets were loaded, concatenate with a column to indicate sheet
        frames = []
        for sheet_name, sheet_df in df.items():
            sheet_df = sheet_df.copy()
            sheet_df["__sheet__"] = sheet_name
            frames.append(sheet_df)
        df = pd.concat(frames, ignore_index=True)

    if row_slice is not None:
        df = df.iloc[row_slice]

    return df


def pick_columns(df: pd.DataFrame, columns: Iterable[Union[str, int]]) -> pd.DataFrame:
    """Return a new DataFrame with only the specified columns by name or position."""
    resolved_columns = []
    for col in columns:
        if isinstance(col, int):
            resolved_columns.append(df.columns[col])
        else:
            resolved_columns.append(col)
    return df.loc[:, resolved_columns]
