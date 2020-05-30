import sqlite3
import requests
import os
import datetime
import threading
from collections import namedtuple
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot
from bokeh.models import LinearAxis, Range1d

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

def graph_states():
    conn = sqlite3.connect('covid.db')
    c = conn.cursor()

    output_file("./graphs/deaths_per_state.html")
    plots = {}

    start_day = datetime.datetime.strptime("20200403", "%Y%m%d").date()
    date = start_day.strftime("%Y%m%d")

    state = 'NM'
    g = {'title' : "Covid deaths and death rate {}",
         'x_axis_label': 'Day',
         'y1_axis_label': 'Deaths per 100k',
         'y1_col': 'deathPer100k',
         'y2_axis_label': 'Deaths',
         'y2_col': 'death'}

    # Set Min and Max for y1 and y2 col
    y1_stmt = 'SELECT {} FROM covidData WHERE state = ? ORDER BY {}'.format(g['y1_col'],g['y1_col'])
    c.execute(y1_stmt, (state,))
    y1_list = c.fetchall()
    y1_min = y1_list[0][0]
    y1_max = y1_list[len(y1_list)-1][0]
    print(y1_min, y1_max)
    y2_stmt = 'SELECT {} FROM covidData WHERE state = ? ORDER BY {}'.format(g['y2_col'],g['y2_col'])
    c.execute(y2_stmt, (state,))
    y2_list = c.fetchall()
    y2_min = y2_list[0][0]
    y2_max = y2_list[len(y2_list)-1][0]
    print(y2_min, y2_max)

    # get a collolated list for graphings
    stmt = 'SELECT state, date, {}, {} FROM covidData WHERE state = ? ORDER BY date'.format(g['y1_col'],g['y2_col'])
    c.execute(stmt, (state,))
    data_list = c.fetchall()
    y1_data = []
    y2_data = []
    for data in data_list:
        y1_data.append(data[2])
        y2_data.append(data[3])

    days=list(range(0,len(data_list)))
    title = "Covid deaths and death rate for {}".format(state)
    plot = figure(title=g['title'].format(state), 
                  x_axis_label = g['x_axis_label'],
                  y_axis_label = g['y1_axis_label'], 
                  y_range = (0, y1_max))
    # Right y axis
    plot.line(days, y1_data, legend_label='deaths per 100k', line_width=2)
    # Left y axis
    plot.extra_y_ranges = { 'y_col2_range': Range1d( y2_min, y2_max * 1.10) }
    plot.add_layout(LinearAxis(y_range_name = 'y_col2_range', axis_label = g['y2_axis_label']), "right")
    plot.line(days, y2_data, legend_label = g['y2_axis_label'], line_width=2, y_range_name='y_col2_range', color = 'red')

    plot.legend.location = "top_left"

    #grid = gridplot(plots)
    #grid = gridplot(list(plots.values()), ncols = 3)
    show(plot)


def collect_data(state,population):
    # Each Thread needs to connect to the database
    conn = sqlite3.connect('covid.db')
    c = conn.cursor()

    placeholder = ", ".join(["?"] * len(columns))
    start_day = datetime.datetime.strptime("20200403", "%Y%m%d").date()
    end_day = datetime.date.today()
    dates_generated = [start_day + datetime.timedelta(days=x) for x in range(0, (end_day-start_day).days)]
    data = []
    for d in dates_generated:
        date = d.strftime("%Y%m%d")
        print("Collecting data for state {} and date {}. Column Length = {}".format(state,date,len(columns)))
        stmt = "https://covidtracking.com/api/v1/states/{}/{}.json".format(state, date)
        response = requests.get(stmt)
        state_covid = response.json()
    
        stmt = "REPLACE INTO `{table}` ({columns}) VALUES ({values});".format(table='covidData', columns=",".join(columns), values=placeholder)
        data.append([state_covid['state'],
                    date,
                    population,
                    state_covid['dataQualityGrade'],
                    state_covid['hospitalizedCumulative'],
                    state_covid.get('hospitalizedCurrently',0),
                    state_covid['inIcuCumulative'],
                    state_covid['onVentilatorCumulative'],
                    state_covid['recovered'],
                    state_covid['death'],
                    (state_covid['death']/population) * 100000,
                    state_covid['hospitalized'],
                    state_covid['totalTestResults'],
                    (state_covid['totalTestResults']/population) * 100])

    with lock:
        print("saving data for {state} for period {start} to  {end}".format(state=state,start=start_day.strftime("%Y%m%d"),end=end_day.strftime("%Y%m%d")))
        c.executemany(stmt, data)
        conn.commit()

def make_ranks():
    print("Sorting and ranking the data per state per day")
    # Create rank table if it doesnt exist
    c.execute("CREATE TABLE IF NOT EXISTS ranks (state text, date text, popRank int, deathRank int, deathPer100kRank int, testsRank int, testsPercentRank int, PRIMARY KEY (state,date))")

    start_day = datetime.datetime.strptime("20200403", "%Y%m%d").date()
    end_day = datetime.date.today()
    dates_generated = [start_day + datetime.timedelta(days=x) for x in range(0, (end_day-start_day).days)]
    ranks = {} 
    for d in dates_generated:
        date = d.strftime("%Y%m%d")
        # Get Sorted list of items we want to rank
        c.execute('SELECT state, population FROM population ORDER BY population DESC')
        pop_list = c.fetchall()
        c.execute('SELECT state, death FROM covidData WHERE date = ? ORDER BY death DESC',(date,))
        death_list = c.fetchall()
        c.execute('SELECT state, deathPer100k FROM covidData WHERE date = ? ORDER BY deathPer100k DESC',(date,))
        per100k_list = c.fetchall()
        c.execute('SELECT state, totalTestResults FROM covidData WHERE date = ? ORDER BY totalTestResults DESC',(date,))
        tests_list = c.fetchall()
        c.execute('SELECT state, testPercent FROM covidData WHERE date = ? ORDER BY testPercent DESC',(date,))
        test_percent = c.fetchall()
        
        rankKey = namedtuple("rankKey", ["state", "date"])
        
        for count, item in enumerate(pop_list):
            state = item[0]
            r = rankKey(state=state, date=date)
            ranks[r] = {'state': state, 'date': date}
            ranks[r]['popRank'] = count + 1
        
        for count, item in enumerate(death_list):
            state = item[0]
            r = rankKey(state=state, date=date)
            ranks[r]['deathRank'] = count + 1
    
        for count, item in enumerate(per100k_list):
            state = item[0]
            r = rankKey(state=state, date=date)
            ranks[r]['per100kRank'] = count + 1
        
        for count, item in enumerate(tests_list):
            state = item[0]
            r = rankKey(state=state, date=date)
            ranks[r]['testsRank'] = count + 1
        
        for count, item in enumerate(test_percent):
            state = item[0]
            r = rankKey(state=state, date=date)
            ranks[r]['testPercentRank'] = count + 1

    rank_list = []
    for rank in ranks:
        entry = [ranks[rank]['state'],
                 ranks[rank]['date'],
                 ranks[rank]['popRank'],
                 ranks[rank]['deathRank'],
                 ranks[rank]['per100kRank'],
                 ranks[rank]['testsRank'],
                 ranks[rank]['testPercentRank']]
        rank_list.append(entry)

    c.executemany('REPLACE INTO ranks VALUES (?,?,?,?,?,?,?)', rank_list)
    conn.commit()


# Connect to sqlite database
conn = sqlite3.connect('covid.db')
c = conn.cursor()

# Create Population table if it doesn't exist
c.execute("CREATE TABLE IF NOT EXISTS population (state text, fullName text, population int, popRank int, PRIMARY KEY (state))")

# Check to see if there is data in the population table
print('Hello')
c.execute('SELECT * FROM population ORDER BY population DESC')
pop_list = c.fetchall()
print(pop_list)
if len(pop_list) == 0:
    # table is empty
    # Collect population data and enter in table. A key from api.census.gov is required
    print("Collecting population data")
    response = requests.get("https://api.census.gov/data/2019/pep/population?get=POP,NAME&for=state:*&key={}".format(os.environ['CENSUS_KEY']))
    states_pop = response.json()

    state_list = []
    for state_pop in states_pop[1:]:
        pop = int(state_pop[0])
        state = us_state_abbrev[state_pop[1]]
        fullName = state_pop[1]
        state_list.append([state, fullName, pop])

    c.executemany('INSERT INTO population (state, fullName, population) VALUES (?,?,?)', state_list)
    conn.commit()

# Data types for covidData table
data_type = ['state text',
             'date text',
             'population int',
             'dataQualityGrade text',
             'hospitalizedCurrently int',
             'hospitalizedCumulative int',
             'inIcuCumulative int',
             'onVentilatorCumulative int',
             'recovered int',
             'death int',
             'deathPer100k float',
             'hospitalized int',
             'totalTestResults int',
             'testPercent float']
columns = []
for entry in data_type:
    columns.append(entry.split()[0])
print(len(columns), len(data_type))

stmt = "CREATE TABLE IF NOT EXISTS covidData ({columns}, PRIMARY KEY (state, date))".format(columns=",".join(data_type))
c.execute(stmt)


c.execute('SELECT * FROM population ORDER BY population DESC')
pop_list = c.fetchall()

threads = {}
lock = threading.Lock()
for pop in pop_list:
    state = pop[0]
    # Get Population for the state
    c.execute('SELECT population FROM population where state = ?',(state,))
    rows = c.fetchall()
    population = rows[0][0]
    threads[state] = threading.Thread( target=collect_data, args=(state, population))
    print("starting thread for {}".format(state))
    threads[state].start()

# Join Threads
for state in threads:
    print("joining thread for {}".format(state))
    threads[state].join()

make_ranks()
