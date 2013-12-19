'''
Created on Apr 29, 2013

@author: desmond cai

'''

'''
This module contains global constants and module level methods in the SCE model.

'''

import itertools
import bisect

""" The following two dict objects store the parameter dictionary for each agent for each 
    time step i.e. when Agent.step_forward method is called """
    
dict_customer_log = {}
dict_utility_log = {}

print 

""" The following constants are for converting between units of time """
NUMBER_OF_MONTHS_IN_ONE_YEAR = 12
NUMBER_OF_DAYS_IN_ONE_YEAR = 365
NUMBER_OF_HOURS_IN_ONE_YEAR = 24*365
NUMBER_OF_MINUTES_IN_ONE_YEAR = 60*24*365
NUMBER_OF_SECONDS_IN_ONE_YEAR = 60*60*24*365
NUMBER_OF_DAYS_IN_EACH_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
NUMBER_OF_HOURS_IN_EACH_MONTH = [24 * x for x in NUMBER_OF_DAYS_IN_EACH_MONTH]
NUMBER_OF_MINUTES_IN_EACH_MONTH = [60 * x for x in NUMBER_OF_HOURS_IN_EACH_MONTH]
NUMBER_OF_SECONDS_IN_EACH_MONTH = [60 * x for x in NUMBER_OF_MINUTES_IN_EACH_MONTH]
FIRST_DAY_OF_EACH_MONTH = [sum(NUMBER_OF_DAYS_IN_EACH_MONTH[0:i]) for i in range(0,13)]
FIRST_HOUR_OF_EACH_MONTH = [sum(NUMBER_OF_HOURS_IN_EACH_MONTH[0:i]) for i in range(0,13)]
FIRST_MINUTE_OF_EACH_MONTH = [sum(NUMBER_OF_MINUTES_IN_EACH_MONTH[0:i]) for i in range(0,13)]
FIRST_SECOND_OF_EACH_MONTH = [sum(NUMBER_OF_SECONDS_IN_EACH_MONTH[0:i]) for i in range(0,13)]
WINTER_MONTHS = [0, 1, 2, 3, 4, 5, 10, 11]
SUMMER_MONTHS = [5, 6, 7, 8]
NUMBER_OF_DAYS_IN_SUMMER = sum(NUMBER_OF_DAYS_IN_EACH_MONTH[x] for x in SUMMER_MONTHS)
NUMBER_OF_DAYS_IN_WINTER = sum(NUMBER_OF_DAYS_IN_EACH_MONTH[x] for x in WINTER_MONTHS)
FIRST_DAY_OF_SUMMER = FIRST_DAY_OF_EACH_MONTH[5]
FIRST_HOUR_OF_SUMMER = FIRST_HOUR_OF_EACH_MONTH[5]
FIRST_MINUTE_OF_SUMMER = FIRST_MINUTE_OF_EACH_MONTH[5]
FIRST_SECOND_OF_SUMMER = FIRST_SECOND_OF_EACH_MONTH[5]
FIRST_DAY_OF_WINTER = FIRST_DAY_OF_EACH_MONTH[9]
FIRST_HOUR_OF_WINTER = FIRST_HOUR_OF_EACH_MONTH[9]
FIRST_MINUTE_OF_WINTER = FIRST_MINUTE_OF_EACH_MONTH[9]
FIRST_SECOND_OF_WINTER = FIRST_SECOND_OF_EACH_MONTH[9]

""" This method returns the year that contains the given time """
def calculate_year(time):
    return time // NUMBER_OF_SECONDS_IN_ONE_YEAR

""" This method returns the month that contains the given time """
def calculate_month(time):
    (year, time_of_the_year) = divmod(time, NUMBER_OF_SECONDS_IN_ONE_YEAR)
    return year * NUMBER_OF_MONTHS_IN_ONE_YEAR + bisect.bisect_right(FIRST_SECOND_OF_EACH_MONTH, time_of_the_year) - 1

""" This method normalizes the given month by the number of months in a year """
def calculate_month_of_year_from_month(month):
    return month % NUMBER_OF_MONTHS_IN_ONE_YEAR

""" This method returns the first second of the given month """
def calculate_time_from_month(month):
    (year, month_of_the_year) = divmod(month, NUMBER_OF_MONTHS_IN_ONE_YEAR)
    return year * NUMBER_OF_SECONDS_IN_ONE_YEAR + FIRST_SECOND_OF_EACH_MONTH[month_of_the_year]

""" The following lists specify the ticks on the time axis and auxiliary variables derived from the tick values """
TICK_VALUES = []            # Entry i in this list is the value (in seconds) of the i-th tick on the time axis
TICK_INTERVALS = []         # Entry i in this list is the interval between the i-th tick and the (i+1)-th tick
TICK_VALUES_MONTH = []      # Entry i in this list is the number of the month that contains the i-th tick
FIRST_INDEX_OF_MONTH = []   # Entry i in this list is the index of the first tick that is contained in the i-th month
FIRST_INDEX_OF_YEAR = []    # Entry i in this list is the index of the first tick that is contained in the i-th year

""" The following constants are for specifying the sample interval in set_time_axis() """
SAMPLE_EVERY_MONTH = 1

"""
This method defines the tick values and should be called once 
at the start of the simulation setup.  The sample interval must 
be one of the constants defined above, e.g. SAMPLE_EVERY_MONTH, etc.
Regardless of the sample interval, TICK_VALUES must always contain 
the first second of every month.
"""
def set_time_axis(sample_interval, sample_length_in_years):
    global TICK_VALUES, TICK_INTERVALS, TICK_VALUES_MONTH, FIRST_INDEX_OF_MONTH, FIRST_INDEX_OF_YEAR    
    TICK_VALUES = []
    TICK_INTERVALS = []
    FIRST_INDEX_OF_MONTH = []
    FIRST_INDEX_OF_YEAR = []
    if sample_interval == SAMPLE_EVERY_MONTH:
        for y in range(0, sample_length_in_years):
            TICK_VALUES.extend([s + y * NUMBER_OF_SECONDS_IN_ONE_YEAR for s in FIRST_SECOND_OF_EACH_MONTH[0:12]])
        TICK_VALUES.append(FIRST_SECOND_OF_EACH_MONTH[12] + (sample_length_in_years - 1) * NUMBER_OF_SECONDS_IN_ONE_YEAR)
    TICK_VALUES_MONTH = range(0, sample_length_in_years * 12 + 1)
    i1, i2 = itertools.tee(TICK_VALUES)
    i2.next()
    for t in itertools.izip(i1,i2):
        TICK_INTERVALS.append(t[1]-t[0])
    last_month = calculate_month(TICK_VALUES[-2]) + 1
    last_year = calculate_year(TICK_VALUES[-2]) + 1
    FIRST_INDEX_OF_MONTH = [None] * last_month
    FIRST_INDEX_OF_YEAR = [None] * last_year
    i1 = reversed(TICK_VALUES)
    i1.next()
    index = len(TICK_VALUES) - 1
    for t in i1:
        index -= 1
        FIRST_INDEX_OF_MONTH[calculate_month(t)] = index
        FIRST_INDEX_OF_YEAR[calculate_year(t)] = index

""" This method returns the largest value i such that TICK_VALUES[i] <= time """
def get_index_at_time(time):
    return bisect.bisect_right(TICK_VALUES,time) - 1

""" This method returns 1 if x >= 0 and 0 otherwise """
def sign(x):
    if x >= 0:
        return 1
    else:
        return -1