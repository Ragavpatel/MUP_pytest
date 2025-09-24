import logging
import os

def generate_html_report(user_info, mismatches=None):
    """
    Generate an HTML report for a customer showing user info and mismatched rows.
    Formats date and slot values for cleaner display.

    :param user_info: dict containing customer details (e.g., "customerId", "name", etc.)
    :param mismatches: list of tuples (idx, date_val, slot_val, calculated_value, existing_value)
    :return: filepath of the saved HTML report
    """
    customer_id = user_info.get("customerId", "Unknown")

    # ---------- HTML Header ----------
    html_str = f"""
    <html>
    <head>
    <title>Report for Customer: {customer_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        h2, h3 {{
            text-align: center;
        }}
        table {{
            width: 80%;
            margin: 0 auto 20px auto;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid #333;
            padding: 10px;
            text-align: center;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .passed {{
            background-color: #c6efce;
            color: #006100;
            font-weight: bold;
        }}
        .failed {{
            background-color: #ffc7ce;
            color: #9c0006;
            font-weight: bold;
        }}
    </style>
    </head>
    <body>
    <h2>Report for Customer: {customer_id}</h2>
    """

    # ---------- User Info Table ----------
    html_str += '<h3>User Information</h3>\n'
    html_str += '<table>\n<thead><tr>'
    for key in user_info.keys():
        html_str += f'<th>{key}</th>'
    html_str += '</tr></thead>\n<tbody>\n<tr>'
    for value in user_info.values():
        html_str += f'<td>{value}</td>'
    html_str += '</tr>\n</tbody>\n</table>\n'

    # ---------- Execution / Mismatches Table ----------
    html_str += '<h3>Execution Results</h3>\n'
    html_str += '<table>\n<thead><tr>'
    html_str += '<th>Row</th><th>Date</th><th>Slot</th><th>Calculated Value</th><th>Existing Value</th><th>Status</th>'
    html_str += '</tr></thead>\n<tbody>\n'

    if not mismatches:
        html_str += '<tr class="passed"><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>All rows match perfectly!</td></tr>\n'
        logging.info("All rows match perfectly!")
    else:
        for idx, date_val, slot_val, calc_val, exist_val in mismatches:
            # Format date
            if isinstance(date_val, str):
                date_display = date_val.split(" ")[0]  # remove time if present
            elif hasattr(date_val, "strftime"):
                date_display = date_val.strftime("%Y-%m-%d")
            else:
                date_display = str(date_val)

            # Format slot
            if isinstance(slot_val, float) and slot_val.is_integer():
                slot_display = str(int(slot_val))
            else:
                slot_display = str(slot_val)

            html_str += f'<tr class="failed"><td>{idx}</td><td>{date_display}</td><td>{slot_display}</td><td>{calc_val}</td><td>{exist_val}</td><td>Mismatch</td></tr>\n'
            logging.error(f"Row {idx}: Date {date_display} Slot {slot_display} → Calculated Value: {calc_val} != Existing Value: {exist_val}")

    html_str += "</tbody>\n</table>\n</body>\n</html>"

    # ---------- Save HTML ----------
    report_dir = r"C:\Automation\E-MUG\MUP_pytest\MUG_pytest\report"
    os.makedirs(report_dir, exist_ok=True)
    filepath = os.path.join(report_dir, "report.html")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_str)

    print(f"Report saved to: {filepath}")
    return filepath
