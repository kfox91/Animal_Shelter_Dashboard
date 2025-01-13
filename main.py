#!/usr/bin/env python

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import functions
import datetime as dt
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("Animal Shelter Data Dashboard")
st.write("This dashboard visualizes Animal Shelter data and provides insightful monitoring metrics. Two datasets, representing intakes and outcomes, were merged and are the source for the plots. I created this dashboard as a personal project. I love pets and wanted to create something using my newly learned data science skills. Any questions about the dashboard can be answer by contacting kyzerf@uark.edu. Enjoy!")


# Fetch and Clean Data
df = functions.fetch_and_clean()

# Adoption Rate Bar Graph
st.markdown("#### :blue[Time in Shelter by Variable]")
ar_option = st.selectbox(label="Select variable to visualize",
             options=("Outcome Type", "Intake Type", "Animal Type", "Animal Age (Years)", "Intake Conditon"))

if ar_option != "Animal Age (Years)":
    ar_option_var = (ar_option.lower()).replace(" ", "_")
else:
    ar_option_var = "animal_age"
# Write Graph
st.write(functions.make_bar(df, ar_option_var, ar_option))


#---


# Intake condition by outcomes Heatmap
st.markdown("#### :blue[Intakes by Outcomes Heatmap]")
# Radio Button for x axis
hm_radio = st.radio(label="Select x-axis", options=("Intake condition", "Intake type"), horizontal=True)
# Radio Button for z axis
hm_measurement = st.radio(label="Select Measurment", options=("avg", "count"), horizontal=True)
hm_radio_var = (hm_radio.replace(" ", "_").lower())
# Write Graph
st.write(px.density_heatmap(df, x=hm_radio_var, y="outcome_type", z="datetime_difference", title=f"{hm_radio}s by Outcome Types",
                            histfunc=hm_measurement, color_continuous_scale="Viridis",
                            labels={
                                "outcome_type":"Outcome Type",
                                "datetime_difference": "Days spent in Shelter",
                                hm_radio_var: hm_radio
                            }))


#---


# Stacked Bar for animal population by outcome and intake
st.markdown("#### :blue[Intake and Outcome Distribution Across Animal Types]")
# Select Box
sb_option = st.selectbox(label="Select variable to visualize",
             options=("Intake Type", "Outcome Type"))
if sb_option == "Intake Type":
    sb_option_var = "intake_type"
else:
    sb_option_var = "outcome_type"
# Write Histogram
st.write(px.histogram(df, x="animal_type", y=sb_option_var, title=f"{sb_option} Distribution", 
                      histfunc="count", color=sb_option_var,
                      labels={
                          "animal_type": "Animal Type",
                          sb_option_var: sb_option,
                          "count": "Population"
                          }))



st.markdown("#### :blue[Time Series Analysis]")
# Filter Data to only Last Year
last_year = dt.datetime.now().year - 1
ly_df = df[(df["datetime_intake"].dt.year) == last_year]
# Month-by-Month Analysis
ly_df["month"] = ly_df["datetime_intake"].dt.month
ly_df["month_name"] = ly_df["datetime_intake"].dt.month_name()
month_series = ly_df.groupby(["month", "month_name"], as_index=False).count()
month_bar = px.bar(month_series, x="month_name", y="animal_id")
# Trend Overtime
trend_series = df.groupby(pd.Grouper(key="datetime_intake", axis=0, freq="7D"))["animal_id"].count()
ts_bar = px.line(trend_series, x=trend_series.index, y="animal_id", title=f"Intakes Per Week Since {(trend_series.index[0]).date()}",
                 labels={
                     "animal_id": "# of Intakes",
                     "datetime_intake": "Week"
                 })
# Assemble Subplots
subplt = make_subplots(rows=1, cols=2, subplot_titles=(f"Intakes Per Month in {last_year}", f"Intakes Per Week Since {(trend_series.index[0]).date()}"))
subplt.add_trace(month_bar.data[0], row=1, col=1)
subplt.add_trace(ts_bar.data[0], row=1, col=2)
subplt.update_xaxes(title_text="Month", tickformat="%b", row=1, col=1)
subplt.update_xaxes(title_text="Week", row=1, col=2)
subplt.update_yaxes(title_text="# of Intakes", row=1, col=2)
subplt.update_yaxes(title_text="# of Intakes", row=1, col=1)
st.write(subplt)

#---


# Length of Stay and Age Distribution
st.markdown("#### :blue[Animal Demographic Distributions]")
# Select Box for filter
los_option = st.selectbox(label="Select Animal Type to filter by:",
                          options=("All", "Cat", "Dog", "Other"))
if los_option == "All":
    # LOS Histogram
    los_hist = px.histogram(df, x="datetime_difference", labels={"datetime_difference":"Time Spent in Shelter"})
    # Animal Age Histogram
    aa_hist = px.histogram(df, x="animal_age", labels={"animal_age":"Animal Age (Years)"})
    
else:
    # Filtered Data by selected Animal Type
    df_filter = df[df["animal_type"] == los_option]
    # LOS Histogram
    los_hist = px.histogram(df_filter, x="datetime_difference", 
                            labels={
                                "datetime_difference":"Time Spent in Shelter"
                                })
    # Animal Age Histogram
    aa_hist = px.histogram(df_filter, x="animal_age", labels={"animal_age":"Animal Age (Years)"})

# Assemble Histogram subplots
hist_subplt = make_subplots(rows=1, cols=2, subplot_titles=["Distribution of Time Spent in Shelter", "Distribution of Animal Age"], )
hist_subplt.add_trace(los_hist.data[0], row=1, col=1)
hist_subplt.add_trace(aa_hist.data[0], row=1, col=2)
hist_subplt.update_xaxes(title_text="Time Spent in Shelter (Days)", row=1, col=1)
hist_subplt.update_xaxes(title_text="Animal Age (Years)", row=1, col=2)
hist_subplt.update_yaxes(title_text="Count", row=1, col=2)
hist_subplt.update_yaxes(title_text="Count", row=1, col=1)
st.write(hist_subplt)