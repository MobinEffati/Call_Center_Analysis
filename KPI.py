from pathlib import Path

import pandas as pd


# ==================================================
# Paths and Constants
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
CLEANED_DATA_PATH = DATA_DIR / "CleanedData.csv"

HANDLED_STATUSES = ["answered", "transferred"]

DURATION_COLUMNS = [
    "wait_seconds",
    "handle_seconds",
    "hold_seconds",
    "after_call_work_seconds",
]

HANDLE_TIME_COLUMNS = [
    "handle_seconds",
    "hold_seconds",
    "after_call_work_seconds",
]

REQUIRED_COLUMNS = [
    "call_date",
    "start_time",
    "queue",
    "status",
    "wait_seconds",
    "handle_seconds",
    "hold_seconds",
    "after_call_work_seconds",
    "csat_score",
    "first_contact_resolution",
]


# ==================================================
# Load Cleaned Data
# ==================================================

def load_cleaned_data(
    file_path: Path = CLEANED_DATA_PATH,
) -> pd.DataFrame:
    """Load the cleaned dataset."""

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {file_path}. "
            "Run CleanData.py first."
        )

    return pd.read_csv(
        file_path,
        dtype={"customer_phone": "string"},
    )


# ==================================================
# Prepare Data
# ==================================================

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare dates, times, and shifts for KPI calculations."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    result = df.copy()

    # Parse call_date.
    if pd.api.types.is_datetime64_any_dtype(result["call_date"]):
        result["call_date"] = pd.to_datetime(
            result["call_date"],
            errors="coerce",
        ).dt.normalize()
    else:
        result["call_date"] = pd.to_datetime(
            result["call_date"],
            format="%m/%d/%Y",
            errors="coerce",
        ).dt.normalize()

    # Extract hours from valid 24-hour times.
    time_values = (
        result["start_time"]
        .astype("string")
        .str.strip()
    )

    valid_time = time_values.str.fullmatch(
        r"(?:[01]?\d|2[0-3]):[0-5]\d:[0-5]\d",
        na=False,
    )

    hours = pd.to_numeric(
        time_values.where(valid_time)
        .str.extract(r"^(\d{1,2}):", expand=False),
        errors="coerce",
    )

    # Default missing or invalid times to Unknown.
    result["shift"] = pd.Series(
        "Unknown",
        index=result.index,
        dtype="string",
    )

    # Morning: 06:00 <= time < 14:00
    result.loc[
        hours.ge(6) & hours.lt(14),
        "shift",
    ] = "Morning"

    # Evening: 14:00 <= time < 22:00
    result.loc[
        hours.ge(14) & hours.lt(22),
        "shift",
    ] = "Evening"

    # Night: 22:00-23:59 and 00:00-05:59
    result.loc[
        hours.ge(22) | hours.lt(6),
        "shift",
    ] = "Night"

    return result


# ==================================================
# Helper Functions
# ==================================================

def safe_mean(values: pd.Series):
    """Return the mean or None if no numeric values exist."""

    numeric_values = pd.to_numeric(
        values,
        errors="coerce",
    ).dropna()

    if numeric_values.empty:
        return None

    return round(float(numeric_values.mean()), 2)


def safe_percentage(numerator: int, denominator: int):
    """Calculate percentage safely."""

    if denominator == 0:
        return None

    return round(
        numerator / denominator * 100,
        2,
    )


def normalize_fcr(value):
    """Normalize first_contact_resolution values."""

    if pd.isna(value):
        return None

    normalized_value = str(value).strip().casefold()

    true_values = {
        "yes",
        "y",
        "true",
        "1",
        "1.0",
    }

    false_values = {
        "no",
        "n",
        "false",
        "0",
        "0.0",
    }

    if normalized_value in true_values:
        return True

    if normalized_value in false_values:
        return False

    return None


# ==================================================
# KPI Calculations
# ==================================================

def _calculate_kpis_prepared(df: pd.DataFrame) -> dict:
    """Calculate KPIs for an already prepared dataset."""

    status = (
        df["status"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    total_calls = len(df)

    answered_calls = int(status.eq("answered").sum())
    abandoned_calls = int(status.eq("abandoned").sum())
    transferred_calls = int(status.eq("transferred").sum())

    # Transferred calls are treated as calls that were answered.
    handled_mask = status.isin(HANDLED_STATUSES)
    handled_calls = int(handled_mask.sum())

    # --------------------------------------------------
    # 1. Answer Rate
    # --------------------------------------------------

    answer_rate = safe_percentage(
        handled_calls,
        total_calls,
    )

    # --------------------------------------------------
    # 2. Abandon Rate
    # --------------------------------------------------

    abandon_rate = safe_percentage(
        abandoned_calls,
        total_calls,
    )

    # --------------------------------------------------
    # 3. Average Waiting Time (AWT)
    # --------------------------------------------------

    wait_values = pd.to_numeric(
        df["wait_seconds"],
        errors="coerce",
    )

    average_wait_time = safe_mean(
        wait_values.loc[handled_mask]
    )

    # --------------------------------------------------
    # 4. Average Handle Time (AHT)
    # --------------------------------------------------

    handle_components = df[HANDLE_TIME_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce",
    )

    total_handle_time = handle_components.sum(
        axis=1,
        min_count=len(HANDLE_TIME_COLUMNS),
    )

    average_handle_time = safe_mean(
        total_handle_time.loc[handled_mask]
    )

    # --------------------------------------------------
    # 5. Customer Satisfaction (CSAT)
    # --------------------------------------------------

    csat_values = pd.to_numeric(
        df["csat_score"],
        errors="coerce",
    )

    average_csat = safe_mean(csat_values)

    # --------------------------------------------------
    # 6. First Contact Resolution (FCR)
    # --------------------------------------------------

    fcr_values = df["first_contact_resolution"].apply(
        normalize_fcr
    )

    # IMPORTANT:
    # Abandoned calls are excluded from FCR.
    # Even if their FCR value is "No", they are not eligible.
    fcr_eligible_mask = (
        handled_mask
        & fcr_values.notna()
    )

    fcr_eligible_calls = int(
        fcr_eligible_mask.sum()
    )

    fcr_resolved_calls = int(
        (
            fcr_values.eq(True)
            & fcr_eligible_mask
        ).sum()
    )

    fcr_rate = safe_percentage(
        fcr_resolved_calls,
        fcr_eligible_calls,
    )

    return {
        "total_calls": total_calls,
        "answered_calls": answered_calls,
        "abandoned_calls": abandoned_calls,
        "transferred_calls": transferred_calls,
        "handled_calls": handled_calls,
        "answer_rate_pct": answer_rate,
        "abandon_rate_pct": abandon_rate,
        "average_wait_time_seconds": average_wait_time,
        "average_handle_time_seconds": average_handle_time,
        "average_csat_score": average_csat,
        "fcr_eligible_calls": fcr_eligible_calls,
        "fcr_resolved_calls": fcr_resolved_calls,
        "fcr_rate_pct": fcr_rate,
    }


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate all KPIs for the supplied dataset."""

    prepared_df = prepare_data(df)

    return _calculate_kpis_prepared(prepared_df)


# ==================================================
# Data Filtering
# ==================================================

def filter_data(
    df: pd.DataFrame,
    team: str | None = None,
    shift: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Filter calls by team, shift, and date range."""

    result = prepare_data(df)

    if team is not None:
        team_value = team.strip().casefold()

        team_mask = (
            result["queue"]
            .astype("string")
            .str.strip()
            .str.casefold()
            .eq(team_value)
            .fillna(False)
        )

        result = result.loc[team_mask]

    if shift is not None:
        available_shifts = {
            "morning": "Morning",
            "evening": "Evening",
            "night": "Night",
            "unknown": "Unknown",
        }

        normalized_shift = available_shifts.get(
            shift.strip().casefold()
        )

        if normalized_shift is None:
            raise ValueError(
                "Invalid shift. Use Morning, Evening, Night, or Unknown."
            )

        result = result.loc[
            result["shift"].eq(normalized_shift)
        ]

    start = None
    end = None

    if start_date is not None:
        try:
            start = pd.Timestamp(start_date).normalize()
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Invalid start_date. Use YYYY-MM-DD."
            ) from exc

    if end_date is not None:
        try:
            end = pd.Timestamp(end_date).normalize()
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Invalid end_date. Use YYYY-MM-DD."
            ) from exc

    if start is not None and end is not None and start > end:
        raise ValueError(
            "start_date must be on or before end_date."
        )

    if start is not None:
        result = result.loc[
            result["call_date"].ge(start)
        ]

    if end is not None:
        result = result.loc[
            result["call_date"].le(end)
        ]

    return result.copy()


# ==================================================
# KPI Aggregations
# ==================================================

KPI_COLUMNS = [
    "total_calls",
    "answered_calls",
    "abandoned_calls",
    "transferred_calls",
    "handled_calls",
    "answer_rate_pct",
    "abandon_rate_pct",
    "average_wait_time_seconds",
    "average_handle_time_seconds",
    "average_csat_score",
    "fcr_eligible_calls",
    "fcr_resolved_calls",
    "fcr_rate_pct",
]


def _calculate_kpis_by_group(
    df: pd.DataFrame,
    group_column: str,
    output_column: str,
) -> pd.DataFrame:
    """Calculate KPI metrics for each group."""

    prepared_df = prepare_data(df)

    records = []

    for group_value, group_df in prepared_df.groupby(
        group_column,
        dropna=False,
        sort=True,
    ):
        label = (
            "Unknown"
            if pd.isna(group_value)
            else str(group_value)
        )

        records.append({
            output_column: label,
            **_calculate_kpis_prepared(group_df),
        })

    return pd.DataFrame(
        records,
        columns=[output_column] + KPI_COLUMNS,
    )


def calculate_kpis_by_team(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate KPIs for each team."""

    return _calculate_kpis_by_group(
        df,
        group_column="queue",
        output_column="team",
    )


def calculate_kpis_by_shift(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate KPIs for each shift."""

    return _calculate_kpis_by_group(
        df,
        group_column="shift",
        output_column="shift",
    )


def calculate_daily_kpis(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate KPIs for each calendar day."""

    prepared_df = prepare_data(df)

    records = []

    for date_value, group_df in prepared_df.groupby(
        "call_date",
        dropna=False,
        sort=True,
    ):
        date_label = (
            "Unknown"
            if pd.isna(date_value)
            else date_value.strftime("%Y-%m-%d")
        )

        records.append({
            "date": date_label,
            **_calculate_kpis_prepared(group_df),
        })

    return pd.DataFrame(
        records,
        columns=["date"] + KPI_COLUMNS,
    )


# ==================================================
# Local Execution
# ==================================================

if __name__ == "__main__":

    df = load_cleaned_data()

    print("\nOVERALL KPI SUMMARY")
    print("=" * 60)
    print(pd.Series(calculate_kpis(df)).to_string())

    print("\nKPIs BY TEAM")
    print("=" * 60)
    print(calculate_kpis_by_team(df).to_string(index=False))

    print("\nKPIs BY SHIFT")
    print("=" * 60)
    print(calculate_kpis_by_shift(df).to_string(index=False))

    print("\nDAILY KPIs")
    print("=" * 60)
    print(calculate_daily_kpis(df).to_string(index=False))