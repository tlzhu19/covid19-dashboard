# COVID19 Dashboard

## Data used

NYC data:
* https://projects.thecity.nyc/2020_03_covid-19-tracker/
* https://github.com/nychealth/coronavirus-data
  * https://github.com/nychealth/coronavirus-data/blob/master/trends/data-by-day.csv

US data:
* https://github.com/nytimes/covid-19-data/

## About
COVID19 dashboard made using [Dash](https://plotly.com/dash/) and deployed with [Heroku](https://www.heroku.com/python). Can be viewed on https://covid19-dashboard-tz.herokuapp.com/.

To run app locally, you should have Dash installed.
```
>> pip install dash
```
Then,
```
>> cd covid19-dashboard
>> python covid19_dash.py
```

Files:
1. covid19_dashboard.ipynb - Python notebook 
2. covid19_dash.py - main app file that follows Dash workflow
3. Procfile - needed to deploy app, contains commands to run the app
4. requirements.txt - List of Python libraries needed

### Website Preview
Can be viewed on https://covid19-dashboard-tz.herokuapp.com/.
Three sections:
1. Overall USA data
2. NYC data - new cases, deaths, hospilazations
3. County level data - can change the state, the default is NJ

![USA overall data](https://github.com/tlzhu19/covid19-dashboard/blob/master/images/image_1.png)
![NYC data](https://github.com/tlzhu19/covid19-dashboard/blob/master/images/image_2.png)
![County data](https://github.com/tlzhu19/covid19-dashboard/blob/master/images/image_3.png)
