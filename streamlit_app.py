import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

conn = None
session = None
my_dataframe = []

try:
    conn = st.connection("snowflake")
    session = conn.session()
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
except Exception:
    st.error(
        "Snowflake connection failed. Add your Snowflake credentials to `.streamlit/secrets.toml` "
        "or pass them via `st.connection` configuration."
    )
    st.write("See `.streamlit/secrets.toml.example` for the required Snowflake settings.")

if not my_dataframe:
    st.warning("No fruit options available because the Snowflake connection is not configured.")

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5,
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders(ingredients, name_on_order) "
        "VALUES ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

st.markdown("---")
st.write("### Sample fruit data")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
