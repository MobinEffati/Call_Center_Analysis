import json
from datetime import date

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

import KPI as kpi


app = FastAPI(
    title="Call Center Analytics API",
    description="API for Call Center performance KPIs",
    version="1.0.0",
)


# ==================================================
# Helper Functions
# ==================================================

def get_filtered_data(
    team: str | None = None,
    shift: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Load data and apply request filters."""

    try:
        df = kpi.load_cleaned_data()

        return kpi.filter_data(
            df,
            team=team,
            shift=shift,
            start_date=(
                start_date.isoformat()
                if start_date else None
            ),
            end_date=(
                end_date.isoformat()
                if end_date else None
            ),
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "CleanedData.csv was not found. "
                "Run CleanData.py before using the API."
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


def dataframe_to_records(
    df: pd.DataFrame,
) -> list[dict]:
    """Convert a DataFrame to JSON-compatible records."""

    return json.loads(
        df.to_json(
            orient="records",
            date_format="iso",
        )
    )


def filters_response(
    team: str | None,
    shift: str | None,
    start_date: date | None,
    end_date: date | None,
) -> dict:
    """Return the filters used in the request."""

    return {
        "team": team,
        "shift": shift,
        "start_date": (
            start_date.isoformat()
            if start_date else None
        ),
        "end_date": (
            end_date.isoformat()
            if end_date else None
        ),
    }


# ==================================================
# General
# ==================================================

@app.get("/", tags=["General"])
def root():
    return {
        "message": "Call Center Analytics API",
        "docs": "/docs",
    }


# ==================================================
# Overall KPI Summary
# ==================================================

@app.get("/api/kpis/summary", tags=["KPIs"])
def get_kpi_summary(
    team: str | None = Query(default=None),
    shift: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):
    """Return KPI summary with optional filters."""

    df = get_filtered_data(
        team=team,
        shift=shift,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "filters": filters_response(
            team,
            shift,
            start_date,
            end_date,
        ),
        "kpis": kpi.calculate_kpis(df),
    }


# ==================================================
# KPI by Team
# ==================================================

@app.get("/api/kpis/teams", tags=["KPIs"])
def get_kpis_by_team(
    shift: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):
    """Return KPI metrics for each team."""

    df = get_filtered_data(
        shift=shift,
        start_date=start_date,
        end_date=end_date,
    )

    result = kpi.calculate_kpis_by_team(df)

    return {
        "filters": filters_response(
            None,
            shift,
            start_date,
            end_date,
        ),
        "count": len(result),
        "data": dataframe_to_records(result),
    }


# ==================================================
# KPI by Shift
# ==================================================

@app.get("/api/kpis/shifts", tags=["KPIs"])
def get_kpis_by_shift(
    team: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):
    """Return KPI metrics for each shift."""

    df = get_filtered_data(
        team=team,
        start_date=start_date,
        end_date=end_date,
    )

    result = kpi.calculate_kpis_by_shift(df)

    return {
        "filters": filters_response(
            team,
            None,
            start_date,
            end_date,
        ),
        "count": len(result),
        "data": dataframe_to_records(result),
    }


# ==================================================
# Daily KPI
# ==================================================

@app.get("/api/kpis/daily", tags=["KPIs"])
def get_daily_kpis(
    team: str | None = Query(default=None),
    shift: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):
    """Return daily KPI metrics with optional filters."""

    df = get_filtered_data(
        team=team,
        shift=shift,
        start_date=start_date,
        end_date=end_date,
    )

    result = kpi.calculate_daily_kpis(df)

    return {
        "filters": filters_response(
            team,
            shift,
            start_date,
            end_date,
        ),
        "count": len(result),
        "data": dataframe_to_records(result),
    }