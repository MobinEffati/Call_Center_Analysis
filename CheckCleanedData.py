from pathlib import Path

import pandas as pd
import pytest


# ==================================================
# Paths and Constants
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

CLEANED_DATA_PATH = (
    BASE_DIR
    / "Data"
    / "CleanedData.csv"
)

DURATION_COLUMNS = [
    "wait_seconds",
    "hold_seconds",
    "handle_seconds",
    "after_call_work_seconds",
]

EXPECTED_COLUMNS = [
    "call_id",
    "call_date",
    "start_time",
    "customer_phone",
    "call_reason",
    "agent_id",
    "queue",
    "channel",
    "status",
    "wait_seconds",
    "handle_seconds",
    "hold_seconds",
    "after_call_work_seconds",
    "csat_score",
    "first_contact_resolution",
    "transfer_count",
]


# ==================================================
# Load Cleaned Dataset
# ==================================================

@pytest.fixture(scope="module")
def cleaned_df() -> pd.DataFrame:
    """Load the dataset already produced by the ETL process."""

    if not CLEANED_DATA_PATH.is_file():
        pytest.fail(
            "CleanedData.csv was not found. "
            "Run CleanData.py before executing the tests."
        )

    df = pd.read_csv(
        CLEANED_DATA_PATH,
        dtype={"customer_phone": "string"},
    )

    if df.empty:
        pytest.fail(
            "CleanedData.csv is empty. "
            "The ETL output must be investigated."
        )

    return df


# ==================================================
# 1. Dataset Structure
# ==================================================

def test_expected_columns_exist(cleaned_df):
    """All expected dataset columns must exist."""

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in cleaned_df.columns
    ]

    assert not missing_columns, (
        f"Missing columns in cleaned dataset: {missing_columns}"
    )


def test_cleaned_dataset_is_not_empty(cleaned_df):
    """The cleaned dataset must contain records."""

    assert len(cleaned_df) > 0


# ==================================================
# 2. Duplicate Call IDs
# ==================================================

def test_call_ids_are_unique(cleaned_df):
    """Each call_id must appear only once."""

    assert cleaned_df["call_id"].notna().all(), (
        "NULL values were found in call_id."
    )

    duplicate_mask = cleaned_df["call_id"].duplicated(
        keep=False
    )

    duplicates = cleaned_df.loc[
        duplicate_mask,
        "call_id",
    ].unique().tolist()

    assert not duplicates, (
        f"Duplicate call IDs found: {duplicates}"
    )


# ==================================================
# 3. Customer Phone Numbers
# ==================================================

def test_customer_phones_contain_only_digits(cleaned_df):
    """
    Non-empty phone numbers must contain digits only.

    Phone-number length is deliberately not checked.
    """

    phones = (
        cleaned_df["customer_phone"]
        .dropna()
        .astype("string")
        .str.strip()
    )

    phones = phones[phones.ne("")]

    invalid_mask = ~phones.str.fullmatch(
        r"\d+",
        na=False,
    )

    invalid_phones = phones[invalid_mask].tolist()

    assert not invalid_phones, (
        f"Phone numbers containing non-digit characters: "
        f"{invalid_phones[:20]}"
    )


def test_customer_phone_prefixes_are_removed(cleaned_df):
    """
    Remaining non-empty phone numbers must not start with
    the local prefix 0 or country prefix 98.

    No phone-length validation is performed.
    """

    phones = (
        cleaned_df["customer_phone"]
        .dropna()
        .astype("string")
        .str.strip()
    )

    phones = phones[phones.ne("")]

    invalid_prefix_mask = (
        phones.str.startswith("0")
        | phones.str.startswith("98")
    )

    invalid_phones = phones[invalid_prefix_mask].tolist()

    assert not invalid_phones, (
        "Phone numbers with an unremoved prefix were found: "
        f"{invalid_phones[:20]}"
    )


def test_customer_phones_do_not_have_added_plus98(cleaned_df):
    """The ETL must not append the +98 prefix."""

    phones = (
        cleaned_df["customer_phone"]
        .dropna()
        .astype("string")
    )

    assert not phones.str.startswith("+98").any()


# ==================================================
# 4. Duration Columns
# ==================================================

def test_duration_columns_have_no_null_values(cleaned_df):
    """All NULL duration values must be replaced with zero."""

    for column in DURATION_COLUMNS:

        numeric_values = pd.to_numeric(
            cleaned_df[column],
            errors="coerce",
        )

        assert numeric_values.notna().all(), (
            f"NULL or non-numeric values remain in {column}."
        )


def test_hold_seconds_contains_no_negative_values(cleaned_df):
    """All hold_seconds values must be non-negative."""

    hold_values = pd.to_numeric(
        cleaned_df["hold_seconds"],
        errors="coerce",
    )

    assert hold_values.notna().all(), (
        "NULL or non-numeric values remain in hold_seconds."
    )

    negative_values = hold_values[hold_values < 0]

    assert negative_values.empty, (
        f"Negative hold_seconds values found: "
        f"{negative_values.tolist()[:20]}"
    )


# ==================================================
# 5. Customer Satisfaction
# ==================================================

def test_csat_score_has_no_null_values(cleaned_df):
    """NULL csat_score values must be replaced with zero."""

    csat_values = pd.to_numeric(
        cleaned_df["csat_score"],
        errors="coerce",
    )

    assert csat_values.notna().all(), (
        "NULL or non-numeric values remain in csat_score."
    )


# ==================================================
# 6. First Contact Resolution
# ==================================================

def test_first_contact_resolution_has_no_null_values(cleaned_df):
    """NULL first_contact_resolution values must be replaced with zero."""

    assert cleaned_df["first_contact_resolution"].notna().all(), (
        "NULL values remain in first_contact_resolution."
    )


# ==================================================
# 7. Agent ID
# ==================================================

def test_agent_id_has_no_null_or_empty_values(cleaned_df):
    """NULL agent_id values must be replaced with A01."""

    agent_ids = (
        cleaned_df["agent_id"]
        .astype("string")
        .str.strip()
    )

    invalid_agents = (
        agent_ids.isna()
        | agent_ids.eq("")
    )

    assert not invalid_agents.any(), (
        "NULL or empty agent_id values remain in the dataset."
    )


# ==================================================
# 8. Numeric Duration Integrity
# ==================================================

def test_duration_columns_are_numeric(cleaned_df):
    """Duration columns must contain numeric values."""

    for column in DURATION_COLUMNS:

        numeric_values = pd.to_numeric(
            cleaned_df[column],
            errors="coerce",
        )

        assert numeric_values.notna().all(), (
            f"Non-numeric values found in {column}."
        )