import os
from typing import Dict, Tuple, Optional

import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account


@st.cache_resource
def get_bigquery_client() -> Optional[bigquery.Client]:
    """Create a reusable BigQuery client using Streamlit secrets or env auth."""
    try:
        if "gcp_service_account" in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            return bigquery.Client(
                credentials=credentials,
                project=st.secrets["gcp_service_account"]["project_id"],
                location=st.secrets.get("gcp_location", "europe-west3"),
            )

        # Fall back to application default credentials / env vars
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
        return bigquery.Client(project=project_id) if project_id else bigquery.Client()
    except Exception as exc:
        st.error(
            "BigQuery client initialization failed. "
            "Check Streamlit secrets or GOOGLE_APPLICATION_CREDENTIALS. "
            f"Details: {exc}"
        )
        return None


def _build_query_params(
    params: Optional[Dict[str, Tuple[str, object]]]
) -> Optional[list]:
    if not params:
        return None
    query_params = []
    for name, (param_type, value) in params.items():
        query_params.append(bigquery.ScalarQueryParameter(name, param_type, value))
    return query_params


@st.cache_data(ttl=3600)
def run_query(sql: str, params: Optional[Dict[str, Tuple[str, object]]] = None) -> Optional[pd.DataFrame]:
    """Run a parameterized BigQuery SQL query and return a DataFrame."""
    client = get_bigquery_client()
    if client is None:
        return None

    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=_build_query_params(params)
        )
        return client.query(sql, job_config=job_config).to_dataframe()
    except Exception as exc:
        st.error(
            "BigQuery query failed. Validate the SQL, parameters, and dataset access. "
            f"Details: {exc}"
        )
        return None
