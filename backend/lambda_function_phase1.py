from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os

def process_nutritional_data_from_azurite():

    connect_str = (
        "DefaultEndpointsProtocol=http;"
        "AccountName=localstore;"
        "AccountKey=MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=;"
        "BlobEndpoint=http://127.0.0.1:10000/localstore;"
    )

    container_name = "datasets"
    blob_name = "All_Diets.csv"

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    blob_data = blob_client.download_blob().readall()

    df = pd.read_csv(io.BytesIO(blob_data))

    df.columns = df.columns.str.strip()

    nutrition_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]

    for col in nutrition_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].mean())

    avg_macros = df.groupby("Diet_type")[nutrition_cols].mean()

    results = avg_macros.reset_index().to_dict(orient="records")

    os.makedirs("simulated_nosql", exist_ok=True)

    with open("simulated_nosql/results.json", "w") as file:
        json.dump(results, file, indent=4)

    print("Data processed successfully.")
    print("Results saved to simulated_nosql/results.json")

    return results

if __name__ == "__main__":
    process_nutritional_data_from_azurite()

