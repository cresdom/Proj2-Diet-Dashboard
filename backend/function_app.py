import azure.functions as func
import datetime
import io
import json
import logging
import os
import time

import pandas as pd
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """Clean the diet dataset and prepare dashboard data."""

    df.columns = df.columns.str.strip()

    required_columns = [
        "Diet_type",
        "Cuisine_type",
        "Protein(g)",
        "Carbs(g)",
        "Fat(g)",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {missing_columns}"
        )

    nutrition_columns = ["Protein(g)", "Carbs(g)", "Fat(g)"]

    for column in nutrition_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        df[column] = df[column].fillna(df[column].mean())

    df["Diet_type"] = df["Diet_type"].fillna("Unknown").astype(str).str.strip()

    df["Cuisine_type"] = (
        df["Cuisine_type"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    averages = (
        df.groupby("Diet_type")[nutrition_columns]
        .mean()
        .round(2)
        .reset_index()
    )

    averages = averages.rename(
        columns={
            "Protein(g)": "protein",
            "Carbs(g)": "carbs",
            "Fat(g)": "fat",
        }
    )

    diet_distribution = (
        df["Diet_type"]
        .value_counts()
        .rename_axis("diet_type")
        .reset_index(name="count")
    )

    cuisine_distribution = (
        df["Cuisine_type"]
        .value_counts()
        .head(10)
        .rename_axis("cuisine_type")
        .reset_index(name="count")
    )

    overall_averages = {
        "protein": round(float(df["Protein(g)"].mean()), 2),
        "carbs": round(float(df["Carbs(g)"].mean()), 2),
        "fat": round(float(df["Fat(g)"].mean()), 2),
    }

    return {
        "averages_by_diet": averages.to_dict(orient="records"),
        "diet_distribution": diet_distribution.to_dict(orient="records"),
        "cuisine_distribution": cuisine_distribution.to_dict(orient="records"),
        "overall_averages": overall_averages,
        "records_processed": int(len(df)),
        "diet_type_count": int(df["Diet_type"].nunique()),
        "cuisine_type_count": int(df["Cuisine_type"].nunique()),
    }


def load_blob_dataset() -> pd.DataFrame:
    """Download the diet dataset from Azure Blob Storage."""

    connection_string = os.environ.get(
        "DIET_STORAGE_CONNECTION_STRING"
    )

    container_name = os.environ.get(
        "DIET_CONTAINER_NAME",
        "diet-data",
    )

    blob_name = os.environ.get(
        "DIET_BLOB_NAME",
        "All_Diets.csv",
    )

    if not connection_string:
        raise ValueError(
            "DIET_STORAGE_CONNECTION_STRING is not configured."
        )

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name,
    )

    csv_bytes = blob_client.download_blob().readall()

    return pd.read_csv(io.BytesIO(csv_bytes))


@app.route(
    route="diet_dashboard",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=["GET"],
)
def diet_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Diet dashboard function started.")

    start_time = time.perf_counter()

    try:
        df = load_blob_dataset()
        analysis = analyze_dataframe(df)

        execution_time_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        response_data = {
            "status": "success",
            "data_source": (
                "Azure Blob Storage: "
                "diet-data/All_Diets.csv"
            ),
            "metadata": {
                "records_processed": analysis["records_processed"],
                "diet_type_count": analysis["diet_type_count"],
                "cuisine_type_count": analysis["cuisine_type_count"],
                "execution_time_ms": execution_time_ms,
                "generated_at_utc": (
                    datetime.datetime.now(datetime.timezone.utc)
                    .isoformat()
                ),
            },
            "overall_averages": analysis["overall_averages"],
            "averages_by_diet": analysis["averages_by_diet"],
            "diet_distribution": analysis["diet_distribution"],
            "cuisine_distribution": analysis["cuisine_distribution"],
        }

        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "no-store",
            },
        )

    except Exception as error:
        logging.exception("Diet analysis failed.")

        return func.HttpResponse(
            json.dumps(
                {
                    "status": "error",
                    "message": str(error),
                }
            ),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
            },
        )
