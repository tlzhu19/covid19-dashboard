import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from datetime import date, datetime, timedelta
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'COVID19 Dashboard'
server = app.server


class NYCData:
    def __init__(self):
        self.nyc_boro_url = 'https://raw.githubusercontent.com/nychealth/coronavirus-data/master/boro/boroughs-case-hosp-death.csv'
        self.nyc_tests_url = 'https://raw.githubusercontent.com/nychealth/coronavirus-data/master/tests.csv'
        self.nyc_boro_df = pd.read_csv(self.nyc_boro_url)
        self.nyc_tests_df = pd.read_csv(self.nyc_tests_url)

        self.borough_to_fips = {'Bronx': '36005',
                                'Brooklyn': '36047',
                                'Queens': '36081',
                                'Manhattan': '36061',
                                'Staten Island': '36085'}

        self.cases_df = self.clean_nyc_data_by_metric('CASE_COUNT')
        self.hospitalized_df = self.clean_nyc_data_by_metric('HOSPITALIZED_COUNT')
        self.deaths_df = self.clean_nyc_data_by_metric('DEATH_COUNT')

    def clean_nyc_data_by_metric(self, metric):
        column_filter = self.nyc_boro_df.columns.to_series().str.contains(metric)
        column_filter.DATE_OF_INTEREST = True
        columns = self.nyc_boro_df.columns[column_filter]
        nyc_cases = self.nyc_boro_df[columns]
        nyc_cases.columns = ['date', 'Brooklyn', 'Bronx', 'Manhattan', 'Queens', 'Staten Island']

        nyc_cases_tidy = pd.melt(nyc_cases, ["date"], var_name="county", value_name="new_cases")
        nyc_cases_tidy['state'] = ['New York' for i in range(len(nyc_cases_tidy))]
        nyc_cases_tidy['fips'] = [self.borough_to_fips[borough] for borough in nyc_cases_tidy['county'].values]
        nyc_cases_tidy['date'] = pd.to_datetime(nyc_cases_tidy['date']).dt.strftime('%Y-%m-%d')
        return nyc_cases_tidy


class Counties:
    def __init__(self):
        counties_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
        counties_df = pd.read_csv(counties_url, dtype=str)

        types_dict = {'cases': int, 'deaths': int}
        for col, col_type in types_dict.items():
            counties_df[col] = counties_df[col].astype(col_type)

        counties_df['date'] = pd.to_datetime(counties_df['date']).dt.strftime('%Y-%m-%d')
        counties_df['new_cases'] = counties_df.sort_values(['state', 'county', 'date']).groupby('state')['cases'].diff()

        self.df = counties_df

class States:
    def __init__(self):
        states_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
        states_df = pd.read_csv(states_url)

        types_dict = {'cases': int, 'deaths': int}
        for col, col_type in types_dict.items():
            states_df[col] = states_df[col].astype(col_type)

        states_df['date'] = pd.to_datetime(states_df['date']).dt.strftime('%Y-%m-%d')
        states_df['new_cases'] = states_df.sort_values(['state', 'date']).groupby('state')['cases'].diff()

        self.df = states_df



# FIGURES
## NYC
YESTERDAY = (date.today() - timedelta(2)).strftime("%Y-%m-%d")
nyc = NYCData()
nyc_test = nyc.cases_df[nyc.cases_df['date'] == YESTERDAY]
fig = px.choropleth(nyc_test,
                    geojson=counties,
                    locations='fips',
                    color='new_cases',
                    color_continuous_scale="Blues",
                    range_color=(0, max(nyc_test["new_cases"])),
                    scope="usa",
                    hover_name="county",
                    hover_data=["date", "new_cases"],
                    labels={'new_cases':'new cases'}
                   )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend_orientation="h")


fig_nyc = px.line(nyc.cases_df, x="date", y="new_cases", color='county',
                  labels={'date': 'Date', 'new_cases': 'New Cases', 'county': 'Borough'})

fig_nyc_hosp = px.line(nyc.hospitalized_df, x="date", y="new_cases", color='county',
                  labels={'date': 'Date', 'new_cases': 'Hospitalizations', 'county': 'Borough'})

fig_nyc_deaths = px.line(nyc.deaths_df, x="date", y="new_cases", color='county',
                  labels={'date': 'Date', 'new_cases': 'Deaths', 'county': 'Borough'})

nyc_dates = [d for d in nyc.cases_df.date.unique()]


## NJ
us_counties = Counties()
nj_test = us_counties.df[(us_counties.df.state=='New Jersey') & (us_counties.df.date==YESTERDAY)]
fig_nj = px.choropleth(nj_test,
                    geojson=counties,
                    locations='fips',
                    color='new_cases',
                    color_continuous_scale="Blues",
                    range_color=(0, max(nj_test["new_cases"])),
                    scope="usa",
                    hover_name="county",
                    hover_data=["date", "new_cases"],
                    labels={'new_cases':'new cases'}
                   )
fig_nj.update_geos(fitbounds="locations", visible=False)
fig_nj.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend_orientation="h")

nj_df = us_counties.df[(us_counties.df.state=='New Jersey') & (us_counties.df.new_cases >= 0) & (us_counties.df.county != 'Unknown')]
fig_nj_line = px.line(nj_df, x="date", y="new_cases", color='county',
                      labels={'date': 'Date', 'new_cases': 'New Cases', 'county': 'County'})


## States
states = States()
n = 5
top_n_new = states.df[states.df['date']==YESTERDAY].sort_values('new_cases', ascending=False).head(n)
top_n_total = states.df[states.df['date']==YESTERDAY].sort_values('cases', ascending=False).head(n)
top_n_deaths = states.df[states.df['date']==YESTERDAY].sort_values('deaths', ascending=False).head(n)


# LAYOUT
app.layout = html.Div(children=[

    html.Div(
        [
            html.Div(
                [
                    html.H1(children='US COVID19 Dashboard'),
                ],
            ),
            html.Div(
                [
                    html.H3(children='US States'),
                    dbc.Row(
                        [
                            dbc.Col([
                                dbc.CardHeader("New Cases"),
                                dbc.Card(
                                    dbc.Table.from_dataframe(top_n_new[['state', 'new_cases']], striped=True, hover=True)
                                )
                            ]),
                            dbc.Col([
                                dbc.CardHeader("Total Cases"),
                                dbc.Card(
                                    dbc.Table.from_dataframe(top_n_total[['state', 'cases']], striped=True, hover=True)
                                )
                            ]),
                            dbc.Col([
                                dbc.CardHeader("Total Deaths"),
                                dbc.Card(
                                    dbc.Table.from_dataframe(top_n_total[['state', 'deaths']], striped=True, hover=True)
                                )
                            ]),
                        ],
                    )
                ],
            ),
            html.Div(
                [
                    html.H3(children='New York City'),
                    dbc.Row(
                        [
                            dbc.Col([
                                dbc.CardHeader("New Cases"),
                                dbc.Card(
                                    [
                                        dcc.DatePickerSingle(
                                            id='date-ny',
                                            min_date_allowed=nyc_dates[0],
                                            max_date_allowed=nyc_dates[-1],
                                            initial_visible_month=YESTERDAY,
                                            date=YESTERDAY
                                        ),
                                        dcc.Loading(
                                            dcc.Graph(id='map-ny', figure=fig)
                                        )
                                    ]
                                )
                            ]),
                            dbc.Col([
                                dbc.CardHeader("New Cases Over Time"),
                                dbc.Card(
                                    [
                                        dcc.Dropdown(
                                            options=[
                                                {'label': 'Brooklyn', 'value': 'Brooklyn'},
                                                {'label': 'Bronx', 'value': 'Bronx'},
                                                {'label': 'Manhattan', 'value': 'Manhattan'},
                                                {'label': 'Queens', 'value': 'Queens'},
                                                {'label': 'Staten Island', 'value': 'Staten Island'},
                                            ],
                                            value=['Brooklyn'],
                                            multi=True
                                        ),
                                        dcc.Loading(
                                            dcc.Graph(figure=fig_nyc)
                                        )
                                    ]
                                )
                            ]),
                        ],
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.CardHeader("Hospitalized"),
                                    dbc.Card(
                                        dcc.Loading(
                                            dcc.Graph(figure=fig_nyc_hosp)
                                        )
                                    )
                                ]
                            ),
                            dbc.Col(
                                [
                                    dbc.CardHeader("Deaths"),
                                    dbc.Card(
                                        dcc.Loading(
                                            dcc.Graph(figure=fig_nyc_deaths)
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                ],
            ),
            html.Div(
                [
                    html.H3('New Jersey Counties', id='header-state'),
                    dcc.Dropdown(
                                    id='value-state',
                                    options=[{'label': s, 'value': s} for s in states.df.state.unique()],
                                    value='New Jersey',
                                    clearable=False
                    ), 
                    dbc.Row(
                        [
                            dbc.Col([
                                dbc.CardHeader("New Cases"),
                                dbc.Card(
                                    [
                                        dcc.DatePickerSingle(
                                            id='date-state',
                                            min_date_allowed=nyc_dates[0],
                                            max_date_allowed=nyc_dates[-1],
                                            initial_visible_month=YESTERDAY,
                                            date=YESTERDAY
                                        ),
                                        dcc.Loading(
                                            dcc.Graph(figure=fig_nj, id='map-state')
                                        )
                                    ]
                                )
                            ]),
                            dbc.Col([
                                dbc.CardHeader("New Cases Over Time"),
                                dbc.Card(
                                    [
                                        dcc.Dropdown(
                                                options=[{'label': c, 'value': c} for c in us_counties.df[(us_counties.df.state=='New Jersey')].county.unique()],
                                                value='Somerset',
                                                multi=True
                                        ),
                                        dcc.Loading(
                                            dcc.Graph(figure=fig_nj_line, id='line-state')
                                        )
                                    ]
                                )
                            ])
                        ]
                    )
                ]
            ),
            html.Footer(
                [
                    dcc.Markdown('© 2020 [Github](https://github.com/tlzhu19/covid19-dashboard) | [US Data](https://github.com/nytimes/covid-19-data/) | [NYC Data] (https://github.com/nychealth/coronavirus-data/)'),
                ]
            )
        ],
        style={'margin': '50px'}
    ),
    
])


@app.callback(
    dash.dependencies.Output('map-ny', 'figure'),
    [dash.dependencies.Input('date-ny', 'date')]
)
def update_map_ny(value):
    nyc_test = nyc.cases_df[nyc.cases_df['date'] == value]
    fig = px.choropleth(nyc_test,
                        geojson=counties,
                        locations='fips',
                        color='new_cases',
                        color_continuous_scale="Blues",
                        range_color=(0, max(nyc_test["new_cases"])),
                        scope="usa",
                        hover_name="county",
                        hover_data=["date", "new_cases"],
                        labels={'new_cases':'new cases'}
                       )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend_orientation="h")
    return fig


@app.callback(
    [
        dash.dependencies.Output('map-state', 'figure'),
        dash.dependencies.Output('line-state', 'figure'),
        dash.dependencies.Output('header-state', 'children')
    ],
    [
        dash.dependencies.Input('value-state', 'value'), 
        dash.dependencies.Input('date-state', 'date')
    ]
)
def update_map_state(state_value, input_date):
    # Map
    nj_test = us_counties.df[(us_counties.df.state==state_value) & (us_counties.df.date==input_date)]
    fig_nj = px.choropleth(nj_test,
                        geojson=counties,
                        locations='fips',
                        color='new_cases',
                        color_continuous_scale="Blues",
                        range_color=(0, max(nj_test["new_cases"])),
                        scope="usa",
                        hover_name="county",
                        hover_data=["date", "new_cases"],
                        labels={'new_cases':'new cases'}
                       )
    fig_nj.update_geos(fitbounds="locations", visible=False)
    fig_nj.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend_orientation="h")

    # Line chart
    nj_df = us_counties.df[(us_counties.df.state==state_value) & (us_counties.df.new_cases >= 0) & (us_counties.df.county != 'Unknown')]
    fig_nj_line = px.line(nj_df, x="date", y="new_cases", color='county',
                          labels={'date': 'Date', 'new_cases': 'New Cases', 'county': 'County'})
    return fig_nj, fig_nj_line, '{} Counties'.format(state_value)


if __name__ == '__main__':
    app.run_server(debug=True)  