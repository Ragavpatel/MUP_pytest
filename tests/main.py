import os
import logging
import pandas as pd

def test_excel_calculation():
    # Load Excel file
    file_path = "./data/test.xlsx"
    df = pd.read_excel(file_path)

    # Choose column and multiplier
    source_col = "Col5"
    multiplier = 10
    new_col = "Col7"
    assert_col = "Col1"

    # Always recalculate new_col
    df[new_col] = df[source_col] * multiplier

    # Save the updated Excel into the output folder
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_output.xlsx")
    # Write multiple sheets: full data and a focused sheet
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Calculated")
        focused = df[[source_col, new_col]].copy()
        focused.to_excel(writer, index=False, sheet_name="Col5_x10")

    # Compare new column with Col1
    for idx, row in df.iterrows():
        assert row[assert_col] == row[new_col],  f"Mismatch at row {idx}: {row[assert_col]} != {row[new_col]}"

def test_print_col5_and_row1():
    # Load Excel file
    file_path = "./data/test.xlsx"
    df = pd.read_excel(file_path)

    if "Col5" in df.columns:
        logging.info("Col5 values: %s", df["Col5"].tolist())
    elif df.shape[1] >= 5:
        logging.info("5th column values: %s", df.iloc[:, 4].tolist())
    else:
        logging.info("No 5th column found")

    # Print Row 1 (first data row)
    if len(df) > 0:
        logging.info("Row 1 data: %s", df.iloc[0].to_dict())
    else:
        logging.info("DataFrame is empty")

def test_write_row1_and_col5_to_sheet2():
    # Load Excel file
    file_path = "./data/test.xlsx"
    df = pd.read_excel(file_path)

    if df.empty:
        logging.info("Input DataFrame is empty; skipping Sheet2 write")
        return

    # Resolve Column 5 series (prefer named Col5, else 5th positional)
    if "Col5" in df.columns:
        col5_series = df["Col5"]
        col5_label = "Col5"
    elif df.shape[1] >= 5:
        col5_series = df.iloc[:, 4]
        col5_label = df.columns[4]
    else:
        logging.info("No 5th column available; skipping Sheet2 write")
        return

    # Row 1 (first data row)
    row1 = df.iloc[0]

    # Prepare output path
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_output.xlsx")

    # Compose two tables in Sheet2: a single-row table for Row1 and a single-column table for Col5
    row1_df = row1.to_frame().T  # one-row DataFrame
    col5_df = pd.DataFrame({col5_label: col5_series})

    # Create or append Sheet2
    if os.path.exists(output_path):
        mode = "a"
        if_sheet_exists = "replace"
    else:
        mode = "w"
        if_sheet_exists = None  # not used in write mode

    with pd.ExcelWriter(output_path, engine="openpyxl", mode=mode, if_sheet_exists=if_sheet_exists) as writer:  # type: ignore[arg-type]
        # Write Row1 at the top
        row1_df.to_excel(writer, index=False, sheet_name="Sheet2")
        # Leave one empty row, then write Col5 list
        start_row = len(row1_df) + 2
        col5_df.to_excel(writer, index=False, sheet_name="Sheet2", startrow=start_row)

    logging.info("Wrote Row 1 and %s column to Sheet2 at %s", col5_label, output_path)