import requests
from datetime import datetime
import glob
import csv
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot
from bokeh.models import LinearAxis, Range1d

def deaths_per_state():
    data_files = glob.glob('./data/covid-*')
    data_files.sort()

    output_file("./graphs/deaths_per_state.html")
    plots = {}
    for data_file in data_files:
        with open(data_file) as csvfile:
            deaths_pc_list = []
            deaths_list = []
            dates = []
            deaths_max = 0
            deaths_pc_max = 0
            creader = csv.reader(csvfile)
            list_iterator = iter(creader)
            next(list_iterator)
            for row in list_iterator:
                state=row[0]
                dates.append(row[1])
                deaths = float(row[2])
                deaths_list.append(deaths)
                if deaths > deaths_max: 
                    deaths_max = deaths 
                deaths_pc = float(row[3])
                deaths_pc_list.append(deaths_pc)
                if deaths_pc > deaths_pc_max: 
                    deaths_pc_max = deaths_pc 
    
            days=list(range(0,len(deaths_list)))
            title = "Covid deaths and death rate for {}".format(state)
            plots[state] = figure(title=title, x_axis_label='Day', y_axis_label='Deaths per 100k', y_range=(0,deaths_pc_max))
            # Right y axis
            plots[state].line(days, deaths_pc_list, legend_label='deaths per 100k', line_width=2)
            # Left y axis
            plots[state].extra_y_ranges = { 'y_col2_range': Range1d(0, deaths_max * 1.10) }
            plots[state].add_layout(LinearAxis(y_range_name = 'y_col2_range', axis_label='Deaths'), "right")
            plots[state].line(days, deaths_list, legend_label='Deaths', line_width=2, y_range_name='y_col2_range', color = 'red')
    
            plots[state].legend.location = "top_left"
        
    #grid = gridplot(plots)
    grid = gridplot(list(plots.values()), ncols = 3)
    show(grid)

def tests_per_state():
    data_files = glob.glob('./data/covid-*')
    data_files.sort()

    output_file("./graphs/tests_per_state.html")
    plots = {}
    for data_file in data_files:
        with open(data_file) as csvfile:
            tests_per_capita = []
            tests = []
            dates = []
            tests_max = 0
            tests_per_capita_max = 0
            creader = csv.reader(csvfile)
            list_iterator = iter(creader)
            next(list_iterator)
            for row in list_iterator:
                state=row[0]
                dates.append(row[1])
                test = float(row[4])
                tests.append(test)
                if test > tests_max: 
                    tests_max = test 
                test_per_capita = float(row[5])
                tests_per_capita.append(test_per_capita)
                if test_per_capita > tests_per_capita_max: 
                    tests_per_capita_max = test_per_capita 
    
            days=list(range(0,len(tests)))
            title = "Covid tests and test % for {}".format(state)
            plots[state] = figure(title=title, x_axis_label='Day', y_axis_label='% Tested', y_range=(0,tests_per_capita_max))
            # Right y axis
            plots[state].line(days, tests_per_capita, legend_label='% Tested', line_width=2)
            # Left y axis
            plots[state].extra_y_ranges = { 'y_col2_range': Range1d(0, tests_max * 1.10) }
            plots[state].add_layout(LinearAxis(y_range_name = 'y_col2_range', axis_label='Tested'), "right")
            plots[state].line(days, tests, legend_label='Tested', line_width=2, y_range_name='y_col2_range', color = 'red')
    
            plots[state].legend.location = "top_left"
        
    #grid = gridplot(plots)
    grid = gridplot(list(plots.values()), ncols = 3)
    show(grid)

deaths_per_state()
tests_per_state()
