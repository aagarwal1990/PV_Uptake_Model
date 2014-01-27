'''
Created on Apr 29, 2013

@author: desmond cai

'''

'''
This module contains classes that define the non-agent objects in the SCE model

'''

import time
import sce_settings
import bisect
import itertools
import copy
import logging
import logging.config
import yaml

class Trace(object):
    """
    A class for representing trace data.
    Trace data is represented using a list of values and the index of the time tick at which this trace starts.
    
    Attributes
    ----------
    list_of_values
    index_of_begin_tick
    
    """
    
    def __init__(self, list_of_values, index_of_starting_time):
        self.list_of_values = list_of_values
        self.index_of_starting_time = index_of_starting_time
    
    def set_list_of_values(self, list_of_values):
        self.list_of_values = list_of_values
    
    def set_index_of_starting_time(self, index_of_starting_time):
        self.index_of_starting_time = index_of_starting_time
                
    def set_starting_time(self, starting_time):
        self.index_of_starting_time = sce_settings.get_index_at_time(starting_time)
    
    def get_list_of_values(self):
        return self.list_of_values
        
    def get_list_of_times(self):
        return sce_settings.TICK_VALUES[self.index_of_starting_time:(self.index_of_starting_time + len(self.list_of_values))]
    
    def get_index_of_starting_time(self):
        return self.index_of_starting_time

    def get_start_time(self):
        return sce_settings.TICK_VALUES[self.index_of_starting_time]
    
    def get_end_time(self):
        return sce_settings.TICK_VALUES[self.index_of_starting_time + len(self.list_of_values)]
    
    def get_start_month(self):
        return sce_settings.TICK_VALUES_MONTH[self.index_of_starting_time]
    
    def get_end_month(self):
        return sce_settings.TICK_VALUES_MONTH[self.index_of_starting_time + len(self.list_of_values)]
    
    def get_value_at_time(self, time):
        return self.list_of_values[sce_settings.get_index_at_time(time) - self.index_of_starting_time]
    
    def get_value_at_time_index(self, time_index):
        return self.list_of_values[time_index - self.index_of_starting_time]
            
    def get_value_at_month(self, month):
        return self.list_of_values[sce_settings.FIRST_INDEX_OF_MONTH[month] - self.index_of_starting_time]

    def get_integral(self):
        return sum([x * y for (x,y) in itertools.izip(self.list_of_values,sce_settings.TICK_INTERVALS[self.index_of_starting_time:(self.index_of_starting_time+len(self.list_of_values))])])

    def get_integral_over_time(self, start_time, end_time):
        total = 0
        i1 = sce_settings.get_index_at_time(start_time)
        i2 = sce_settings.get_index_at_time(end_time)
        if i1 == i2:
            total = (end_time - start_time) * self.list_of_values[i1-self.index_of_starting_time]
        else:
            total = (sce_settings.TICK_VALUES[i1+1] - start_time) * self.list_of_values[i1-self.index_of_starting_time]
            for (x,y) in zip(sce_settings.TICK_INTERVALS[(i1+1):(i2-1)],self.list_of_values[(i1+1-self.index_of_starting_time):(i2-1-self.index_of_starting_time)]):
                total += (x*y)
            if i2 > i1+1:
                total += (end_time - sce_settings.TICK_VALUES[i2-1]) * self.list_of_values[i2-1-self.index_of_starting_time]
        return total
        
    def get_integral_over_month(self, month):
        i1 = sce_settings.FIRST_INDEX_OF_MONTH[month]
        i2 = sce_settings.FIRST_INDEX_OF_MONTH[month + 1]
        return sum([x * y for (x,y) in itertools.izip(self.list_of_values[(i1-self.index_of_starting_time):(i2 - self.index_of_starting_time)],sce_settings.TICK_INTERVALS[i1:i2])])
    
    def get_integral_over_time_index(self, index_of_start_time, index_of_end_time):
        total = 0
        for (x,y) in zip(sce_settings.TICK_INTERVALS[index_of_start_time:index_of_end_time],self.list_of_values[(index_of_start_time-self.index_of_starting_time):(index_of_end_time-self.index_of_starting_time)]):
            total += (x*y)
        return total
    
    def get_peak_over_time_index(self, index_of_start_time, index_of_end_time):
        peak = 0
        for x in self.list_of_values[(index_of_start_time-self.index_of_starting_time):(index_of_end_time-self.index_of_starting_time)]:
            if x > peak:
                peak = x
        return peak
    
    def get_trace_over_time(self, start_time, end_time):
        i1 = sce_settings.get_index_at_time(start_time)
        i2 = sce_settings.get_index_at_time(end_time)
        return Trace(self.list_of_values[(i1-self.index_of_starting_time):(i2-self.index_of_starting_time)],i1)
    
    def get_trace_over_month(self, month):
        i1 = sce_settings.FIRST_INDEX_OF_MONTH[month]
        i2 = sce_settings.FIRST_INDEX_OF_MONTH[month + 1]
        return Trace(self.list_of_values[(i1-self.index_of_starting_time):(i2-self.index_of_starting_time)],i1)
    
    def get_trace_over_time_index(self, start_index, end_index):
        return Trace(self.list_of_values[(start_index-self.index_of_starting_time):(end_index-self.index_of_starting_time)],start_index)
    
    def scale_values(self, s):
        self.list_of_values = [v * s for v in self.list_of_values]

    def set_value_at_time(self, start_time, end_time, value):
        i1 = sce_settings.get_index_at_time(start_time)
        i2 = sce_settings.get_index_at_time(end_time)
        self.list_of_values[(i1-self.index_of_starting_time):(i2-self.index_of_starting_time)] = ([value] * (i2-i1))

    def append_trace(self, other):
        self.list_of_values.extend(other.get_list_of_values())
        return self
    
    def remove_trace_before_time(self, cut_off_time):
        i = sce_settings.get_index_at_time(cut_off_time)
        removed_trace = Trace(self.list_of_values[0:(i-self.index_of_starting_time)],self.index_of_starting_time)
        self.list_of_values[0:(i-self.index_of_starting_time)] = []
        self.index_of_starting_time = i
        return removed_trace

    def remove_trace_before_time_index(self, cut_off_time_index):
        removed_trace = Trace(self.list_of_values[0:(cut_off_time_index-self.index_of_starting_time)],self.index_of_starting_time)
        self.list_of_values[0:(cut_off_time_index-self.index_of_starting_time)] = []
        self.index_of_starting_time = cut_off_time_index
        return removed_trace
                
    def __add__(self, other):
        return Trace([x + y for (x,y) in itertools.izip(self.list_of_values,other.get_list_of_values())],self.index_of_starting_time)
    
    def __sub__(self, other):
        return Trace([x - y for (x,y) in itertools.izip(self.list_of_values,other.get_list_of_values())],self.index_of_starting_time)
    
    def __mul__(self, other):
        return Trace([x * y for (x,y) in itertools.izip(self.list_of_values,other.get_list_of_values())],self.index_of_starting_time)
    
    
class RateSchedule(object):
    """
    An abstract class for a rate schedule. 
    Specific rate schedule classes are subclasses of this class.
    
    Attributes
    ----------
    name : string
    rate_component_dictionary : dictionary
    rate_update_rules_dictionary : dictionary
            
    """
    
    def __init__(self, name, rate_component_dictionary, rate_update_rules_dictionary):
        self.name = name
        self.rate_component_dictionary = rate_component_dictionary
        self.rate_update_rules_dictionary = rate_update_rules_dictionary
    
    def get_name(self):
        return self.name
    
    def get_rate_component_dictionary(self):
        return self.rate_component_dictionary
    
    def get_rate_update_rules_dictionary(self):
        return self.rate_update_rules_dictionary
    
    def generate_utility_bill(self, customer_name, load_profile, baseline_region, month_of_billing_period, bill_for_previous_month):
        raise Exception('Class derived from RateSchedule must implement generate_utility_bill()')
    
    def calculate_total_charge_over_year(self, load_profile, baseline_region):
        raise Exception('Class derived from RateSchedule must implement calculate_total_charges()')


class TierNetMeterRateSchedule(RateSchedule):
    """
    A class for a rate schedule with tiered tariff and net metering.
    
    Attributes
    ----------
    name : string
            The name of the rate schedule.
    rate_component_dictionary : dictionary 
            This dictionary contains the following keys.
            minimum_charge : float
            customer_charge_demand_differentiated_flag : boolean
            demand_differentiated_break_point : float
            customer_charge_above_break_point : float
            customer_charge : float
            number_of_tiers : integer
            T2_usage_baseline : float
            T3_usage_baseline : float
            T4_usage_baseline : float
            T1_rate : float
            T2_rate : float
            T3_rate : float
            T4_rate : float
            T5_rate : float
            net_surplus_compensation_rate : float
    rate_update_rules_dictionary : dictionary
            This dictionary contains the following keys.
            CARE_flag : boolean
            ratio_flag : boolean
            T1_increase : float
            T2_increase : float
            T4_T3_delta : float
            T5_T4_delta : float
            T2_T1_ratio : float
            T3_T1_ratio : float
            T4_T1_ratio : float
            T5_T1_ratio : float
            T1_CARE_discount : float
            T2_CARE_discount : float
            T3_CARE_discount : float
            T4_CARE_discount : float
            T5_CARE_discount : float
            fixed_charge_CARE_discount : float
    """
    
    def __init__(self, name, rate_component_dictionary, rate_update_rules_dictionary):
        super(TierNetMeterRateSchedule,self).__init__(name, rate_component_dictionary, rate_update_rules_dictionary)
        self.history_of_calculations = dict()
    
    @classmethod
    def parse_yaml(cls, specs):
        return TierNetMeterRateSchedule(specs['name'], specs['rate_component_dictionary'], specs['rate_update_rules_dictionary'])
    
    def is_CARE(self):
        if self.rate_update_rules_dictionary['CARE_flag'] == 1:
            return True
        else:
            return False
    
    def is_ratio(self):
        if self.rate_update_rules_dictionary['ratio_flag'] == 1:
            return True
        else:
            return False
    
    def get_number_of_tiers(self):
        return self.rate_component_dictionary['number_of_tiers']
    
    def set_basic_charge(self, basic_charge):
        self.rate_component_dictionary['customer_charge'] = basic_charge
        return self
        
    def set_tiered_variable_charge(self, tiered_variable_charge):
        self.rate_component_dictionary['T1_rate'] = tiered_variable_charge[0]
        self.rate_component_dictionary['T2_rate'] = tiered_variable_charge[1]
        self.rate_component_dictionary['T3_rate'] = tiered_variable_charge[2]
        self.rate_component_dictionary['T4_rate'] = tiered_variable_charge[3]
        self.rate_component_dictionary['T5_rate'] = tiered_variable_charge[4]
        return self
        
    def set_net_surplus_compensation_rate(self, net_surplus_compensation_rate):
        self.rate_component_dictionary['net_surplus_compensation_rate'] = net_surplus_compensation_rate
        return self
    
    def get_basic_charge(self):
        return self.rate_component_dictionary['customer_charge']
    
    def get_tiered_variable_charge(self):
        return [self.rate_component_dictionary['T1_rate'], self.rate_component_dictionary['T2_rate'], self.rate_component_dictionary['T3_rate'], self.rate_component_dictionary['T4_rate'], self.rate_component_dictionary['T5_rate']]
    
    def get_net_surplus_compensation_rate(self):
        return self.rate_component_dictionary['net_surplus_compensation_rate']
    
    def generate_utility_bill(self, customer_name, load_profile, baseline_allocation, month_of_billing_period, bill_for_previous_month = None):
        index_of_start_time = sce_settings.FIRST_INDEX_OF_MONTH[month_of_billing_period]
        index_of_end_time = sce_settings.FIRST_INDEX_OF_MONTH[month_of_billing_period + 1]
        baseline_allocation_for_whole_month = baseline_allocation.get_integral_over_time_index(index_of_start_time, index_of_end_time)
        usage = load_profile.get_integral_over_time_index(index_of_start_time, index_of_end_time)
        
        if self.rate_component_dictionary['customer_charge_demand_differentiated_flag'] == 1:
            peak = load_profile.get_integral_over_time_index(index_of_start_time, index_of_end_time)/sce_settings.NUMBER_OF_HOURS_IN_ONE_YEAR
            if peak <= self.rate_component_dictionary['demand_differentiated_break_point']:
                basic_charge = self.rate_component_dictionary['customer_charge']
            else:
                basic_charge = self.rate_component_dictionary['customer_charge_above_break_point']
        else:
            basic_charge = self.rate_component_dictionary['customer_charge']
        tiered_variable_charge = [self.rate_component_dictionary['T1_rate'],
                                  self.rate_component_dictionary['T2_rate'],
                                  self.rate_component_dictionary['T3_rate'],
                                  self.rate_component_dictionary['T4_rate'],
                                  self.rate_component_dictionary['T5_rate']]
        net_surplus_compensation_rate = self.rate_component_dictionary['net_surplus_compensation_rate']                
        units_of_basic_charge = sce_settings.NUMBER_OF_DAYS_IN_EACH_MONTH[month_of_billing_period % 12]
        sign_of_usage = sce_settings.sign(usage)
        absolute_usage = abs(usage)
        if absolute_usage <= self.rate_component_dictionary['T2_usage_baseline'] * baseline_allocation_for_whole_month:
            units_of_tiered_variable_charge = [usage, 0, 0, 0, 0]
        elif absolute_usage <= self.rate_component_dictionary['T3_usage_baseline'] * baseline_allocation_for_whole_month:
            units_of_tiered_variable_charge = [sign_of_usage * self.rate_component_dictionary['T2_usage_baseline'] * baseline_allocation_for_whole_month, sign_of_usage * ( absolute_usage - self.rate_component_dictionary['T2_usage_baseline'] * baseline_allocation_for_whole_month), 0, 0, 0]
        elif absolute_usage <= self.rate_component_dictionary['T4_usage_baseline'] * baseline_allocation_for_whole_month:
            units_of_tiered_variable_charge = [sign_of_usage * self.rate_component_dictionary['T2_usage_baseline'] * baseline_allocation_for_whole_month, sign_of_usage * ( self.rate_component_dictionary['T3_usage_baseline'] - self.rate_component_dictionary['T2_usage_baseline'] ) * baseline_allocation_for_whole_month, sign_of_usage * (absolute_usage - self.rate_component_dictionary['T3_usage_baseline'] * baseline_allocation_for_whole_month), 0, 0]
        elif absolute_usage <= self.rate_component_dictionary['T5_usage_baseline'] * baseline_allocation_for_whole_month:
            units_of_tiered_variable_charge = [sign_of_usage * self.rate_component_dictionary['T2_usage_baseline'] * baseline_allocation_for_whole_month, sign_of_usage * ( self.rate_component_dictionary['T3_usage_baseline'] - self.rate_component_dictionary['T2_usage_baseline'] ) * baseline_allocation_for_whole_month, sign_of_usage * ( self.rate_component_dictionary['T4_usage_baseline'] - self.rate_component_dictionary['T3_usage_baseline'] ) * baseline_allocation_for_whole_month, sign_of_usage * ( absolute_usage - self.rate_component_dictionary['T4_usage_baseline'] * baseline_allocation_for_whole_month) , 0] 
        else:
            units_of_tiered_variable_charge = [sign_of_usage * self.rate_component_dictionary['T2_usage_baseline'] * baseline_allocation_for_whole_month, sign_of_usage * ( self.rate_component_dictionary['T3_usage_baseline'] - self.rate_component_dictionary['T2_usage_baseline'] ) * baseline_allocation_for_whole_month, sign_of_usage * ( self.rate_component_dictionary['T4_usage_baseline'] - self.rate_component_dictionary['T3_usage_baseline'] ) * baseline_allocation_for_whole_month, sign_of_usage * ( self.rate_component_dictionary['T5_usage_baseline'] - self.rate_component_dictionary['T4_usage_baseline'] ) * baseline_allocation_for_whole_month, sign_of_usage * ( absolute_usage - self.rate_component_dictionary['T5_usage_baseline'] * baseline_allocation_for_whole_month) ]
        total_basic_charge = units_of_basic_charge * basic_charge
        total_tiered_variable_charge = sum(u * r for u, r in zip(units_of_tiered_variable_charge, tiered_variable_charge))
        month_of_relevant_period = 12 if bill_for_previous_month is None else bill_for_previous_month.get_month_of_relevant_period()
        month_of_relevant_period = (month_of_relevant_period + 1) if month_of_relevant_period < 12 else 1
        if month_of_relevant_period == 1:
            cumulative_usage_over_current_relevant_period = usage
            units_of_net_surplus_compensation = 0
            total_net_surplus_compensation = 0
            cumulative_usage_charge_over_current_relevant_period = total_tiered_variable_charge
        elif month_of_relevant_period == 12:
            cumulative_usage_over_current_relevant_period = usage + bill_for_previous_month.get_cumulative_usage_over_current_relevant_period()
            units_of_net_surplus_compensation = - min(0, cumulative_usage_over_current_relevant_period)
            total_net_surplus_compensation = units_of_net_surplus_compensation * net_surplus_compensation_rate
            cumulative_usage_charge_over_current_relevant_period = max(0, total_tiered_variable_charge + bill_for_previous_month.get_cumulative_usage_charge_over_current_relevant_period())
            if cumulative_usage_charge_over_current_relevant_period == 0:
                total_tiered_variable_charge = - bill_for_previous_month.get_cumulative_usage_charge_over_current_relevant_period()
            cumulative_usage_charge_over_current_relevant_period -= total_net_surplus_compensation
        else:
            cumulative_usage_over_current_relevant_period = usage + bill_for_previous_month.get_cumulative_usage_over_current_relevant_period()
            units_of_net_surplus_compensation = 0
            total_net_surplus_compensation = 0
            cumulative_usage_charge_over_current_relevant_period = total_tiered_variable_charge + bill_for_previous_month.get_cumulative_usage_charge_over_current_relevant_period()
        
        b = TierNetMeterBill(customer_name, month_of_billing_period,
                                {'month_of_relevant_period' : month_of_relevant_period,
                                 'usage' : usage,
                                 'cumulative_usage_charge_over_current_relevant_period' : cumulative_usage_charge_over_current_relevant_period,
                                 'cumulative_usage_over_current_relevant_period' : cumulative_usage_over_current_relevant_period,
                                 'baseline_allocation_for_this_month' : baseline_allocation_for_whole_month,
                                 'units_of_basic_charge' : units_of_basic_charge,
                                 'units_of_tiered_variable_charge' : units_of_tiered_variable_charge,
                                 'units_of_net_surplus_compensation' : units_of_net_surplus_compensation,
                                 'total_basic_charge' : total_basic_charge,
                                 'total_tiered_variable_charge' : total_tiered_variable_charge,
                                 'total_net_surplus_compensation' : total_net_surplus_compensation,
                                 'basic_charge' : basic_charge,
                                 'tiered_variable_charge' : tiered_variable_charge,
                                 'net_surplus_compensation_rate' : net_surplus_compensation_rate})
        return b
                                
    def calculate_monthly_charge(self, load_profile, baseline_allocation, first_month_of_billing_period, number_of_months, bill_for_previous_month = None):          
        monthly_charge = []
        for m in range(first_month_of_billing_period, first_month_of_billing_period + number_of_months):
            bill_for_previous_month = self.generate_utility_bill('', load_profile, baseline_allocation, m, bill_for_previous_month)
            monthly_charge.append(bill_for_previous_month.get_total_basic_charge() + bill_for_previous_month.get_total_tiered_variable_charge() - bill_for_previous_month.get_total_net_surplus_compensation())
        return monthly_charge
    

class Bill(object):
    """
    A class for representing a utility bill.
    Bills for specific rate schedules are subclasses of this class.
    
    Attributes
    ----------
    customer_name : string
    month_of_billing_period : integer
    bill_item_dictionary : dictionary
    
    """
    
    def __init__(self, customer_name, month_of_billing_period, bill_item_dictionary):
        self.customer_name = customer_name
        self.month_of_billing_period = month_of_billing_period
        self.bill_item_dictionary = bill_item_dictionary
    
    def get_customer_name(self):
        return self.customer_name
    
    def get_month_of_billing_period(self):
        return self.month_of_billing_period
        
    def get_bill_item_dictionary(self):
        return self.bill_item_dictionary
        
        
class TierNetMeterBill(Bill):
    """
    A class for representing a utility bill of a customer who is under a rate schedule with tiered tariff and net metering.
    
    Attributes
    ----------
    customer_name : string
    month_of_billing_period : integer
    bill_item_dictionary : dictionary
                This dictionary contains the following keys.
                month_of_relevant_period : integer
                usage : float
                cumulative_usage_charge_over_current_relevant_period : float
                cumulative_usage_over_current_relevant_period : float
                baseline_allocation_for_this_month : float
                units_of_basic_charge : float
                units_of_tiered_variable_charge : list of float
                units_of_net_surplus_compensation : float
                total_basic_charge : float
                total_tiered_variable_charge : float
                total_net_surplus_compensation : float
                basic_charge : float
                tiered_variable_charge : list of float
                net_surplus_compensation_rate : float
    
    """
    
    def __init__(self, customer_name, month_of_billing_period, bill_item_dictionary): 
        super(TierNetMeterBill,self).__init__(customer_name, month_of_billing_period, bill_item_dictionary)
        
    def get_month_of_relevant_period(self):
        return self.bill_item_dictionary['month_of_relevant_period']
    
    def get_usage(self):
        return self.bill_item_dictionary['usage']
    
    def get_cumulative_usage_charge_over_current_relevant_period(self):
        return self.bill_item_dictionary['cumulative_usage_charge_over_current_relevant_period']
    
    def get_cumulative_usage_over_current_relevant_period(self):
        return self.bill_item_dictionary['cumulative_usage_over_current_relevant_period']
    
    def get_baseline_allocation_for_this_month(self):
        return self.bill_item_dictionary['baseline_allocation_for_this_month']
    
    def get_units_of_basic_charge(self):
        return self.bill_item_dictionary['units_of_basic_charge']
    
    def get_units_of_tiered_variable_charge(self):
        return self.bill_item_dictionary['units_of_tiered_variable_charge']
    
    def get_units_of_net_surplus_compensation(self):
        return self.bill_item_dictionary['units_of_net_surplus_compensation']
    
    def get_total_basic_charge(self):
        return self.bill_item_dictionary['total_basic_charge']
    
    def get_total_tiered_variable_charge(self):
        return self.bill_item_dictionary['total_tiered_variable_charge']
    
    def get_total_net_surplus_compensation(self):
        return self.bill_item_dictionary['total_net_surplus_compensation']
        
    def get_basic_charge(self):
        return self.bill_item_dictionary['basic_charge']
    
    def get_tiered_variable_charge(self):
        return self.bill_item_dictionary['tiered_variable_charge']
    
    def get_net_surplus_compensation_rate(self):
        return self.bill_item_dictionary['net_surplus_compensation_rate']
        

class CustomerCategoryAccount(object):
    """
    A class for representing a customer's account information at the utility. 
    The account contains information on the customer's baseline zone, 
    the customer's current rate schedule, his load profile since the last billed 
    month up to the current time-step, and all his historical utility bills. 
    The account could also contain miscellaneous notes.
    
    Attributes
    ----------
    customer_category_name : string
    number_of_customers : int
    baseline_region : BaselineRegion
    current_rate_schedule : RateSchedule
    dictionary_of_unprocessed_load_profile : dictionary (Trace, number_of_customers)
    bill_history : dictionary (month, dictionary (PvTechnology, (utility bill, number_of_customers_with_this_utility_bill)))
    notes_dictionary : dictionary
    
    """
    
    def __init__(self, customer_category_name, number_of_customers, baseline_region, current_rate_schedule):
        self.customer_category_name = customer_category_name
        self.number_of_customers = number_of_customers
        self.baseline_region = baseline_region
        self.current_rate_schedule = current_rate_schedule
        self.dictionary_of_unprocessed_load_profile = dict() #Trace([],0)
        self.bill_history = dict()
        self.notes_dictionary = dict()
	     
    def get_customer_account_number(self):
        return self.customer_account_number
    
    def get_number_of_customers(self):
        return self.number_of_customers
    
    def get_baseline_region(self):
        return self.baseline_region
    
    def get_current_rate_schedule(self):
        return self.current_rate_schedule
    
    def get_bill_history(self):
        return self.bill_history
    
    def get_bill(self, month):
        return self.bill_history[month]
    
    def get_notes_dictionary(self):
        return self.notes_dictionary
    
    def get_total_usage(self, start_month, number_of_months):
        usage = 0
        for m in range(start_month, start_month + number_of_months):
            for v in self.bill_history[m].itervalues():
                usage += v[0].get_usage() * v[1]
        return usage
    
    def get_distribution_of_total_summer_usage(self, start_month, number_of_months):
        distribution_of_total_summer_usage = []
        number_of_customers_processed = 0
        for m in range(start_month + number_of_months - 1, start_month, -1):
            # find the customers that adopted PV in this month
            for pv_technology, v in self.bill_history[m].iteritems():
                if v[1] > self.bill_history[m-1][pv_technology][1]:
                    break
            usage = 0
            for n in range(start_month, m):
                if (n % 12) in sce_settings.SUMMER_MONTHS:
                    usage += self.bill_history[n][None][0].get_usage()
            for n in range(m, start_month + number_of_months):
                if (n % 12) in sce_settings.SUMMER_MONTHS:
                    usage += self.bill_history[n][pv_technology][0].get_usage()
            distribution_of_total_summer_usage.append((usage/sce_settings.NUMBER_OF_DAYS_IN_SUMMER, v[1]))
            number_of_customers_processed += v[1]
        usage = 0
        for n in range(start_month, start_month + number_of_months):
            if (n % 12) in sce_settings.SUMMER_MONTHS:
                usage += self.bill_history[n][None][0].get_usage()
        distribution_of_total_summer_usage.append((usage/sce_settings.NUMBER_OF_DAYS_IN_SUMMER, self.bill_history[start_month][None][1] - number_of_customers_processed))
        return distribution_of_total_summer_usage
    
    def get_total_summer_usage(self, start_month, number_of_months):
        usage = 0
        for m in range(start_month, start_month + number_of_months):
            if (m % 12) in sce_settings.SUMMER_MONTHS:
                usage += self.bill_history[m].get_usage()
        return usage
    
    def get_distribution_of_total_winter_usage(self, start_month, number_of_months):
        distribution_of_total_winter_usage = []
        number_of_customers_processed = 0
        for m in range(start_month + number_of_months - 1, start_month, -1):
            # find the customers that adopted PV in this month
            for pv_technology, v in self.bill_history[m].iteritems():
                if v[1] > self.bill_history[m-1][pv_technology][1]:
                    break
            usage = 0
            for n in range(start_month, m):
                if (n % 12) in sce_settings.WINTER_MONTHS:
                    usage += self.bill_history[n][None][0].get_usage()
            for n in range(m, start_month + number_of_months):
                if (n % 12) in sce_settings.WINTER_MONTHS:
                    usage += self.bill_history[n][pv_technology][0].get_usage()
            distribution_of_total_winter_usage.append((usage/sce_settings.NUMBER_OF_DAYS_IN_WINTER, v[1]))
            number_of_customers_processed += v[1]
        usage = 0
        for n in range(start_month, start_month + number_of_months):
            if (n % 12) in sce_settings.WINTER_MONTHS:
                usage += self.bill_history[n][None][0].get_usage()
        distribution_of_total_winter_usage.append((usage/sce_settings.NUMBER_OF_DAYS_IN_WINTER, self.bill_history[start_month][None][1] - number_of_customers_processed))
        return distribution_of_total_winter_usage
    
    def get_total_winter_usage(self, start_month, number_of_months):
        usage = 0
        for m in range(start_month, start_month + number_of_months):
            if (m % 12) in sce_settings.WINTER_MONTHS:
                usage += self.bill_history[m].get_usage()
        return usage
    
    def set_current_rate_schedule(self, rate_schedule):
        self.current_rate_schedule = rate_schedule
    
    def add_note(self, name, note):
        self.notes_dictionary[name] = note
        
    def delete_note(self, name):
        del self.notes_dictionary[name]
        
    def get_customer_category_tier(self, usage_lst):
       for tier in range(len(usage_lst)):
            if usage_lst[tier] == 0:
                return tier 
       return len(usage_lst)
      
    def log_bill(self, bill, pv_technology, number_of_customers):
         '''
          attributes:
             number_of_customers: float
             usage: float
             cumulative_usage_charge_over_current_relevant_period: float
             cumulative_usage_over_current_relevant_period: float
             baseline_allocation_for_this_month: float
             units_of_basic_charge: float
             units_of_tiered_variable_charge: list of floats
             units_of_net_surplus_compensation: float
             total_basic_charge: float
             total_tiered_variable_charge: float
             total_net_surplus_compensation: float
             basic_charge: float
             tiered_variable_charge: list of float
             net_surplus_compensation_rate: float
     
          output:
            dict_utility_log = {month_of_billing_period: {customer_category_name: {pv_technology: [{attribute_dct}, ....], ....}, ....}, .....}
         '''
         
         if pv_technology == None:
            pv_quantity = None
         else:
            pv_quantity = pv_technology.get_quantity()                                       
     
         temp_dict = {}     
         month_of_billing_period = bill.month_of_billing_period
         customer_category_name = bill.customer_name
         pv_tech = pv_quantity
         
         # Write to Logfile
         nonagent_utility_logger = logging.getLogger('utilityLogger')
         nonagent_utility_logger.info(' '.join('Bill history for customer_category_name: %s, \
                              pv_technology: %s, \
                              number_of_customers: %d, \
                              month_of_billing_period: %d, \
                              month_of_relevant_period: %d, \
                              usage: %f, \
                              cumulative_usage_charge_over_current_relevant_period: %f, \
                              cumulative_usage_over_current_relevant_period: %f, \
                              baseline_allocation_for_this_month: %f, \
                              units_of_basic_charge: %f, \
                              units_of_tiered_variable_charge: [%s], \
                              units_of_net_surplus_compensation: %f, \
                              total_basic_charge: %f, \
                              total_tiered_variable_charge: %f, \
                              total_net_surplus_compensation: %f, \
                              basic_charge: %f, \
                              tiered_variable_charge: [%s], \
                              net_surplus_compensation_rate: %f\n'.split()) % 
                              (bill.customer_name,
                               pv_quantity,
                               number_of_customers,
                               bill.month_of_billing_period, 
                               bill.bill_item_dictionary['month_of_relevant_period'], 
                               bill.bill_item_dictionary['usage'], 
                               bill.bill_item_dictionary['cumulative_usage_charge_over_current_relevant_period'], 
                               bill.bill_item_dictionary['cumulative_usage_over_current_relevant_period'],
                               bill.bill_item_dictionary['baseline_allocation_for_this_month'],
                               bill.bill_item_dictionary['units_of_basic_charge'],
                               ', '.join(map(str, bill.bill_item_dictionary['units_of_tiered_variable_charge'])),
                               bill.bill_item_dictionary['units_of_net_surplus_compensation'],
                               bill.bill_item_dictionary['total_basic_charge'],
                               bill.bill_item_dictionary['total_tiered_variable_charge'],
                               bill.bill_item_dictionary['total_net_surplus_compensation'],
                               bill.bill_item_dictionary['basic_charge'],
                               ', '.join(map(str, bill.bill_item_dictionary['tiered_variable_charge'])),
                               bill.bill_item_dictionary['net_surplus_compensation_rate']))
         
         # Write to Datastore
         temp_dict['utility_log_number_of_customers'] = number_of_customers
         temp_dict['utility_log_usage'] = bill.bill_item_dictionary['usage']
         temp_dict['utility_log_cumulative_usage_charge_over_current_relevant_period'] = bill.bill_item_dictionary['cumulative_usage_charge_over_current_relevant_period']
         temp_dict['utility_log_cumulative_usage_over_current_relevant_period'] = bill.bill_item_dictionary['cumulative_usage_over_current_relevant_period']
         temp_dict['utility_log_baseline_allocation_for_this_month'] = bill.bill_item_dictionary['baseline_allocation_for_this_month']
         temp_dict['utility_log_units_of_basic_charge'] = bill.bill_item_dictionary['units_of_basic_charge']
         temp_dict['utility_log_units_of_tiered_variable_charge'] = bill.bill_item_dictionary['units_of_tiered_variable_charge']
         temp_dict['utility_log_units_of_net_surplus_compensation'] = bill.bill_item_dictionary['units_of_net_surplus_compensation']
         temp_dict['utility_log_total_basic_charge'] = bill.bill_item_dictionary['total_basic_charge']
         temp_dict['utility_log_total_tiered_variable_charge'] = bill.bill_item_dictionary['total_tiered_variable_charge']
         temp_dict['utility_log_total_net_surplus_compensation'] = bill.bill_item_dictionary['total_net_surplus_compensation'],
         temp_dict['utility_log_basic_charge'] = bill.bill_item_dictionary['basic_charge']
         temp_dict['utility_log_tiered_variable_charge'] = bill.bill_item_dictionary['tiered_variable_charge']
         temp_dict['utility_log_net_surplus_compensation_rate'] = bill.bill_item_dictionary['net_surplus_compensation_rate']
     
         # case 1: month_of billing period not in log
         if month_of_billing_period not in sce_settings.dict_utility_log:
             sce_settings.dict_utility_log[month_of_billing_period] = {customer_category_name: {pv_tech: [temp_dict]}}
          
         # case 2: month_of billing period in log
         else:
                # case 2.1: month_of billing period in log & customer_category_name & pv_technology not in log
                if customer_category_name not in sce_settings.dict_utility_log[month_of_billing_period].keys():
                    sce_settings.dict_utility_log[month_of_billing_period][customer_category_name] = {pv_tech: [temp_dict]}
                # case 2.2: month_of billing period in log & customer_category_name in log & pv_technology not in log
                elif customer_category_name in sce_settings.dict_utility_log[month_of_billing_period].keys() and pv_tech not in sce_settings.dict_utility_log[month_of_billing_period][customer_category_name].keys():
                    sce_settings.dict_utility_log[month_of_billing_period][customer_category_name][pv_tech] = [temp_dict]
                # case 2.3: month_of billing period in log & customer_category_name & pv_technology in log 
                else:
                    sce_settings.dict_utility_log[month_of_billing_period][customer_category_name][pv_tech].append(temp_dict)

    
    def add_load_profile(self, new_dictionary_of_load_profile):
        for pv_technology, value in new_dictionary_of_load_profile.iteritems():
            unprocessed_load_profile = value[0]
            number_of_customers = value[1]
            m1 = unprocessed_load_profile.get_start_month()
            m2 = unprocessed_load_profile.get_end_month()
            bill = None if m1 == 0 else self.bill_history[m1-1][pv_technology][0]
            for month in range(m1,m2):
                bill = self.current_rate_schedule.generate_utility_bill(self.customer_category_name, unprocessed_load_profile, self.baseline_region.get_baseline_allocation(), month, bill)
                if month not in self.bill_history:
                    self.bill_history[month] = dict()
                self.bill_history[month][pv_technology] = (bill, number_of_customers)
                self.log_bill(bill, pv_technology, number_of_customers)
                
class BaselineRegion(object):
    """
    A class for a baseline zone.  
    This class contains a list of customers residing in this baseline region and also 
    the historical and future baseline allocations to this baseline region.
    
    Attributes
    ----------
    name : string
    baseline_allocation : Trace
    customer_category_account_list : list of CustomerAccount
    
    """
    
    def __init__(self, name, summer_baseline_in_kwh_per_day, winter_baseline_in_kwh_per_day):
        self.name = name
        values = []
        summer_baseline_in_kwh_per_second = summer_baseline_in_kwh_per_day / (sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR / sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR)
        winter_baseline_in_kwh_per_second = winter_baseline_in_kwh_per_day / (sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR / sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR)
        
        for m in sce_settings.TICK_VALUES_MONTH:
            if (m % 12) in sce_settings.SUMMER_MONTHS:
                values.append(summer_baseline_in_kwh_per_second)
            else:
                values.append(winter_baseline_in_kwh_per_second)
        self.baseline_allocation = Trace(values,0)
        self.customer_category_account_list = []
    
    @classmethod
    def parse_yaml(cls, specs):
        return BaselineRegion(specs['name'], float(specs['summer_baseline_in_kwh_per_year'])/ sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR,
                                             float(specs['winter_baseline_in_kwh_per_year'])/ sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR) 
    
    def get_name(self):
        return self.name
    
    def get_baseline_allocation(self):
        return self.baseline_allocation
    
    def get_customer_category_account_list(self):
        return self.customer_category_account_list
    
    def get_baseline_allocation_for_period(self, start_time, end_time):
        return self.baseline_allocation.get_integral_over_time(start_time, end_time)
    
    def add_customer_category_account(self, customer_category_account):
        self.customer_category_account_list.append(customer_category_account)
        
    def remove_customer_category_account(self, customer_category_account):
        self.customer_category_account_list.remove(customer_category_account)
    
    def update_baseline_allocation(self, month_of_change, summer_baseline_in_kwh_per_day, winter_baseline_in_kwh_per_day):
        summer_baseline_in_kwh_per_second = summer_baseline_in_kwh_per_day / (sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR / sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR)
        winter_baseline_in_kwh_per_second = winter_baseline_in_kwh_per_day / (sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR / sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR)
        i = sce_settings.FIRST_INDEX_OF_MONTH[month_of_change]
        v = self.baseline_allocation.get_list_of_values()
        for (i,m) in enumerate(sce_settings.TICK_VALUES_MONTH):
            if (m % 12) in sce_settings.SUMMER_MONTHS:
                v[i] = summer_baseline_in_kwh_per_second
            else:
                v[i] = winter_baseline_in_kwh_per_second
    
    
class Technology(object):
    """
    A class for a technology owned by a customer. 
    Specific technologies are subclasses of this class.
    
    Attributes
    ----------
    name : string
    parameter_dictionary : dictionary
            This dictionary contains the following keys.
            quantity : float
            purchase_month : float
            lifetime_in_months : float
            initial_payment : float
            monthly_payment : float
    
    """
    
    def __init__(self, name, parameter_dictionary):
        self.name = name
        self.parameter_dictionary = parameter_dictionary

    def get_name(self):
        return self.name
        
    def get_quantity(self):
        return self.parameter_dictionary['quantity']
    
    def get_purchase_month(self):
        return self.parameter_dictionary['purchase_month']
    
    def get_lifetime_in_months(self):
        return self.parameter_dictionary['lifetime_in_months']
    
    def get_initial_payment(self):
        return self.parameter_dictionary['initial_payment']
    
    def get_monthly_payment(self):
        return self.parameter_dictionary['monthly_payment']
    
    def get_reduction_in_load_over_time_index(self, index_of_start_time, index_of_end_time, parameter_dictionary = None):
        raise Exception('Class derived from Technology must implement get_reduction_in_load()')


class PvTechnology(Technology):
    """
    A class for a PV system.
    
    Attributes
    ----------
    name : string
    parameter_dictionary : dictionary
            This dictionary contains the following keys.
            quantity : float
                        The quantity of PV in kW.
            purchase_month : float
                        The first operating month of this PV system.
            lifetime_in_months : float
                        The lifetime of this lease in months.
            initial_payment : float
                        The initial up front payment.
            monthly_payment : float
                        The monthly lease payment.
            conversion_factor : float
                        A multiplicative factor that converts a solar intensity value into 
                        kWh output for a 1 kW PV system.
            efficiency : Trace
                        A time trace of values between 0 and 1 that represents the decrease 
                        in production of the PV system over time.
    
    """
    
    def __init__(self, name, parameter_dictionary):
        super(PvTechnology,self).__init__(name, parameter_dictionary)
        
    def get_efficiency_at_time(self, time):
        return self.parameter_dictionary['efficiency'].get_value_at_time(time)
    
    def get_reduction_in_load_over_time_index(self, index_of_start_time, index_of_end_time, parameter_dictionary):
        solar_profile = parameter_dictionary['solar_intensity_profile'].get_trace_over_time_index(index_of_start_time, index_of_end_time)
        solar_profile.scale_values(self.parameter_dictionary['quantity']*self.parameter_dictionary['conversion_factor'])
        return solar_profile
    

class TechnologyInstaller(object):
    """
    A class for a technology installer.
    Technology installers for specific technologies are subclasses of this class.
    The role of the technology installer is to recommend a technology system 
    for a customer with a given load profile and rate schedule.
    
    Attributes
    ----------
    name : string
    parameter_dictionary : dictionary
    
    """
    
    def __init__(self, name, parameter_dictionary):
        self.name = name
        self.parameter_dictionary = parameter_dictionary
    
    def calculate_constant_monthly_payment(self, number_of_months, principal, annual_interest_rate):
        monthly_interest_rate = float(annual_interest_rate) / 12 / 100
        return principal * ( monthly_interest_rate ) / ( 1 - ( 1 + monthly_interest_rate ) ** ( - number_of_months ) )
    
    def calculate_net_present_value(self, monthly_payments, annual_interest_rate):
        monthly_interest_rate = annual_interest_rate / 12 / 100
        npv = 0
        for t in range(0, len(monthly_payments)):
            npv += monthly_payments[t] / ( ( 1 + monthly_interest_rate ) ** t )
        return npv
    
    def get_recommended_quantity_at_time_index(self, index_of_current_time, load_profile, baseline_allocation, rate_schedule, parameter_dictionary = None):
        raise Exception('Class derived from TechnologyInstaller must implement get_recommended_technology_quantity()')
  
    def get_recommended_quantity_at_time(self, current_time, load_profile, baseline_allocation, rate_schedule, parameter_dictionary = None):
        raise Exception('Class derived from TechnologyInstaller must implement get_recommended_technology_quantity()')


class PvInstaller(TechnologyInstaller):
    """
    A class for a PV installer.
    
    Attributes
    ----------
    name : string
    parameter_dictionary : dictionary
                This dictionary contains the following keys.
                kw_per_panel : float
                        The kW rating of each PV panel.
                minimum_number_of_panels : integer
                        The minimum number of panels for a PV system.
                maximum_number_of_panels : integer
                        The maximum number of panels for a PV system.
                conversion_factor : float
                        A multiplicative factor that converts a solar intensity value into 
                        kWh output for a 1 kW PV system.
                efficiency : Trace
                        A time trace of values between 0 and 1 that represents the decrease
                        in efficiency of the PV system over time.
                cost_per_kw : Trace
                        A time trace that represents the cost of PV in $/kW.
                term_in_months : integer
                        The length of the lease in months.
                annual_interest_rate : float
                        The annual interest rate on the lease.
    
    """
    
    def __init__(self, name, parameter_dictionary):
        super(PvInstaller,self).__init__(name, parameter_dictionary)
        self.parameter_dictionary['history_of_calculations'] = dict()

    def get_name_of_technology(self):
        return 'Pv System'
        
    @classmethod   
    def parse_yaml(cls, specs):                                               
        return PvInstaller(specs['name'], {'kw_per_panel': specs['parameter_dictionary']['kw_per_panel'],
                                           'minimum_number_of_panels': specs['parameter_dictionary']['minimum_number_of_panels'],
                                           'maximum_number_of_panels': specs['parameter_dictionary']['maximum_number_of_panels'],
                                           'conversion_factor': specs['parameter_dictionary']['conversion_factor'],
                                           'efficiency': Trace([float(x) for x in specs['parameter_dictionary']['efficiency']['list_of_values']], specs['parameter_dictionary']['efficiency']['index_of_begin_tick']),
                                           'cost_per_kw': Trace([float(x) for x in specs['parameter_dictionary']['cost_per_kw']['list_of_values']], specs['parameter_dictionary']['cost_per_kw']['index_of_begin_tick']),
                                           'term_in_months': specs['parameter_dictionary']['term_in_months'],
                                           'annual_interest_rate': specs['parameter_dictionary']['annual_interest_rate'],
                                           'consumptionBin_systemSize': specs['parameter_dictionary']['consumptionBin_systemSize']}) 
                                                   
    def get_kw_per_panel(self):
        return self.parameter_dictionary['kw_per_panel']
    
    def get_minimum_number_of_panels(self):
        return self.parameter_dictionary['minimum_number_of_panels']
    
    def get_maximum_number_of_panels(self):
        return self.parameter_dictionary['maximum_number_of_panels']
    
    def get_efficiency_at_time(self, time):
        return self.parameter_dictionary['efficiency'].get_value_at_time(time)
    
    def get_cost_per_kw(self, time):
        return self.parameter_dictionary['cost_per_kw'].get_value_at_time(time)
    
    def get_term_in_months(self):
        return self.parameter_dictionary['term_in_months']
    
    def get_annual_interest_rate(self):
        return self.parameter_dictionary['annual_interest_rate']
            
    def get_recommended_quantity_at_time_index(self, index_of_current_time, load_profile, baseline_allocation, rate_schedule, consumption_bin, parameter_dictionary = None):
        key = (index_of_current_time, load_profile, baseline_allocation, rate_schedule, parameter_dictionary['solar_intensity_profile'])
        if key in self.parameter_dictionary['history_of_calculations'].keys():
            return self.parameter_dictionary['history_of_calculations'][key]
        cost_per_kw = self.parameter_dictionary['cost_per_kw']
        term_in_months = self.parameter_dictionary['term_in_months']
        annual_interest_rate = self.parameter_dictionary['annual_interest_rate']
        best_savings = 0
        best_technology = None
        current_month = index_of_current_time
        index_of_end_time = index_of_current_time + term_in_months        
        original_load_profile = load_profile.get_trace_over_time_index(index_of_current_time, index_of_end_time)        
        monthly_utility_bill = rate_schedule.calculate_monthly_charge(original_load_profile, baseline_allocation, current_month, term_in_months)
        original_net_present_value_of_utility_bill = self.calculate_net_present_value(monthly_utility_bill, annual_interest_rate)    
        technology_quantity = int(self.parameter_dictionary['consumptionBin_systemSize'][consumption_bin])
        for candidate_pv_technology in parameter_dictionary['pv_dictionary']:
            if  candidate_pv_technology is not None and  candidate_pv_technology.get_quantity() ==  technology_quantity:
                best_technology =  candidate_pv_technology
                quantity = best_technology.get_quantity()
                cost_of_pv = quantity * cost_per_kw.get_value_at_time_index(index_of_current_time)
                reduction_in_load = best_technology.get_reduction_in_load_over_time_index(index_of_current_time, index_of_end_time, parameter_dictionary)    
                new_load_profile = original_load_profile - reduction_in_load
                monthly_utility_bill = rate_schedule.calculate_monthly_charge(new_load_profile, baseline_allocation, current_month, term_in_months)
                new_net_present_value_of_utility_bill = self.calculate_net_present_value(monthly_utility_bill, annual_interest_rate)
                best_savings = original_net_present_value_of_utility_bill - new_net_present_value_of_utility_bill - cost_of_pv
            
        recommendation = (best_technology, best_savings, original_net_present_value_of_utility_bill)
        self.parameter_dictionary['history_of_calculations'][key] = recommendation
        return recommendation
    
        