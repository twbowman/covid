import requests
import sqlite3
import datetime
import glob
import csv
from datetime import date
from random import randint
from bokeh.plotting import figure, output_file, show, save
from bokeh.layouts import gridplot
from bokeh.models import LinearAxis, Range1d
from bokeh.models import ColumnDataSource, DataTable, DateFormatter, TableColumn


def graph_ranks(state):
    conn = sqlite3.connect('covid.db')
    c = conn.cursor()

    stmt = 'SELECT state,date,popRank,deathRank,deathPer100kRank,testsRank,testsPercentRank FROM ranks WHERE state = ? ORDER BY date'
    c.execute(stmt, (state,))
    data_list = c.fetchall()
    days=list(range(1,len(data_list)+1))
    popRank = []
    deathRank = []
    per100kRank = []
    testsRank = []
    testPercentRank = []
    for data in data_list:
        popRank.append(data[2])
        deathRank.append(data[3])
        per100kRank.append(data[4])
        testsRank.append(data[5])
        testPercentRank.append(data[6])
    plot = figure(title="Ranking for {}".format(state),
                  x_axis_label = 'Days',
                  y_axis_label = 'Ranking',
                  y_range = (55, 1))
    plot.line(days, popRank, legend_label='Population Rank', line_width=2, color = 'red')
    plot.line(days, deathRank, legend_label='Death Rank', line_width=2, color = 'blue')
    plot.line(days, per100kRank, legend_label='Deaths Per 100k Rank', line_width=2, color = 'green')
    plot.line(days, testsRank, legend_label='Tests Rank', line_width=2, color = 'yellow')
    plot.line(days, testPercentRank, legend_label='Test% Rank', line_width=2, color = 'orange')
    plot.legend.location = "bottom_left"
    return(plot)

def graph_hospital(state):
    conn = sqlite3.connect('covid.db')
    c = conn.cursor()

    # Set Min and Max for y1 and y2 col
    y1_stmt = 'SELECT hospitalizedCumulative FROM covidData WHERE state = ? ORDER BY hospitalizedCumulative'
    c.execute(y1_stmt, (state,))
    y1_list = c.fetchall()
    y1_min = y1_list[0][0]
    y1_max = y1_list[len(y1_list)-1][0]

    # get a collolated list for graphings
    stmt = 'SELECT state, date, hospitalizedCumulative FROM covidData WHERE state = ? ORDER BY date'
    c.execute(stmt, (state,))
    data_list = c.fetchall()
    y1_data = []
    for data in data_list:
        y1_data.append(data[2])

    days=list(range(1,len(data_list)+1))
    plot = figure(title="Currently in Hospital in {}".format(state),
                  x_axis_label = 'Days',
                  y_axis_label = 'In Hospital',
                  y_range = (0, y1_max))
    # Right y axis
    plot.line(days, y1_data, legend_label='In Hospital', line_width=2)

    return(plot)


# Graph death and tests
def graph_states(state, g):
    conn = sqlite3.connect('covid.db')
    c = conn.cursor()

    # Set Min and Max for y1 and y2 col
    y1_stmt = 'SELECT {} FROM covidData WHERE state = ? ORDER BY {}'.format(g['y1_col'],g['y1_col'])
    c.execute(y1_stmt, (state,))
    y1_list = c.fetchall()
    y1_min = y1_list[0][0]
    y1_max = y1_list[len(y1_list)-1][0]
    y2_stmt = 'SELECT {} FROM covidData WHERE state = ? ORDER BY {}'.format(g['y2_col'],g['y2_col'])
    c.execute(y2_stmt, (state,))
    y2_list = c.fetchall()
    y2_min = y2_list[0][0]
    y2_max = y2_list[len(y2_list)-1][0]

    # get a collolated list for graphings
    stmt = 'SELECT state, date, {}, {} FROM covidData WHERE state = ? ORDER BY date'.format(g['y1_col'],g['y2_col'])
    c.execute(stmt, (state,))
    data_list = c.fetchall()
    y1_data = []
    y2_data = []
    for data in data_list:
        y1_data.append(data[2])
        y2_data.append(data[3])

    days=list(range(1,len(data_list)+1))
    plot = figure(title=g['title'].format(state),
                  x_axis_label = g['x_axis_label'],
                  y_axis_label = g['y1_axis_label'],
                  y_range = (0, y1_max))
    # Right y axis
    plot.line(days, y1_data, legend_label=g['y1_axis_label'], line_width=2)
    # Left y axis
    plot.extra_y_ranges = { 'y_col2_range': Range1d( y2_min, y2_max * 1.10) }
    plot.add_layout(LinearAxis(y_range_name = 'y_col2_range', axis_label = g['y2_axis_label']), "right")
    plot.line(days, y2_data, legend_label = g['y2_axis_label'], line_width=2, y_range_name='y_col2_range', color = 'red')

    plot.legend.location = "top_left"

    return(plot)

def graph_table():
    output_file("graphs/rank_table.html")

    # get latest date
    stmt = 'SELECT date FROM ranks WHERE state = "NM" ORDER BY date DESC'
    c.execute(stmt, ())
    last_date = c.fetchall()[0][0]

    stmt = 'SELECT state,date,popRank,deathRank,deathPer100kRank,testsRank,testsPercentRank FROM ranks WHERE date = ? ORDER BY popRank'
    c.execute(stmt, (last_date,))
    data_list = c.fetchall()

    state = []
    popRank = []
    deathRank = []
    deathPer100kRank = []
    testsRank = []
    testPercentRank = []
    for data in data_list:
        state.append(data[0])
        popRank.append(data[2])
        deathRank.append(data[3])
        deathPer100kRank.append(data[4])
        testsRank.append(data[5])
        testPercentRank.append(data[6])

    data = dict(
        state=state,
        popRank=popRank,
        deathRank=deathRank,
        deathPer100kRank=deathPer100kRank,
        testsRank=testsRank,
        testPercentRank=testPercentRank)
    source = ColumnDataSource(data)

    columns = [ 
                TableColumn(field="state", title="State"),
                TableColumn(field="popRank", title="Population Rank"),
                TableColumn(field="deathRank", title="Death Rank"),
                TableColumn(field="deathPer100kRank", title="Death per 100K Rank"),
                TableColumn(field="testsRank", title="Tests Rank"),
                TableColumn(field="testPercentRank", title="Test Percent Rank")]
    data_table = DataTable(source=source, columns=columns, width=800, height=480)

    show(data_table)

# Connect to sqlite database
conn = sqlite3.connect('covid.db')
c = conn.cursor()
c.execute('SELECT state FROM population ORDER BY state')
state_list = c.fetchall()

graph_table()
for state in state_list:
    plots = [] 
    output_file("./graphs/covid_in_{}.html".format(state[0]))

    g = {'title' : "Covid deaths and death rate {}",
         'x_axis_label': 'Day',
         'y1_axis_label': 'Deaths per 100k',
         'y1_col': 'deathPer100k',
         'y2_axis_label': 'Deaths',
         'y2_col': 'death'}
    h = {'title' : "Covid tests and test percentage {}",
         'x_axis_label': 'Day',
         'y1_axis_label': 'Test Percentage',
         'y1_col': 'testPercent',
         'y2_axis_label': 'total tests',
         'y2_col': 'totalTestResults'}
    gplots = graph_states(state[0], g)
    hplots = graph_states(state[0], h)
    hoPlots = graph_hospital(state[0])
    rankPlots = graph_ranks(state[0])
    grid = gridplot([gplots, hplots, hoPlots, rankPlots], ncols = 2)
    save(grid)
