from pathlib import Path
import re

import pandas as pd


# ==================================================
# Paths
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "Data"

CSV_PATH = DATA_DIR / "call_center_1000_with_reason_phone.csv"
OUTPUT_PATH = DATA_DIR / "CleanedData.csv"


# ==================================================
# Load Data
# ==================================================

def load_csv(file_path: Path) -> pd.DataFrame:
    """Load the source CSV file."""

    if not file_path.is_file():
        raise FileNotFoundError(
            f"CSV file not found: {file_path}"
        )

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


def clean_customer_phone(value):
    """
    Keep the first phone number and remove its prefix.

    No phone-length validation is performed.
    No country prefix is added at the end.
    """

    phones = split_customer_phones(value)

    if not phones:
        return pd.NA

    # Keep only the first phone number.
    phone = phones[0]

    # Remove spaces, + signs, and other non-digit characters.
    digits = re.sub(r"\D", "", phone)

    # Remove the country prefix 98 or local prefix 0.
    if digits.startswith("98"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = digits[1:]

    if not digits:
        return pd.NA

    return digits


# ==================================================
# Transform Data
# ==================================================

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the ETL cleaning rules."""

    df = df.copy()

    initial_rows = len(df)

    # --------------------------------------------------
    # 1. Clean customer phone numbers
    # --------------------------------------------------

    phone_lists = df["customer_phone"].apply(
        split_customer_phones
    )

    multiple_phone_count = int(
        phone_lists.map(
            lambda phones: len(phones) > 1
        ).sum()
    )

    df["customer_phone"] = (
        df["customer_phone"]
        .apply(clean_customer_phone)
        .astype("string")
    )

    print(
        "Rows containing multiple phone numbers "
        f"(first number retained): {multiple_phone_count}"
    )

    # No rows are removed based on phone-number length.

    # --------------------------------------------------
    # 2. Remove duplicate call IDs
    # --------------------------------------------------

    duplicate_count = int(
        df["call_id"].duplicated(keep="first").sum()
    )

    df = df.drop_duplicates(
        subset=["call_id"],
        keep="first",
    ).copy()

    print(
        f"Duplicate call ID rows removed: {duplicate_count}"
    )

    # --------------------------------------------------
    # 3. Replace NULL duration values with 0
    # --------------------------------------------------

    duration_columns = [
        "wait_seconds",
        "hold_seconds",
        "handle_seconds",
        "after_call_work_seconds",
    ]

    for column in duration_columns:
        df[column] = (
            pd.to_numeric(df[column], errors="raise")
            .fillna(0)
        )

    # --------------------------------------------------
    # 4. Convert negative hold_seconds values to positive
    # --------------------------------------------------

    df["hold_seconds"] = df["hold_seconds"].abs()

    # --------------------------------------------------
    # 5. Replace NULL csat_score values with 0
    # --------------------------------------------------

    df["csat_score"] = (
        pd.to_numeric(df["csat_score"], errors="raise")
        .fillna(0)
    )

    # --------------------------------------------------
    # 6. Replace NULL first_contact_resolution values with 0
    # --------------------------------------------------

    df["first_contact_resolution"] = (
        df["first_contact_resolution"]
        .astype("object")
        .fillna(0)
    )

    # --------------------------------------------------
    # 7. Replace NULL agent_id values with A01
    # --------------------------------------------------

    df["agent_id"] = (
        df["agent_id"]
        .astype("string")
        .fillna("A01")
    )

    # --------------------------------------------------
    # 8. Report cleaning results
    # --------------------------------------------------

    print(f"Original row count: {initial_rows}")
    print(f"Cleaned row count: {len(df)}")
    print(
        f"Total rows removed: {initial_rows - len(df)}"
    )

    return df


# ==================================================
# Save Cleaned Data
# ==================================================

def main() -> None:
    """Run the ETL process and save the cleaned dataset."""

    print("Starting ETL process...")

    df = load_csv(CSV_PATH)

    cleaned_df = clean_data(df)

    # Safety check: do not overwrite the output with an empty dataset.
    if not df.empty and cleaned_df.empty:
        raise ValueError(
            "ETL produced an empty dataset. "
            "The existing output file was not overwritten."
        )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Overwrite CleanedData.csv if it already exists.
    cleaned_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nETL process completed successfully.")
    print(f"Cleaned dataset saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()