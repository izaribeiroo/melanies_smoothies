import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

conn = None
session = None
fruit_choices = []
pd_df = None

try:
    conn = st.connection("snowflake")
    session = conn.session()
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    pd_df = my_dataframe.to_pandas()
    st.dataframe(pd_df)
    fruit_choices = pd_df['FRUIT_NAME'].tolist()
except Exception:
    st.error(
        "Snowflake connection failed. Add your Snowflake credentials to `.streamlit/secrets.toml` "
        "or pass them via `st.connection` configuration."
    )
    st.write("See `.streamlit/secrets.toml.example` for the required Snowflake settings.")

if not fruit_choices:
    st.warning("No fruit options available because the Snowflake connection is not configured.")

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_choices,
    max_selections=5,
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        if pd_df is not None:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.subheader(fruit_chosen + ' Nutrition Information')
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.warning('Nutrition information is unavailable without a Snowflake connection.')

    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders(ingredients, name_on_order) "
        "VALUES ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    time_to_insert = st.button('Submit Order')

    if time_to_insert and session is not None:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
    elif time_to_insert:
        st.error('Cannot submit order because the Snowflake connection is not configured.')
