import pandas as pd
from sodapy import Socrata
import plotly.express as px
import streamlit as st


def fetch_data(id, type):
    # Identify Socrata client and App Token
    client = Socrata("data.austintexas.gov", "F230eJHxoqwORfwqMR2Pw6gnB")
    # Fetch the most recent 50,000 rows
    json_data = client.get(id, limit=30000, order="datetime DESC")
    # Convert JSON to pandas DataFrame
    df = pd.DataFrame(json_data)
    # Rename datetime columns by 'type' argument (intake or outcome)
    df.rename(columns={"datetime": f"datetime_{type}"}, inplace=True)
    return df

def make_bar(data, grouping, xlab):
    # Create series with median figures
    series = data.groupby(grouping)["datetime_difference"].agg(["mean", "median"])
    # Create bar plot by argument
    plot = px.bar(series, title=f"Mean and Median Time in shelter by {xlab}", barmode="group",
       labels={
           grouping : xlab,
           "value" : "Time in Shelter (days)"
       })
    return plot

@st.cache_data(ttl=259200)
def fetch_and_clean():
    # FETCH DATA
    intake_df = fetch_data("wter-evkm", "intake")
    outcome_df = fetch_data("9t4d-g238", "outcome")

    # DATA CLEANING
    # Merge datasets by only animals that have an outcome
    df = pd.merge(intake_df, outcome_df, on=["animal_id", "animal_type", "name", "color", "breed"], how="inner")

    # Convert intake and outcome datetimes from object to datetime data
    df["datetime_intake"] = pd.to_datetime(df["datetime_intake"], errors='coerce')
    df["datetime_outcome"] = pd.to_datetime(df["datetime_outcome"], errors='coerce')

    # drop all duplicated rows
    df.drop_duplicates(subset=["animal_id", "datetime_intake"], keep=False, inplace=True)
    df.drop_duplicates(subset=["animal_id", "datetime_outcome"], keep=False, inplace=True)

    # Add computated column representing time spent in shelter
    df["datetime_difference"] = abs((df["datetime_outcome"]- df["datetime_intake"]).dt.days)

    # Change non Cat or Dog entries to "Other"
    df.loc[~df["animal_type"].isin(["Cat", "Dog"]), "animal_type"] = "Other"

    # Rename column for Adoption Rate Function
    df.rename(columns={"age_upon_intake": "animal_age"}, inplace=True)

    # Get animal age in years, changing all ages < 1 year to "0"
    df[["animal_age", "age_measurement"]] = df["animal_age"].str.split(" ", expand=True)
    df.loc[df["age_measurement"].isin(["day", "days", "week", "weeks", "month", "month"]), "animal_age"] = "0"
    return df
