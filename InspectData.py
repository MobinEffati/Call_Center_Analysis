from pathlib import Path
import re
import pandas as pd
from tabulate import tabulate


BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    BASE_DIR
    / "Data"
    / "call_center_1000_with_reason_phone.csv"
)


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


def load_csv(file_path: Path) -> pd.DataFrame:

    if not file_path.is_file():
        raise FileNotFoundError(
            f"CSV file not found: {file_path}"
        )

    return pd.read_csv(file_path)


def print_column_dictionary(df: pd.DataFrame) -> None:

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
def print_agents_by_queue(df: pd.DataFrame) -> None:

    print("\nAGENTS BY QUEUE")
    print("=" * 50)

    if "queue" not in df.columns or "agent_id" not in df.columns:
        print("Required columns 'queue' or 'agent_id' were not found.")
        return

    agent_queue = (
        df.dropna(subset=["agent_id"])
        .groupby("queue", dropna=False)["agent_id"]
        .agg(lambda agents: ", ".join(sorted(agents.astype(str).unique())))
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
def check_invalid_start_times(df: pd.DataFrame) -> None:

    print("\nINVALID START TIMES")
    print("=" * 40)

    time_pattern = r"(?:[01]?\d|2[0-3]):[0-5]\d:[0-5]\d"

    invalid_time = ~df["start_time"].astype("string").str.strip().str.fullmatch(
        time_pattern,
        na=False
    )

    invalid_calls = df.loc[invalid_time, ["call_id", "start_time"]]

    print(invalid_calls.to_string(index=False))


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

        numeric_values = pd.to_numeric(df[column], errors="coerce")
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
        result = pd.concat(negative_values, ignore_index=True)

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

def check_invalid_call_dates(df: pd.DataFrame) -> None:

    print("\nINVALID CALL DATES")
    print("=" * 40)

    date_values = df["call_date"].astype("string").str.strip()

    # Expected format: M/D/YYYY or MM/DD/YYYY
    valid_format = date_values.str.fullmatch(
        r"\d{1,2}/\d{1,2}/\d{4}",
        na=False
    )

    # Check both format and actual calendar date
    parsed_dates = pd.to_datetime(
        date_values.where(valid_format),
        format="%m/%d/%Y",
        errors="coerce"
    )

    invalid_mask = parsed_dates.isna()

    invalid_dates = df.loc[
        invalid_mask,
        ["call_id", "call_date"]
    ]

    if invalid_dates.empty:
        print("No invalid call dates found.")
    else:
        print(invalid_dates.to_string(index=False))
def check_invalid_customer_phones(df: pd.DataFrame) -> None:

    print("\nINVALID CUSTOMER PHONE NUMBERS")
    print("=" * 50)

    if "customer_phone" not in df.columns or "call_id" not in df.columns:
        print("Required columns 'customer_phone' or 'call_id' were not found.")
        return

    phone_pattern = re.compile(r"(?<!\d)(?:98)?9\d{8}(?!\d)")

    invalid_phones = []

    for row_number, (_, row) in enumerate(df.iterrows(), start=2):

        value = row["customer_phone"]

        if pd.isna(value) or not str(value).strip():
            invalid_phones.append([
                row_number,
                row["call_id"],
                value,
                "Missing phone number",
            ])
            continue

        raw_phone = str(value).strip()
        digits = re.sub(r"\D", "", raw_phone)

        phone_matches = phone_pattern.findall(raw_phone)
        issues = []

        if len(phone_matches) > 1:
            issues.append(
                f"Multiple phone numbers found: {len(phone_matches)}"
            )

            if any(phone.startswith("98") and len(phone) == 11
                   for phone in phone_matches):
                issues.append("98 prefix detected")

        elif (
            len(digits) == 11
            and digits.startswith("98")
            and re.fullmatch(r"9\d{8}", digits[2:])
        ):
            issues.append("98 prefix detected; expected 9 digits")

        elif len(digits) != 9:
            issues.append(f"Invalid length: {len(digits)} digits; expected 9")

        elif not re.fullmatch(r"9\d{8}", digits):
            issues.append("Invalid mobile number format")

        elif raw_phone != digits:
            issues.append("Invalid format; expected digits only")

        if issues:
            invalid_phones.append([
                row_number,
                row["call_id"],
                raw_phone,
                "; ".join(issues),
            ])

    if invalid_phones:
        print(
            tabulate(
                invalid_phones,
                headers=[
                    "CSV Row",
                    "Call ID",
                    "Customer Phone",
                    "Issue",
                ],
                tablefmt="grid",
                showindex=False,
            )
        )
    else:
        print("No invalid customer phone numbers found.")

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
        column for column in required_columns
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
def check_duplicate_customer_phones(df: pd.DataFrame) -> None:

    print("\nDUPLICATE CUSTOMER PHONE NUMBERS")
    print("=" * 50)

    if "customer_phone" not in df.columns or "call_id" not in df.columns:
        print("Required columns were not found.")
        return

    duplicate_mask = (
        df["customer_phone"].notna()
        & df["customer_phone"].duplicated(keep=False)
    )

    duplicates = (
        df.loc[duplicate_mask, ["customer_phone", "call_id"]]
        .sort_values("customer_phone")
    )

    if duplicates.empty:
        print("No duplicate customer phone numbers found.")
        return

    print(
        tabulate(
            duplicates.values.tolist(),
            headers=["Customer Phone", "Call ID"],
            tablefmt="grid",
            showindex=False,
        )
    )

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
    check_duplicate_customer_phones(df)

if __name__ == "__main__":
    main()