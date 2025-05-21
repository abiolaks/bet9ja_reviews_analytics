import streamlit as st
import json
from azure.storage.blob import BlobServiceClient

# Use Streamlit secrets for configuration
BLOB_CONNECTION_STRING = st.secrets["BLOB_CONNECTION_STRING"]
OUTPUT_CONTAINER_NAME = st.secrets.get("OUTPUT_CONTAINER_NAME", "output")

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER_NAME)

st.title("Real-Time Sentiment Dashboard")

sentiments = []


# List blobs and read sentiment results
def load_sentiments():
    blobs = container_client.list_blobs()
    results = []
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        data = blob_client.download_blob().readall()
        try:
            result = json.loads(data)
            results.append(result)
        except Exception:
            continue
    return results


sentiments = load_sentiments()

if sentiments:
    st.write(f"Loaded {len(sentiments)} sentiment results.")
    st.dataframe(
        [
            {
                "Review": s["review"],
                "Sentiment": s["sentiment"],
                "Positive": s["confidence_scores"]["positive"],
                "Neutral": s["confidence_scores"]["neutral"],
                "Negative": s["confidence_scores"]["negative"],
            }
            for s in sentiments
        ]
    )
    st.bar_chart(
        {
            "Positive": [s["confidence_scores"]["positive"] for s in sentiments],
            "Neutral": [s["confidence_scores"]["neutral"] for s in sentiments],
            "Negative": [s["confidence_scores"]["negative"] for s in sentiments],
        }
    )
else:
    st.info("No sentiment results found in the output container.")
