# COVID19 Dashboard

## Data used

NYC data:
* https://projects.thecity.nyc/2020_03_covid-19-tracker/
* https://github.com/nychealth/coronavirus-data/blob/master/boro/boroughs-case-hosp-death.csv
* https://github.com/nychealth/coronavirus-data/blob/master/tests.csv

US data:
* https://github.com/nytimes/covid-19-data/

## About
Simple COVID19 dashboard made using [Streamlit](https://docs.streamlit.io/en/stable/getting_started.html) and deployed with [Heroku](https://www.heroku.com/python). Can be viewed on https://covid19-dashboard-tz.herokuapp.com/.

To run app locally, you should have Streamlit installed.
```
>> pip install streamlit
```
Then,
```
>> cd covid19-dashboard
>> streamlit run covid19_data.py
```

Files:
1. covid19_dashboard.ipynb - Python notebook 
2. covid19_data.py - main app file that follows Streamlit workflow
3. Procfile - needed to deploy app, contains commands to run the app
4. requirements.txt - List of Python libraries needed
5. setup.sh - need to deploy app
