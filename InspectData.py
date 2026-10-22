from pathlib import Path
import re

import pandas as pd
from tabulate import tabulate


# ==================================================
# Paths
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    BASE_DIR
    / "Data"
    / "call_center_1000_with_reason_phone.csv"
)


# ==================================================
# Column Descriptions
# ==================================================

COLUMN_DESCRIPTIONS = {
    "call_id": "Unique identifier of each call",
    "call_date": "Date when the call was recorded",
    "start_time": "Time when the call started",
    "customer_phone": "Customer phone number",
    "call_reason": "Reason or category of the call",
    "agent_id": "Identifier of the agent handling the call",
    "queue": "Team or queue handling the call",
    "channel": "Communication channel used for the call",
    "status": "Final status of the call",
    "wait_seconds": "Waiting time in seconds",
    "handle_seconds": "Call handling duration in seconds",
    "hold_seconds": "Time spent on hold in seconds",
    "after_call_work_seconds": "Time spent on post-call tasks in seconds",
    "csat_score": "Customer satisfaction score",
    "first_contact_resolution": (
        "Indicates whether the issue was resolved during the first contact"
    ),
    "transfer_count": "Number of transfers during the call",
}


# ==================================================
# Load Data
# ==================================================

def load_csv(file_path: Path) -> pd.DataFrame:
    """Load the source CSV file."""

    if not file_path.is_file():
        raise FileNotFoundError(
            f"CSV file not found: {file_path}"
        )

    # Keep phone numbers as strings to preserve leading zeros.
    return pd.read_csv(
        file_path,
        dtype={"customer_phone": "string"},
    )


# ==================================================
# Customer Phone Helpers
# ==================================================

def split_customer_phones(value) -> list[str]:
    """Split a cell containing multiple phone numbers."""

    if pd.isna(value) or not str(value).strip():
        return []

    phones = re.split(
        r"[,;|،\r\n]+",
        str(value).strip(),
    )

    return [
        phone.strip()
        for phone in phones
        if phone.strip()
    ]


def normalize_customer_phone(value):
    """
    Normalize a phone number for comparison.

    1. Keep the first phone number.
    2. Remove non-digit characters.
    3. Remove the country prefix 98 or local prefix 0.

    No phone-length validation is performed.
    """

    phones = split_customer_phones(value)

    if not phones:
        return pd.NA

    phone = phones[0]

    # Remove spaces, + signs, and other non-digit characters.
    digits = re.sub(r"\D", "", phone)

    # Remove the country prefix 98 or the local prefix 0.
    if digits.startswith("98"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = digits[1:]

    if not digits:
        return pd.NA

    return digits


# ==================================================
# Dataset Report
# ==================================================

def print_column_dictionary(df: pd.DataFrame) -> None:
    """Display column names, data types, missing values, and descriptions."""

    column_info = pd.DataFrame(
        [
            {
                "Column": column,
                "Data Type": str(df[column].dtype),
                "Missing Values": int(df[column].isna().sum()),
                "Description": COLUMN_DESCRIPTIONS.get(
                    column,
                    "Description not defined",
                ),
            }
            for column in df.columns
        ]
    )

    print("\nDATA DICTIONARY")

    print(
        tabulate(
            column_info.values.tolist(),
            headers=column_info.columns.tolist(),
            tablefmt="grid",
            showindex=False,
            maxcolwidths=[24, 12, 16, 55],
            stralign="left",
            numalign="right",
        )
    )


def print_dataset_report(df: pd.DataFrame) -> None:
    """Display a basic report about the dataset."""

    print("\n" + "=" * 80)
    print("DATASET OVERVIEW")
    print("=" * 80)

    print(f"Number of Rows    : {df.shape[0]}")
    print(f"Number of Columns : {df.shape[1]}")

    print_column_dictionary(df)


# ==================================================
# Categorical Values
# ==================================================

def print_status_values(df: pd.DataFrame) -> None:

    print("\nAVAILABLE STATUS VALUES")
    print("=" * 40)

    if "status" not in df.columns:
        print("Column 'status' was not found.")
        return

    status_counts = (
        df["status"]
        .value_counts(dropna=False)
        .rename_axis("Status")
        .reset_index(name="Count")
    )

    print(
        tabulate(
            status_counts.values.tolist(),
            headers=status_counts.columns.tolist(),
            tablefmt="grid",
            showindex=False,
        )
    )


def print_channel_values(df: pd.DataFrame) -> None:

    print("\nAVAILABLE CHANNEL VALUES")
    print("=" * 40)

    if "channel" not in df.columns:
        print("Column 'channel' was not found.")
        return

    channel_counts = (
        df.groupby("channel", dropna=False)
        .size()
        .reset_index(name="Count")
    )

    print(
        tabulate(
            channel_counts.values.tolist(),
            headers=channel_counts.columns.tolist(),
            tablefmt="grid",
            showindex=False,
        )
    )


def print_call_reason_values(df: pd.DataFrame) -> None:

    print("\nAVAILABLE CALL REASON VALUES")
    print("=" * 40)

    if "call_reason" not in df.columns:
        print("Column 'call_reason' was not found.")
        return

    call_reason_counts = (
        df.groupby("call_reason", dropna=False)
        .size()
        .reset_index(name="Count")
    )

    print(
        tabulate(
            call_reason_counts.values.tolist(),
            headers=call_reason_counts.columns.tolist(),
            tablefmt="grid",
            showindex=False,
        )
    )


def print_queue_values(df: pd.DataFrame) -> None:

    print("\nAVAILABLE QUEUE VALUES")
    print("=" * 40)

    if "queue" not in df.columns:
        print("Column 'queue' was not found.")
        return

    queue_counts = (
        df.groupby("queue", dropna=False)
        .size()
        .reset_index(name="Count")
    )

    print(
        tabulate(
            queue_counts.values.tolist(),
            headers=queue_counts.columns.tolist(),
            tablefmt="grid",
            showindex=False,
        )
    )


# ==================================================
# Agents by Queue
# ==================================================

def print_agents_by_queue(df: pd.DataFrame) -> None:

    print("\nAGENTS BY QUEUE")
    print("=" * 50)

    if "queue" not in df.columns or "agent_id" not in df.columns:
        print("Required columns 'queue' or 'agent_id' were not found.")
        return

    agent_queue = (
        df.dropna(subset=["agent_id"])
        .groupby("queue", dropna=False)["agent_id"]
        .agg(
            lambda agents: ", ".join(
                sorted(agents.astype(str).unique())
            )
        )
        .reset_index(name="Agent IDs")
    )

    print(
        tabulate(
            agent_queue.values.tolist(),
            headers=agent_queue.columns.tolist(),
            tablefmt="grid",
            showindex=False,
        )
    )


# ==================================================
# Start Time Validation
# ==================================================

def check_invalid_start_times(df: pd.DataFrame) -> None:

    print("\nINVALID START TIMES")
    print("=" * 40)

    required_columns = ["call_id", "start_time"]

    if not all(column in df.columns for column in required_columns):
        print("Required columns were not found.")
        return

    # Accept H:MM:SS or HH:MM:SS, with a valid 24-hour time.
    time_pattern = r"(?:[01]?\d|2[0-3]):[0-5]\d:[0-5]\d"

    invalid_time = ~(
        df["start_time"]
        .astype("string")
        .str.strip()
        .str.fullmatch(time_pattern, na=False)
    )

    invalid_calls = df.loc[
        invalid_time,
        ["call_id", "start_time"],
    ]

    if invalid_calls.empty:
        print("No invalid start times found.")
    else:
        print(invalid_calls.to_string(index=False))


# ==================================================
# Negative Values Validation
# ==================================================

def check_negative_values(df: pd.DataFrame) -> None:

    columns_to_check = [
        "transfer_count",
        "csat_score",
        "after_call_work_seconds",
        "hold_seconds",
        "handle_seconds",
        "wait_seconds",
    ]

    print("\nNEGATIVE VALUES CHECK")
    print("=" * 50)

    negative_values = []

    for column in columns_to_check:

        if column not in df.columns:
            print(f"Column '{column}' was not found.")
            continue

        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        invalid_mask = numeric_values < 0

        if invalid_mask.any():

            column_results = (
                df.loc[invalid_mask, ["call_id", column]]
                .rename(columns={column: "Value"})
                .copy()
            )

            column_results.insert(1, "Column", column)

            negative_values.append(column_results)

    if negative_values:
        result = pd.concat(
            negative_values,
            ignore_index=True,
        )

        print(
            tabulate(
                result.values.tolist(),
                headers=result.columns.tolist(),
                tablefmt="grid",
                showindex=False,
            )
        )
    else:
        print("No negative values found.")


# ==================================================
# Call Date Validation
# ==================================================

def check_invalid_call_dates(df: pd.DataFrame) -> None:

    print("\nINVALID CALL DATES")
    print("=" * 40)

    required_columns = ["call_id", "call_date"]

    if not all(column in df.columns for column in required_columns):
        print("Required columns were not found.")
        return

    date_values = (
        df["call_date"]
        .astype("string")
        .str.strip()
    )

    # Expected format: M/D/YYYY or MM/DD/YYYY.
    valid_format = date_values.str.fullmatch(
        r"\d{1,2}/\d{1,2}/\d{4}",
        na=False,
    )

    # Check both the format and the actual calendar date.
    parsed_dates = pd.to_datetime(
        date_values.where(valid_format),
        format="%m/%d/%Y",
        errors="coerce",
    )

    invalid_mask = parsed_dates.isna()

    invalid_dates = df.loc[
        invalid_mask,
        ["call_id", "call_date"],
    ]

    if invalid_dates.empty:
        print("No invalid call dates found.")
    else:
        print(invalid_dates.to_string(index=False))


# ==================================================
# Customer Phone Prefix and Multiple Number Check
# ==================================================

def check_invalid_customer_phones(df: pd.DataFrame) -> None:

    print("\nCUSTOMER PHONE PREFIX AND MULTIPLE NUMBER CHECK")
    print("=" * 80)

    required_columns = ["call_id", "customer_phone"]

    if not all(column in df.columns for column in required_columns):
        print("Required columns were not found.")
        return

    phone_issues = []

    for row_number, (_, row) in enumerate(df.iterrows(), start=2):

        value = row["customer_phone"]
        phones = split_customer_phones(value)

        # Only check prefixes and multiple phone numbers.
        # Phone length is deliberately not validated.
        if not phones:
            continue

        issues = []

        if len(phones) > 1:
            issues.append(
                f"Multiple phone numbers found: {len(phones)}"
            )

        # Inspect prefixes in all phone numbers in this cell.
        for phone_number, phone in enumerate(phones, start=1):

            digits = re.sub(r"\D", "", phone)

            if digits.startswith("98"):
                issues.append(
                    f"Phone {phone_number}: country prefix 98/+98 detected"
                )

            elif digits.startswith("0"):
                issues.append(
                    f"Phone {phone_number}: local prefix 0 detected"
                )

        if issues:
            phone_issues.append(
                [
                    row_number,
                    row["call_id"],
                    value,
                    normalize_customer_phone(value),
                    "; ".join(issues),
                ]
            )

    if phone_issues:
        print(
            tabulate(
                phone_issues,
                headers=[
                    "CSV Row",
                    "Call ID",
                    "Customer Phone",
                    "Normalized First Phone",
                    "Issue",
                ],
                tablefmt="grid",
                showindex=False,
            )
        )
    else:
        print("No phone prefixes or multiple phone numbers found.")


# ==================================================
# NULL Duration Validation
# ==================================================

def check_null_duration_calls(df: pd.DataFrame) -> None:

    columns_to_check = [
        "wait_seconds",
        "hold_seconds",
        "handle_seconds",
        "after_call_work_seconds",
    ]

    print("\nCALLS WITH NULL DURATIONS")
    print("=" * 50)

    required_columns = ["call_id", "status"] + columns_to_check

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        return

    null_mask = df[columns_to_check].isna().any(axis=1)

    result = df.loc[
        null_mask,
        ["call_id", "status"] + columns_to_check,
    ]

    if result.empty:
        print("No calls found with NULL duration values.")
        return

    print(result.to_string(index=False))


def check_duplicate_call_ids(df: pd.DataFrame) -> None:

    print("\nDUPLICATE CALL IDS")
    print("=" * 50)

    if "call_id" not in df.columns:
        print("Column 'call_id' was not found.")
        return

    duplicate_ids = (
        df.loc[
            df["call_id"].notna()
            & df["call_id"].duplicated(keep=False),
            "call_id",
        ]
        .value_counts()
        .rename_axis("Call ID")
        .reset_index(name="Count")
    )

    if duplicate_ids.empty:
        print("No duplicate call IDs found.")
        return

    print(
        tabulate(
            duplicate_ids.values.tolist(),
            headers=duplicate_ids.columns.tolist(),
            tablefmt="grid",
            showindex=False,
        )
    )

# ==================================================
# Main
# ==================================================

def main() -> None:

    df = load_csv(CSV_PATH)

    print_dataset_report(df)

    print_status_values(df)
    print_channel_values(df)
    print_call_reason_values(df)
    print_queue_values(df)
    print_agents_by_queue(df)

    check_invalid_start_times(df)
    check_negative_values(df)
    check_invalid_call_dates(df)
    check_invalid_customer_phones(df)
    check_null_duration_calls(df)
    check_duplicate_call_ids(df)

if __name__ == "__main__":
    main()