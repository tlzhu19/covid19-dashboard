import streamlit as st 
import pandas as pd 
import numpy as np 
import pydeck as pdk 
import altair as alt 
from datetime import datetime, timedelta
import time

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
df = load_data().dropna()

# Load rows of data into the dataframe.
st.header('US Data Preview')
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)

########################################################################################
st.header('New Cases')
########################################################################################

########################################################################################
# Linechart with multiselect
st.subheader('Comparing New Cases Among US States')
subset_data =df

state_name_input = st.multiselect(
'State Name',
df.groupby('state').count().reset_index()['state'].tolist())

# by state name
if len(state_name_input) > 0:
    subset_data = df[df['state'].isin(state_name_input)]

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

########################################################################################
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

########################################################################################
## MAP
st.subheader('New Cases Over Time')

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

# your color-scale
scl = [[0.0, '#ffffff'],[0.2, '#a1d9f7'],[0.4, '#73c7f5'],
       [0.6, '#44a6db'],[0.8, '#1a82ba'],[1.0, '#0b5f8c']] 

data_slider = []
subset_dates = all_dates[60:]
for date in subset_dates:
    df_segmented =  df[(df['date']== date)]

    for col in df_segmented.columns:
        df_segmented[col] = df_segmented[col].astype(str)

    data_each_date = dict(
                        type='choropleth',
                        locations = df_segmented['state'].apply(lambda x: us_state_abbrev.get(x, '')),
                        z=df_segmented['new_cases'].astype(float),
                        locationmode='USA-states',
                        colorscale = scl,
                        colorbar= {'title':'# Cases'})

    data_slider.append(data_each_date)

steps = []
for i in range(len(data_slider)):
    step = dict(method='restyle',
                args=['visible', [False] * len(data_slider)],
                label='{}'.format(subset_dates[i]))
    step['args'][1][i] = True
    steps.append(step)

sliders = [dict(active=0, pad={"t": 1}, steps=steps)]

layout = dict(title ='COVID19 Cases by State', geo=dict(scope='usa',
                       projection={'type': 'albers usa'}),
              sliders=sliders)

fig = dict(data=data_slider, layout=layout)
st.plotly_chart(fig)


########################################################################################
st.header('Total Cases and Total Deaths')
########################################################################################

########################################################################################
st.subheader('Comparing Total Cases Among US States')
subset_data =df

state_name_input_total = st.multiselect(
'State Name - Total Cases',
df.groupby('state').count().reset_index()['state'].tolist())

# by state name
if len(state_name_input_total) > 0:
    subset_data = df[df['state'].isin(state_name_input_total)]

new_cases_graph = alt.Chart(subset_data).transform_filter(
    alt.datum.new_cases > 0  
).mark_line().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('sum(cases):Q',  title='Confirmed Total Cases'),
    color='state',
    tooltip = ['date:T', 'state','sum(cases)']
).properties(
    width=800,
    height=600
).configure_axis(
    labelFontSize=12,
    titleFontSize=20
)

st.altair_chart(new_cases_graph)