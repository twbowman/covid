import requests

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

# Collect census Data
response = requests.get("https://api.census.gov/data/2019/pep/population?get=POP,NAME&for=state:*&key={}".format(os.environ['CENSUS_KEY']))
states_pop = response.json()
for state_pop in states_pop[1:]:
    joined[us_state_abbrev[state_pop[1]]] = {'pop': int(state_pop[0]), 'name': state_pop[1] }

# Collect covid data
response = requests.get("https://covidtracking.com/api/v1/states/current.json")
states_covid = response.json()
for state_covid in states_covid:
    if state_covid['state'] in joined:
        joined[state_covid['state']]['totalTestResults'] = int(state_covid['totalTestResults'] )
        joined[state_covid['state']]['test_per_capita'] = (joined[state_covid['state']]['totalTestResults']/joined[state_covid['state']]['pop']) * 100
        joined[state_covid['state']]['death'] = int(state_covid['death'] )
        #joined[state_covid['state']]['death_per_capita'] = (joined[state_covid['state']]['death']/joined[state_covid['state']]['pop']) * 100,000
        joined[state_covid['state']]['death_per_capita'] = (joined[state_covid['state']]['death']/joined[state_covid['state']]['pop']) * 100000

# Sort based on population
pop_sorted = sorted(joined.items(), reverse=True,  key=lambda x: x[1]['pop'])
death_sorted = sorted(joined.items(), reverse=True,  key=lambda x: x[1]['death'])
test_sorted = sorted(joined.items(), reverse=True,  key=lambda x: x[1]['test_per_capita'])
death_per_capita_sorted = sorted(joined.items(), reverse=True,  key=lambda x: x[1]['death_per_capita'])
 
for count, item in enumerate(pop_sorted, start=1):
    joined[item[0]]['pop_rank'] = count
for count, item in enumerate(death_sorted, start=1):
    joined[item[0]]['death_rank'] = count
for count, item in enumerate(test_sorted, start=1):
    joined[item[0]]['tests_rank'] = count
for count, item in enumerate(death_per_capita_sorted, start=1):
    joined[item[0]]['death_per_capita_rank'] = count


print ('state abrev, state,  population, pop rank, deaths, rank per deaths, deaths per 100k, death per 100k rank, total tested, tested %, test% rank')
for k in pop_sorted:
    key = k[0]
    print("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".
                                   format(key,
                                          joined[key]['name'],
                                          joined[key]['pop'], 
                                          joined[key]['pop_rank'],
                                          joined[key]['death'],
                                          joined[key]['death_rank'],
                                          joined[key]['death_per_capita'],
                                          joined[key]['death_per_capita_rank'],
                                          joined[key]['totalTestResults'],
                                          joined[key]['test_per_capita'],
                                          joined[key]['tests_rank']))
