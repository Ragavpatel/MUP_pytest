from datetime import datetime
import logging, os

def generate_html_report(user_info, execution_results=None):
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
    html_str += '<h3>User Info</h3>\n'
    html_str += '<table>\n<thead><tr><th>Field</th><th>Value</th></tr></thead>\n<tbody>\n'
    for key, value in user_info.items():
        html_str += f'  <tr><td>{key}</td><td>{value}</td></tr>\n'
        logging.info(f"{key}: {value}")
    html_str += '</tbody>\n</table>\n'

    # ---------- Execution Results Table ----------
    html_str += '<h3>Execution Results</h3>\n'
    html_str += '<table>\n<thead><tr><th>Row / Step</th><th>Status / Detail</th></tr></thead>\n<tbody>\n'

    if execution_results is None:
        html_str += '  <tr><td>-</td><td>Execution not run yet</td></tr>\n'
        logging.info("Execution not run yet")
    elif isinstance(execution_results, dict) and execution_results:
        for row, detail in execution_results.items():
            css_class = "failed" if ("!=" in str(detail) or "Error" in str(detail)) else "passed"
            html_str += f'  <tr class="{css_class}"><td>{row}</td><td>{detail}</td></tr>\n'
            logging.error(f"Row {row}: {detail}")
    else:
        message = execution_results if isinstance(execution_results, str) else "All raw calculations matched."
        html_str += f'  <tr class="passed"><td>-</td><td>{message}</td></tr>\n'
        logging.info(message)

    html_str += '</tbody>\n</table>\n</body>\n</html>'

    # ---------- Save HTML (overwrite previous report) ----------
    report_dir = r"C:\Automation\E-MUG\MUP_pytest\MUG_pytest\report"
    os.makedirs(report_dir, exist_ok=True)

    filename = "report.html"  # Fixed filename to overwrite
    filepath = os.path.join(report_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_str)

    print(f"Report saved to: {filepath}")
    return filepath