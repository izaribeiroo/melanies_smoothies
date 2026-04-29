import os

import requests
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Write directly to the app.
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw: {st.__version__}")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)


def get_snowflake_session():
    config = {}
    if "snowflake" in st.secrets:
        config.update(st.secrets["snowflake"])
    else:
        for key in ("account", "user", "password", "role", "warehouse", "database", "schema"):
            value = os.environ.get(f"SNOWFLAKE_{key.upper()}")
            if value:
                config[key] = value

    required_keys = ["account", "user", "password", "warehouse", "database", "schema"]
    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        st.error(
            "Snowflake connection is not configured. "
            "Set the required Snowflake credentials in Streamlit secrets or environment variables. "
            f"Missing: {', '.join(missing)}."
        )
        return None

    try:
        return Session.builder.configs(config).create()
    except Exception as exc:
        st.error("Unable to create a Snowflake session. Please verify your credentials and network access.")
        st.exception(exc)
        return None


name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

session = get_snowflake_session()
if session is None:
    st.stop()

fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
st.dataframe(fruit_df, use_container_width=True)

fruit_options = fruit_df["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_options, max_selections=5)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list).strip()
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(
            "INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES (?, ?)",
            [ingredients_string, name_on_order],
        ).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.write(smoothiefroot_response.text)