import requests
import datetime
import os
from bokeh.plotting import figure, output_file, show


output_file("states.html")
p = figure(title="Deaths per 100k", x_axis_label='Date', y_axis_label='Deaths per 100k')

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

joined= {}

# Collect census Data, A key from api.census.gov is required
response = requests.get("https://api.census.gov/data/2019/pep/population?get=POP,NAME&for=state:*&key={}".format(os.environ['CENSUS_KEY']))
states_pop = response.json()
for state_pop in states_pop[1:]:
    pop = int(state_pop[0])
    state = us_state_abbrev[state_pop[1]]

    file = open("data/covid-{}".format(state),'w')
    file.write('state,  date, deaths, deaths per 100k, total tested, tested %\n')
    
    start = datetime.datetime.strptime("20200403", "%Y%m%d")
    end = datetime.datetime.today()
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]

    deaths_per_capita =[]
    for date in date_generated:
        response = requests.get("https://covidtracking.com/api/v1/states/{}/{}.json".format(state, date.strftime("%Y%m%d")))
        state_covid = response.json()
        totalTestResults = int(state_covid['totalTestResults'])
        test_per_capita = (totalTestResults/pop) * 100
        death = int(state_covid['death'])
        death_per_capita = (death/pop) * 100000
        deaths_per_capita.append(death_per_capita)
        file.write("{}, {}, {}, {}, {}, {}\n".format(state, 
                                              date, 
                                              death, 
                                              death_per_capita, 
                                              totalTestResults, 
                                              test_per_capita))
    p.line(date_generated, deaths_per_capita, legend_label=state, line_width=2)
    file.close()


show(p)
