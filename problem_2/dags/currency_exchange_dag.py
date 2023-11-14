import os
import requests
from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator


COUNTRIES_CURRENCIES_MAP = {
    "NGN": "Nigeria",
    "GHS": "Ghana",
    "KES": "Kenya",
    "UGX": "Uganda",
    "MAD": "Morocco",
    "XOF": "Côte d'Ivoire",
    "EGP": "Egypt",
}


@task
def pull_data_from_api() -> dict:
    """Pull Currency data for all Countries from xe.com API
    Returns:
        dict: Raw reponse content from the API
    """
    api_id = os.getenv("XE_API_ID")
    api_key = os.getenv("XE_API_KEY")
    url = "https://xecdapi.xe.com/v1/convert_from"
    params = {
        "from": "USD",
        "to": ",".join((i for i in COUNTRIES_CURRENCIES_MAP)),
        "amount": 1,
        "inverse": "true",
    }
    response = requests.get(url, auth=(api_id, api_key), params=params)
    if not response.status_code == 200:
        raise ValueError(
            f"Response Status Code: {response.status_code}\nResponse Content:{response.content}"
        )
    else:
        data = response.json()
        return data


@task
def validate_data_from_api(data: dict) -> dict:
    """Validate the data types & return in cleaned format

    Args:
        data (dict): Raw dict (json) response content from the API

    Raises:
        ValueError: Either the FROM currency if not USD or the response incomplete

    Returns:
        dict: Cleaned Data in format: "{'currency_id': [currency_to_USD_rate, USD_to_currency_rate]"
    """
    if not data["from"] == "USD":
        raise ValueError(f"Wrong from Currency: {data['from']}")
    if not len(COUNTRIES_CURRENCIES_MAP) == len(data["to"]):
        raise ValueError(
            f"Wrong number of converted currencies: we got {len(data['to'])} instead of {len(COUNTRIES_CURRENCIES_MAP)}"
        )
    else:
        cleaned_data = {}
        for i in data["to"]:
            assert isinstance(i["quotecurrency"], str)
            assert isinstance(i["mid"], float)
            assert isinstance(i["inverse"], float)
            cleaned_data.update({i["quotecurrency"]: [i["mid"], i["inverse"]]})
        return cleaned_data


@task
def store_data_to_db(data: dict) -> bool:
    """Insert currency data into database

    Args:
        data (dict): cleaned_data from in the format: "{'currency_id': [currency_to_USD_rate, USD_to_currency_rate],"

    Returns:
        bool: True if insertion successul else False
    """
    postgres_conn = PostgresHook(postgres_conn_id="autochek_db")
    postgres_conn = postgres_conn.get_conn()
    cursor = postgres_conn.cursor()
    insertion_values = ",".join(
        f"('USD', '{v[1]}', '{v[0]}', '{k}')" for k, v in data.items()
    )
    query = f"""
    INSERT INTO public.xe_currency_exchanges_rates (currency_from, usd_to_currency_rate, currency_to_usd_rate, currency_to)
        VALUES {insertion_values}
        ON CONFLICT(date_key, currency_to) 
	DO UPDATE SET 
        "timestamp" = EXCLUDED."timestamp",
        usd_to_currency_rate = EXCLUDED.usd_to_currency_rate,
	    currency_to_usd_rate = EXCLUDED.currency_to_usd_rate"""
    cursor.execute(query)
    postgres_conn.commit()
    return True


@dag(
    schedule_interval="0 1,23 * * *",  # UTC
    start_date=days_ago(1),
    catchup=True,
    default_args={
        "owner": "Mike",
        "retries": 2,
        "retry_delay": timedelta(seconds=30),
    },
    tags=["autochek", "xe", "exchange"],
)
def currency_exchange_rates():
    create_table_if_not_exists = PostgresOperator(
        postgres_conn_id="autochek_db",
        task_id="create_table_if_not_exists",
        sql="""CREATE TABLE IF NOT EXISTS xe_currency_exchanges_rates (
            id serial primary key,
            date_key date DEFAULT NOW(),
            "timestamp" TIMESTAMP DEFAULT NOW(),
            currency_from VARCHAR(10),
            usd_to_currency_rate numeric,
            currency_to_usd_rate numeric,
            currency_to VARCHAR(10),
            CONSTRAINT unique_date_currency_to UNIQUE (date_key, currency_to)
        ); """,
    )

    # Define DAG order of execution
    create_table_if_not_exists >> store_data_to_db(
        validate_data_from_api(pull_data_from_api())
    )


currency_exchange_rates()
