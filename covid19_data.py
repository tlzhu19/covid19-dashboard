import streamlit as st 
import pandas as pd 
import numpy as np 
import pydeck as pdk 
import altair as alt 
from datetime import datetime


st.title('COVID19 Dashboard - US')

# Load Data
DATA_URL = ('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
@st.cache
def load_data():
    data = pd.read_csv(DATA_URL)
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
    data = data.sort_values(['state', 'date'])
    data['new_cases'] = data.groupby('state')['cases'].diff()
    return data
df = load_data()

# Load rows of data into the dataframe.
st.header('US Data Preview')
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)

st.header('New Cases')

# Linechart with multiselect
st.subheader('Comparing New Cases Among US States')
subset_data =df

state_name_input = st.multiselect(
'State Name',
df.groupby('state').count().reset_index()['state'].tolist())

# by state name
if len(state_name_input) > 0:
    subset_data = df[df['state'].isin(state_name_input)]

# st.subheader('Comparision of New Cases')

new_cases_graph = alt.Chart(subset_data).transform_filter(
    alt.datum.new_cases > 0  
).mark_line().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('sum(new_cases):Q',  title='Confirmed New Cases'),
    color='state',
    tooltip = ['date:T', 'state','sum(new_cases)']
).properties(
    width=800,
    height=600
).configure_axis(
    labelFontSize=12,
    titleFontSize=20
)

st.altair_chart(new_cases_graph)


# Top New Number of Cases
st.subheader('View States with Highest Number of New Cases')
all_dates = sorted(df.date.unique().tolist())
date_option = st.selectbox(
	'Pick Date',
	sorted(df.date.unique().tolist()),
	index=len(all_dates)-1
)
n = st.slider('Top N States New Cases', 0, 50, value=5)
top_n_df = df[df['date']==date_option].sort_values('new_cases', ascending=False).head(n)
st.write(top_n_df)

top_n_bar_chart = top_n_df.set_index('state')
st.bar_chart(top_n_bar_chart[['new_cases']])


st.header('Total Cases and Total Deaths')
