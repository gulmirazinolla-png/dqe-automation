from pathlib import Path

import pandas as pd

# JavaScript that pulls the table data out of the Plotly figure on the page
_JS_READ_TABLE = """
const gd = arguments[0];
const traces = gd._fullData || gd.data || [];
const t = traces.find(x => x.type === 'table');
if (!t) { return null; }
const header = (t.header.values || []).map(v => Array.isArray(v) ? v.join(' ') : String(v));
const columns = (t.cells.values || []).map(col => Array.from(col));
return {header: header, columns: columns};
"""


def get_file_url(path):
    """Turn a local file path into a file:// URL the browser can open."""
    return Path(path).resolve().as_uri()


def read_html_table(table_element):
    """Read the table of a Plotly report (a located WebElement) into a DataFrame."""
    driver = table_element.parent
    data = driver.execute_script(_JS_READ_TABLE, table_element)
    if not data:
        raise AssertionError("No Plotly table found inside the given element.")
    header = [h.strip() for h in data["header"]]
    return pd.DataFrame(dict(zip(header, data["columns"])))


def read_parquet_data(folder, filter_date=None, date_column="visit_date"):
    """Read a partitioned Parquet dataset; optionally keep rows with date >= filter_date."""
    df = pd.read_parquet(folder)
    # partition columns come from folder names and are not part of the report table
    df = df.drop(columns=[c for c in df.columns if "partition" in c.lower()])
    if filter_date:
        dates = pd.to_datetime(df[date_column])
        df = df[dates >= pd.Timestamp(filter_date)]
    return df.reset_index(drop=True)


def _column_name(name):
    """'Average Time Spent' -> 'avg_time_spent', so HTML and Parquet names line up."""
    return str(name).strip().lower().replace(" ", "_").replace("average", "avg")


def _normalize(df):
    """Make both DataFrames comparable: same names, same value formats, same order."""
    df = df.copy()
    df.columns = [_column_name(c) for c in df.columns]
    df = df[sorted(df.columns)]

    for col in df.columns:
        if "date" in col:
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
            continue
        numbers = pd.to_numeric(df[col], errors="coerce")
        if numbers.notna().all():
            # the report shows rounded numbers: 48.0 -> "48", 32.333 -> "32.33"
            df[col] = numbers.round(2).map(lambda x: f"{x:.2f}".rstrip("0").rstrip("."))
        else:
            df[col] = df[col].astype(str).str.strip()

    return df.sort_values(by=list(df.columns)).reset_index(drop=True)


def compare_dataframes(df_html, df_parquet):
    """Return '' if both DataFrames match exactly, otherwise a text description of the differences."""
    a, b = _normalize(df_html), _normalize(df_parquet)

    if list(a.columns) != list(b.columns):
        return (f"Columns differ:\n  HTML:    {list(a.columns)}\n"
                f"  Parquet: {list(b.columns)}")

    problems = []
    if len(a) != len(b):
        problems.append(f"Row count differs: HTML={len(a)}, Parquet={len(b)}")

    merged = a.merge(b, how="outer", indicator=True)
    diff = merged[merged["_merge"] != "both"].copy()
    diff["_merge"] = diff["_merge"].map(
        {"left_only": "only in HTML", "right_only": "only in Parquet"})
    if not diff.empty:
        problems.append("Mismatching rows:\n" + diff.to_string(index=False))

    return "\n".join(problems)