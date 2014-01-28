'''
Created on Apr 29, 2013

@author: desmond cai

'''

'''
This module contains classes that define the agent objects in the SCE model

'''

import sce_settings
import copy
from sim_structure import Agent
from sce_non_agent_specs import CustomerCategoryAccount, Trace, TierNetMeterRateSchedule
import logging
import logging.config
import yaml
import time
import random
import math

class SimulatorClock(Agent):
    """
    A class for keeping track of the time interval corresponding to each step of the simulator.
    There should only be one instance of a SimulatorClock in the simulator.
    Each step of the simulator models the behavior that occurs over the time interval
    (sce_settings.TICK_VALUES[index_of_start_time_of_current_step], sce_settings.TICK_VALUES[index_of_end_time_of_current_step])
    In this version of the simulator, each step corresponds to one month in time.
    
    Attributes
    ----------
    name : string
    month_of_next_step : integer
    index_of_start_time_of_current_step : float
    index_of_end_time_of_current_step : float
    
    Read Variables
    --------------
    (no read variables)
    
    Write Variables
    ---------------
    index_of_start_time_of_current_step : float
    index_of_end_time_of_current_step : float
    
    """
    
    def __init__(self, name, simulator, parameter_dictionary = None):
        super(SimulatorClock,self).__init__(name, simulator)
        # read parameters and set initial state
        self.month_of_current_step = 1
        self.index_of_start_time_of_current_step = 1
        self.index_of_end_time_of_current_step = 2
#         self.index_of_end_time_of_current_step = 12
        # create write variables
        self.create_write_variable('index_of_start_time_of_current_step')
        self.create_write_variable('index_of_end_time_of_current_step')
        # initialize write variables
        self.write('index_of_start_time_of_current_step', self.index_of_start_time_of_current_step)
        self.write('index_of_end_time_of_current_step', self.index_of_end_time_of_current_step)
        
    def step_forward(self):
        self.month_of_current_step += 1
#         self.month_of_current_step = (self.month_of_current_step + 12) if self.month_of_current_step > 1 else 12
        self.index_of_start_time_of_current_step = self.index_of_end_time_of_current_step
        self.index_of_end_time_of_current_step = self.index_of_start_time_of_current_step + 1
#         self.index_of_end_time_of_current_step = self.index_of_start_time_of_current_step + 12
        self.write('index_of_start_time_of_current_step', self.index_of_start_time_of_current_step)
        self.write('index_of_end_time_of_current_step', self.index_of_end_time_of_current_step)


class ResidentialCustomerCategory(Agent):
    """
    A class for a residential customer.
    
    Attributes
    ----------
    customer_category_name : string
    number_of_customers: integer
    consumption_profile : TimeTrace
    solar_intensity_profile : TimeTrace
    name_of_rate_schedule : string
    pv_dictionary : dictionary of (PvTechnology, number of customers with this PvTechnology)
    pv_installer : PvInstaller
    name_of_baseline_region: string
    
    Read Variables
    --------------
    index_of_start_time_of_current_step : float
    index_of_end_time_of_current_step : float
    baseline_allocation : TimeTrace
    rate_schedule_dictionary : dictionary of RateSchedule
    number_of_pv_installations : int
    number_of_households_in_pv_market : int
    
    Write Variables
    ---------------
    dictionary_of_load_profile_in_current_step : dictionary of (PvTechnology, (TimeTrace, number of customers with this load profile))
    rate_schedule_in_current_step : string

    """
    
    def __init__(self, name, simulator, parameter_dictionary):
        super(ResidentialCustomerCategory,self).__init__(name, simulator, parameter_dictionary)    
        number_of_customers = 0
        pv_technology_options = self.parameter_dictionary['pv_dictionary']
        self.parameter_dictionary['pv_dictionary'] = dict()
        self.parameter_dictionary['pv_dictionary'][None] = self.parameter_dictionary['number_of_customers']
        
        category_bin = int(float(self.get_middle_text(name, 'Consumption:Bin', '<')))
        relevant_pv_tech = self.parameter_dictionary['consumptionBin_systemSize'][category_bin]
        for pv_technology in pv_technology_options.keys():
            if int(pv_technology.get_quantity()) == relevant_pv_tech:
                self.parameter_dictionary['pv_dictionary'][pv_technology] = self.parameter_dictionary['initial_category_adopters']
            else:
                self.parameter_dictionary['pv_dictionary'][pv_technology] = 0
                
        # create read variables
        self.create_read_variable('index_of_start_time_of_current_step')
        self.create_read_variable('index_of_end_time_of_current_step')
        self.create_read_variable('baseline_allocation')
        self.create_read_variable('rate_schedule_dictionary')
        
        # need to fix this part if there are multiple technology installers
        self.create_read_variable('number_of_pv_installations')
        self.create_read_variable('number_of_households_in_pv_market')
        
        # create write variables
        self.create_write_variable('dictionary_of_load_profile_in_current_step', None)
        self.create_write_variable('number_of_customers_with_pv', self.parameter_dictionary['initial_category_adopters'])
        self.create_write_variable('number_of_customers_in_market_for_pv', self.parameter_dictionary['initial_category_adopters'])
        
        # initialize write variables
        index_of_start_time_of_current_step = 0
        index_of_end_time_of_current_step = 1
        consumption_profile = self.parameter_dictionary['consumption_profile'].get_trace_over_time_index(index_of_start_time_of_current_step, index_of_end_time_of_current_step)
        dictionary_of_load_profile_in_current_step = dict()
        for pv_technology, number_of_customers in self.parameter_dictionary['pv_dictionary'].iteritems():
            if pv_technology is not None:
                reduction_in_load_profile = self.get_reduction_in_load_profile_over_time_index(pv_technology, index_of_start_time_of_current_step, index_of_end_time_of_current_step)
            else:
                reduction_in_load_profile = Trace([0] * (index_of_end_time_of_current_step - index_of_start_time_of_current_step), index_of_start_time_of_current_step)
            net_load_profile = consumption_profile - reduction_in_load_profile
            dictionary_of_load_profile_in_current_step[pv_technology] = (net_load_profile, number_of_customers)
        self.write('dictionary_of_load_profile_in_current_step', dictionary_of_load_profile_in_current_step)
    
    def get_middle_text(self, line, string_start, string_end):
        temp = line.split(string_start)[1]
        return temp.split(string_end)[0]
         
    @classmethod
    def parse_yaml(cls, specs, simulator, consumption_profile_dictionary, solar_intensity_profile_dictionary, pv_installer_dictionary, pv_dictionary):
        return ResidentialCustomerCategory(specs['parameter_dictionary']['customer_category_name'], simulator,
                                        {'customer_category_name': specs['parameter_dictionary']['customer_category_name'],
                                         'number_of_customers': specs['parameter_dictionary']['number_of_customers'],
                                         'consumption_profile': consumption_profile_dictionary[specs['parameter_dictionary']['consumption_profile']],
                                         'solar_intensity_profile': solar_intensity_profile_dictionary[specs['parameter_dictionary']['solar_intensity_profile']],
                                         'name_of_rate_schedule': specs['parameter_dictionary']['name_of_rate_schedule'],
                                         'pv_installer': pv_installer_dictionary[specs['parameter_dictionary']['pv_installer']],
                                         'pv_dictionary': pv_dictionary,
                                         'model_type': specs['parameter_dictionary']['model_type'],
                                         'adoption_parameter_pClassic': specs['parameter_dictionary']['adoption_parameter_pClassic'],
                                         'adoption_parameter_qClassic': specs['parameter_dictionary']['adoption_parameter_qClassic'],
                                         'adoption_parameter_bClassic': specs['parameter_dictionary']['adoption_parameter_bClassic'],
                                         'adoption_parameter_p_bin_1': specs['parameter_dictionary']['adoption_parameter_p_bin_1'], 
                                         'adoption_parameter_q_bin_1': specs['parameter_dictionary']['adoption_parameter_q_bin_1'],
                                         'adoption_parameter_p_bin_2': specs['parameter_dictionary']['adoption_parameter_p_bin_2'], 
                                         'adoption_parameter_q_bin_2': specs['parameter_dictionary']['adoption_parameter_q_bin_2'], 
                                         'adoption_parameter_p_bin_3': specs['parameter_dictionary']['adoption_parameter_p_bin_3'], 
                                         'adoption_parameter_q_bin_3': specs['parameter_dictionary']['adoption_parameter_q_bin_3'],  
                                         'name_of_baseline_region': specs['parameter_dictionary']['name_of_baseline_region'],
                                         'initial_category_adopters': specs['parameter_dictionary']['initial_category_adopters'],
                                         'initial_total_adopters': specs['parameter_dictionary']['initial_total_adopters'],
                                         'total_population': specs['parameter_dictionary']['total_population'],
                                         'shading_assumption': specs['parameter_dictionary']['shading_assumption'],
                                         'consumptionBin_systemSize': specs['parameter_dictionary']['consumptionBin_systemSize']})
                                         
    def get_customer_category_name(self):
        return self.parameter_dictionary['customer_category_name']
    
    def get_number_of_customers(self):
        return self.parameter_dictionary['number_of_customers']
    
    def get_consumption_profile(self):
        return self.parameter_dictionary['consumption_profile']
    
    def get_solar_profile(self):
        return self.parameter_dictionary['solar_intensity_profile']
    
    def get_name_of_rate_schedule(self):
        return self.parameter_dictionary['name_of_rate_schedule']
    
    def get_technology_dictionary(self):
        return self.parameter_dictionary['technology_dictionary']
        
    def get_name_of_baseline_region(self):
        return self.parameter_dictionary['name_of_baseline_region']
    
    def log(self, load_profile_dict):
        pv_dict = {}
        for key, value in self.parameter_dictionary['pv_dictionary'].iteritems():
            if key == None:
                pv_dict[None] = value    
            else:
                pv_dict[key.get_quantity()] = value
                
        load_dict = {}
        for key, value in load_profile_dict.iteritems():
               load_profile = value[0].get_list_of_values()
               num_of_cust = value[1]
               savings = value[2]
               if key == None:
                   load_dict[None] = (load_profile, num_of_cust, savings)
               else:
                   load_dict[key.get_quantity()] = (load_profile, num_of_cust, savings)
         
        # Write to Logfile 
        self.agent_customer_logger = logging.getLogger('customerLogger')      
        self.agent_customer_logger.info(' '.join('customer_category_name: %s, \
                            start_time_of_current_step: %f, \
                            number_of_customers: %d, \
                            pv_dictionary: %s, \
                            dictionary_of_load_profile_in_current_step: [%s], \
                            number_of_pv_adopters: %d, \
                            number_of_customers_in_market_for_pv: %d, \
                            name_of_rate_schedule_in_current_step: %s\n'.split()) % 
                            (self.parameter_dictionary['customer_category_name'], 
                             self.read('index_of_start_time_of_current_step') - 1, 
                             self.parameter_dictionary['number_of_customers'],
                             pv_dict,
                             load_dict, 
                             self.number_of_pv_adopters,
                             self.number_of_customers_in_market_for_pv,
                             self.parameter_dictionary['name_of_rate_schedule']))
                             
        # Write to Datastore               
        temp_dict = {}   
        start_time_of_current_step = self.read('index_of_start_time_of_current_step') 
        customer_category_name = self.parameter_dictionary['customer_category_name']
        temp_dict['customer_log_number_of_customers'] = self.parameter_dictionary['number_of_customers']
        temp_dict['customer_log_number_of_pv_adopters'] = float(self.number_of_pv_adopters)
        temp_dict['customer_log_number_of_customers_in_market_for_pv'] = float(self.number_of_customers_in_market_for_pv)
        temp_dict['customer_log_name_of_rate_schedule_in_current_step'] = self.parameter_dictionary['name_of_rate_schedule']
        temp_dict['customer_log_pv_dictionary'] = pv_dict
        temp_dict['customer_log_dictionary_of_load_profile_in_current_step'] = load_dict
        
        if start_time_of_current_step not in sce_settings.dict_customer_log:  
             sce_settings.dict_customer_log[start_time_of_current_step] = {customer_category_name: [temp_dict]}
        else:
            if customer_category_name not in sce_settings.dict_customer_log[start_time_of_current_step].keys():
                sce_settings.dict_customer_log[start_time_of_current_step][customer_category_name] = [temp_dict]
            else:
                sce_settings.dict_customer_log[start_time_of_current_step][customer_category_name].append(temp_dict)
                                                         
    def step_forward(self):
            index_of_start_time_of_current_step = self.read('index_of_start_time_of_current_step')
            index_of_end_time_of_current_step = self.read('index_of_end_time_of_current_step')
            
            current_number_of_adopters = self.read('total_number_of_pv_installations')
            number_of_households_in_pv_market = self.read('number_of_households_in_pv_market')
            savings = self._adopt_technology_at_time_index(index_of_start_time_of_current_step, current_number_of_adopters, number_of_households_in_pv_market)
            
            consumption_profile_in_current_step = self.parameter_dictionary['consumption_profile'].get_trace_over_time_index(index_of_start_time_of_current_step, index_of_end_time_of_current_step)
            dictionary_of_load_profile_in_current_step = dict()
            for pv_technology, number_of_customers in self.parameter_dictionary['pv_dictionary'].iteritems():
                if pv_technology is not None:
                    reduction_in_load_profile = self.get_reduction_in_load_profile_over_time_index(pv_technology, index_of_start_time_of_current_step, index_of_end_time_of_current_step)
                else:
                    reduction_in_load_profile = Trace([0] * (index_of_end_time_of_current_step - index_of_start_time_of_current_step), index_of_start_time_of_current_step)
                net_load_profile = consumption_profile_in_current_step - reduction_in_load_profile
                dictionary_of_load_profile_in_current_step[pv_technology] = (net_load_profile, number_of_customers, savings)
            
            self.write('dictionary_of_load_profile_in_current_step', dictionary_of_load_profile_in_current_step)
            # log load profile of customer in step - log level info
            self.log(dictionary_of_load_profile_in_current_step)
                                
    def get_reduction_in_load_profile_over_time_index(self, pv_technology, index_of_start_time, index_of_end_time):
        reduction_in_load_profile = pv_technology.get_reduction_in_load_over_time_index(index_of_start_time, index_of_end_time, self.parameter_dictionary)
        return reduction_in_load_profile
    
    def get_savings_bin(self, savings):
        num_bins = 8.0
        max_bin_savings = 30000.0
        if savings > 0.0:
             bin = math.ceil(num_bins/ (max_bin_savings / savings))
             if bin > num_bins - 1:
                temp_bin = num_bins
             else:
                temp_bin = bin
        else:
            temp_bin = -1.0
        
        if temp_bin in [-1.0, 1.0, 2.0]:
            return 1
        elif temp_bin in [3.0, 4.0, 5.0, 6.0]:
            return 2
        else:
            return 3
            
    def get_P_Q_vals(self, savingsBin):
        if savingsBin == 1:
            return self.parameter_dictionary['adoption_parameter_p_bin_1'], self.parameter_dictionary['adoption_parameter_q_bin_1']
        elif savingsBin == 2:
            return self.parameter_dictionary['adoption_parameter_p_bin_2'], self.parameter_dictionary['adoption_parameter_q_bin_2']
        else:
            return self.parameter_dictionary['adoption_parameter_p_bin_3'], self.parameter_dictionary['adoption_parameter_q_bin_3']
            
    def get_middle_text(self, line, string_start, string_end):
        temp = line.split(string_start)[1]
        return temp.split(string_end)[0]
    
    def _adopt_technology_at_time_index(self, index_of_current_time, current_number_of_adopters, number_of_households_in_pv_market):
        load_profile = self.parameter_dictionary['consumption_profile']
        baseline_allocation = self.read('baseline_allocation')
        rate_schedule = self.read('rate_schedule_dictionary')[('utility', self.parameter_dictionary['name_of_rate_schedule'])]
        consumption_category = self.parameter_dictionary['customer_category_name']
        consumption_bin = float(self.get_middle_text(consumption_category, 'Consumption:Bin', '<'))
        (technology, savings, original_net_present_value_of_utility_bill) = self.parameter_dictionary['pv_installer'].get_recommended_quantity_at_time_index(index_of_current_time, load_profile, baseline_allocation, rate_schedule, consumption_bin, self.parameter_dictionary)
        if savings > 0:
                    P_fit = self.parameter_dictionary['adoption_parameter_pClassic']
                    Q_fit = self.parameter_dictionary['adoption_parameter_qClassic']
                    B_fit = self.parameter_dictionary['adoption_parameter_bClassic']
                    initial_adopters = self.parameter_dictionary['initial_total_adopters']
                    total_population = self.parameter_dictionary['total_population']

                    if self.parameter_dictionary['model_type'].lower() == 'Classic Bass Model With Savings'.lower():
                        savingsBin = self.get_savings_bin(savings)
                        P_fit, Q_fit = self.get_P_Q_vals(savingsBin)
                        probability = (P_fit + (Q_fit) * (float(current_number_of_adopters) / (total_population * 0.3)))
                        
                    if self.parameter_dictionary['model_type'].lower() == 'Classic Bass Model'.lower():
                        probability = (P_fit + (Q_fit) * (float(current_number_of_adopters) / (total_population * 0.3)))
                    
                    if self.parameter_dictionary['model_type'].lower() == 'Bass Model With Savings'.lower():
                        probability = (P_fit + (Q_fit) * (float(current_number_of_adopters) / (total_population * 0.3))) * ((B_fit * savings) / math.sqrt(1 + math.pow(B_fit * savings, 2)))   
                    
                    number_of_adopters = round(probability * self.parameter_dictionary['pv_dictionary'][None])
                    current_pv_adopters = 0
                    for pv_technology, number_of_customers in self.parameter_dictionary['pv_dictionary'].iteritems():
                        if pv_technology is not None:
                            current_pv_adopters += number_of_customers
                    
                    number_of_eligible_customers = self.get_number_of_customers() * self.parameter_dictionary['shading_assumption']       
                    if current_pv_adopters + number_of_adopters > number_of_eligible_customers:
                            number_of_adopters = max(number_of_eligible_customers - current_pv_adopters, 0)
                        
                    self.parameter_dictionary['pv_dictionary'][technology] += number_of_adopters
                    self.parameter_dictionary['pv_dictionary'][None] -= number_of_adopters
                    number_of_pv_adopters = 0
                    for pv_technology, number_of_customers in self.parameter_dictionary['pv_dictionary'].iteritems():
                        if pv_technology is not None:
                            number_of_pv_adopters += number_of_customers
                    self.write('number_of_customers_with_pv', number_of_pv_adopters)            
                    self.write('number_of_customers_in_market_for_pv', number_of_pv_adopters + self.parameter_dictionary['pv_dictionary'][None])
                    self.number_of_pv_adopters = number_of_pv_adopters
                    self.number_of_customers_in_market_for_pv = number_of_pv_adopters + self.parameter_dictionary['pv_dictionary'][None]
        else:
                    number_of_pv_adopters = 0
                    for pv_technology, number_of_customers in self.parameter_dictionary['pv_dictionary'].iteritems():
                        if pv_technology is not None:
                            number_of_pv_adopters += number_of_customers
                    self.write('number_of_customers_with_pv', number_of_pv_adopters)            
                    self.write('number_of_customers_in_market_for_pv', number_of_pv_adopters)
                    self.number_of_pv_adopters = number_of_pv_adopters
                    self.number_of_customers_in_market_for_pv = number_of_pv_adopters 
        
        return savings
        
class Utility(Agent):
    """
    A class for a utility company.
    
    Attributes
    ----------
    baseline_as_percentage_of_aggregate_usage : float
    delivery_revenue_requirement_per_year : float
    generation_revenue_requirement_per_kwh : float
    customer_category_account_dictionary : dictionary of CustomerCategoryAccount
    rate_schedule_dictionary : dictionary of RateSchedule
    baseline_region_dictionary : dictionary of BaselineRegion
    
    Read Variables
    --------------
    index_of_start_time_of_current_step : float
    index_of_end_time_of_current_step : float
    customer_current_load_profile_dictionary : dictionary (customer category name, dictionary of (load profile, number of customers))
    
    Write Variables
    ---------------
    (one RateSchedule write variable for each rate schedule)
    (one TimeTrace write variable for the baseline allocation of each baseline region)
        
    """

    def __init__(self, name, simulator, parameter_dictionary):
        super(Utility,self).__init__(name, simulator)
        self.parameter_dictionary = parameter_dictionary
        # read parameters and set initial state
        self.customer_category_account_dictionary = dict()
        self.rate_schedule_dictionary = dict()
        self.baseline_region_dictionary = dict()
        # create read variables
        self.create_read_variable('index_of_start_time_of_current_step')
        self.create_read_variable('index_of_end_time_of_current_step')
        self.create_read_variable('customer_current_load_profile_dictionary')
        # no write variables to create during initialization    
    
    @classmethod
    def parse_yaml(cls, specs, simulator):
        return Utility(specs['name'], simulator, specs['parameter_dictionary']) 
    
    def get_customer_category_account(self, customer_category_name):
        return self.customer_category_account_dictionary[customer_category_name]
    
    def get_rate_schedule(self, rate_schedule_name):
        return self.rate_schedule_dictionary[rate_schedule_name]
    
    def get_baseline_region(self, baseline_region_name):
        return self.baseline_region_dictionary[baseline_region_name]
    
    def add_customer_category(self, customer_category_agent, baseline_region_name):
        customer_category_name = customer_category_agent.get_customer_category_name()
        rate_schedule_name = customer_category_agent.get_name_of_rate_schedule()
        number_of_customers = customer_category_agent.get_number_of_customers()
        customer_category_account = CustomerCategoryAccount(customer_category_name, number_of_customers,
                                           baseline_region = self.baseline_region_dictionary[baseline_region_name], 
                                           current_rate_schedule = self.rate_schedule_dictionary[rate_schedule_name])
        self.customer_category_account_dictionary[customer_category_name] = customer_category_account
        self.baseline_region_dictionary[baseline_region_name].add_customer_category_account(customer_category_account)
        
    def add_rate_schedule(self, rate_schedule):
        self.rate_schedule_dictionary[rate_schedule.get_name()] = rate_schedule
        self.create_write_variable(rate_schedule.get_name(), copy.copy(rate_schedule))
    
    def add_baseline_region(self, baseline_region):
        self.baseline_region_dictionary[baseline_region.get_name()] = baseline_region
        self.create_write_variable(baseline_region.get_name(), copy.copy(baseline_region.get_baseline_allocation()))
    
    def step_forward(self):
        # read clock
        index_of_start_time_of_current_step = self.read('index_of_start_time_of_current_step')
        # read customer profiles and rate schedule decisions
        for (customer_category_agent_name,customer_category_agent_write_variable), dictionary_of_load_profile_in_current_step in self.read('customer_current_load_profile_dictionary').iteritems():
            # log and append bill to each customer's bill_history 
            self.customer_category_account_dictionary[customer_category_agent_name].add_load_profile(dictionary_of_load_profile_in_current_step, index_of_start_time_of_current_step)
        # every three years, update rate schedules and baseline allocations
        month_of_current_step = index_of_start_time_of_current_step
        year_multiplier = self.parameter_dictionary['years_between_rate_revisions']
        if ( month_of_current_step % 12 * year_multiplier) == 0 and month_of_current_step >= 12 * year_multiplier:
            self._update_rate_schedules(month_of_current_step, month_of_current_step - 12, 12)
            self._update_baseline_allocations(month_of_current_step, month_of_current_step - 12, 12)
        # update all rate schedules
        for rate_schedule_name, rate_schedule in self.rate_schedule_dictionary.iteritems():
            self.write(rate_schedule_name, copy.copy(rate_schedule))
        # update all baseline allocations
        for baseline_region_name, baseline_region in self.baseline_region_dictionary.iteritems():
            self.write(baseline_region_name, copy.copy(baseline_region.get_baseline_allocation()))
    
    def _update_rate_schedules(self, current_month, reference_start_month, reference_number_of_months):
        # Find year of rate revision
        year = int(math.floor(float(current_month) / 12)) 
        rate_schedule_calculations = dict()
        for rate_schedule in self.rate_schedule_dictionary.values():
            if type(rate_schedule) == TierNetMeterRateSchedule:
                rate_schedule_calculations[rate_schedule.get_name()] = {'total_usage': 0, 'total_tiered_usage': [0, 0, 0, 0, 0], 'total_basic_charge': 0}
        for customer_category_account in self.customer_category_account_dictionary.values():
            rate_schedule = customer_category_account.get_current_rate_schedule()
            if type(rate_schedule) == TierNetMeterRateSchedule:
                rate_schedule_calculations[rate_schedule.get_name()]['total_usage'] += customer_category_account.get_total_usage(reference_start_month, reference_number_of_months)
                bill_history = customer_category_account.get_bill_history()
                for m in range(reference_start_month, reference_start_month + reference_number_of_months):
                    for v in bill_history[m].itervalues():
                        rate_schedule_calculations[rate_schedule.get_name()]['total_tiered_usage'] = [(x * v[1]) + y for (x,y) in zip(v[0].get_units_of_tiered_variable_charge(),rate_schedule_calculations[rate_schedule.get_name()]['total_tiered_usage'])]
                        rate_schedule_calculations[rate_schedule.get_name()]['total_basic_charge'] = rate_schedule_calculations[rate_schedule.get_name()]['total_basic_charge'] + v[0].get_basic_charge() * v[1]
        total_usage = 0
        for rate_schedule_name, calculation in rate_schedule_calculations.iteritems():
            total_usage += calculation['total_usage']
            ratio_flag = self.rate_schedule_dictionary[rate_schedule_name].is_ratio()
            number_of_tiers = self.rate_schedule_dictionary[rate_schedule_name].get_number_of_tiers()
        
        # Get delivery_revenue_requirement from list of annual revenue requirements inputted by user
        delivery_revenue_requirement = self.parameter_dictionary['delivery_revenue_requirement_per_year'][year]
        generation_revenue_requirement_per_kwh = self.parameter_dictionary['generation_revenue_requirement_per_kwh']
        total_revenue_requirement = delivery_revenue_requirement + generation_revenue_requirement_per_kwh * total_usage
        
        if ratio_flag:
            CARE = 0
            for rate_schedule_name, calculation in rate_schedule_calculations.iteritems():
                if self.rate_schedule_dictionary[rate_schedule_name].is_CARE():
                    tiered_variable_charge_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                    rate_update_rules_dictionary_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                    usage_CARE = calculation['total_tiered_usage']
                    CARE = 1
                    total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
                else:
                    tiered_variable_charge_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                    rate_update_rules_dictionary_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                    usage_NONCARE = calculation['total_tiered_usage']
                    total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
            if CARE == 0:
                usage_CARE = [0, 0, 0, 0, 0]
            units_of_T1_NONCARE = usage_NONCARE[0] + usage_CARE[0] * rate_update_rules_dictionary_CARE['T1_CARE_discount'] \
                                + ( usage_NONCARE[1] + usage_CARE[1] * rate_update_rules_dictionary_CARE['T2_CARE_discount'] ) * rate_update_rules_dictionary_NONCARE['T2_T1_ratio'] \
                                + ( usage_NONCARE[2] + usage_CARE[2] * rate_update_rules_dictionary_CARE['T3_CARE_discount'] + usage_CARE[3] * rate_update_rules_dictionary_CARE['T4_CARE_discount'] + usage_CARE[4] * rate_update_rules_dictionary_CARE['T5_CARE_discount'] ) * rate_update_rules_dictionary_NONCARE['T3_T1_ratio'] \
                                + ( usage_NONCARE[3] ) * rate_update_rules_dictionary_NONCARE['T4_T1_ratio'] \
                                + ( usage_NONCARE[4] ) * rate_update_rules_dictionary_NONCARE['T5_T1_ratio']
            tiered_variable_charge_NONCARE = [tiered_variable_charge_NONCARE[0], tiered_variable_charge_NONCARE[1], 0, 0, 0]
            tiered_variable_charge_NONCARE[0][year] = total_revenue_requirement / units_of_T1_NONCARE
            tiered_variable_charge_NONCARE[1][year] = tiered_variable_charge_NONCARE[0][year] * rate_update_rules_dictionary_NONCARE['T2_T1_ratio']
            tiered_variable_charge_NONCARE[2] = tiered_variable_charge_NONCARE[0][year] * rate_update_rules_dictionary_NONCARE['T3_T1_ratio']
            tiered_variable_charge_NONCARE[3] = tiered_variable_charge_NONCARE[0][year] * rate_update_rules_dictionary_NONCARE['T4_T1_ratio']
            tiered_variable_charge_NONCARE[4] = tiered_variable_charge_NONCARE[0][year] * rate_update_rules_dictionary_NONCARE['T5_T1_ratio']
            tiered_variable_charge_CARE = [tiered_variable_charge_CARE[0], tiered_variable_charge_CARE[1], 0, 0, 0]
            tiered_variable_charge_CARE[0][year] = tiered_variable_charge_NONCARE[0][year] * rate_update_rules_dictionary_NONCARE['T1_CARE_discount']
            tiered_variable_charge_CARE[1][year] = tiered_variable_charge_NONCARE[1][year] * rate_update_rules_dictionary_NONCARE['T2_CARE_discount']
            tiered_variable_charge_CARE[2] = tiered_variable_charge_NONCARE[2] * rate_update_rules_dictionary_NONCARE['T3_CARE_discount']
            tiered_variable_charge_CARE[3] = tiered_variable_charge_NONCARE[2] * rate_update_rules_dictionary_NONCARE['T4_CARE_discount']
            tiered_variable_charge_CARE[4] = tiered_variable_charge_NONCARE[2] * rate_update_rules_dictionary_NONCARE['T5_CARE_discount']            
        else:
            if number_of_tiers == 1:
                CARE = 0
                for rate_schedule_name, calculation in rate_schedule_calculations.iteritems():
                    if self.rate_schedule_dictionary[rate_schedule_name].is_CARE():
                        rate_update_rules_dictionary_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                        tiered_variable_charge_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                        usage_CARE = calculation['total_tiered_usage']
                        CARE = 1
                        total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
                    else:
                        rate_update_rules_dictionary_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                        tiered_variable_charge_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                        usage_NONCARE = calculation['total_tiered_usage']
                        total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
                if CARE == 0:
                    usage_CARE = [0, 0, 0, 0, 0]
                    tiered_variable_charge_CARE = [tiered_variable_charge_CARE[0], 0, 0, 0, 0]
                units_of_T1_NONCARE = usage_CARE[0] * rate_update_rules_dictionary_CARE['T1_CARE_discount'] \
                                      + usage_CARE[1] * rate_update_rules_dictionary_CARE['T1_CARE_discount'] \
                                      + usage_CARE[2] * rate_update_rules_dictionary_CARE['T1_CARE_discount'] \
                                      + usage_CARE[3] * rate_update_rules_dictionary_CARE['T1_CARE_discount'] \
                                      + usage_CARE[4] * rate_update_rules_dictionary_CARE['T1_CARE_discount'] \
                                      + usage_NONCARE[0] \
                                      + usage_NONCARE[1] \
                                      + usage_NONCARE[2] \
                                      + usage_NONCARE[3] \
                                      + usage_NONCARE[4]
                tiered_variable_charge_NONCARE[0][year::] = [total_revenue_requirement / units_of_T1_NONCARE] * len(tiered_variable_charge_NONCARE[0][year::])
                tiered_variable_charge_NONCARE[1][year::] = [total_revenue_requirement / units_of_T1_NONCARE] * len(tiered_variable_charge_NONCARE[1][year::])
                tiered_variable_charge_NONCARE[2::] = [total_revenue_requirement / units_of_T1_NONCARE] * 3
                
                tiered_variable_charge_CARE[0][year::] = [tiered_variable_charge_NONCARE[0][year] * rate_update_rules_dictionary_CARE['T1_CARE_discount']] * len(tiered_variable_charge_CARE[0][year::])
                tiered_variable_charge_CARE[1][year::] = [tiered_variable_charge_NONCARE[0][year] * rate_update_rules_dictionary_CARE['T1_CARE_discount']] * len(tiered_variable_charge_CARE[0][year::])
                tiered_variable_charge_CARE[2::] = [tiered_variable_charge_NONCARE[0][year]* rate_update_rules_dictionary_CARE['T1_CARE_discount']] * 3          
            elif number_of_tiers == 2:
                CARE = 0
                for rate_schedule_name, calculation in rate_schedule_calculations.iteritems():
                    if self.rate_schedule_dictionary[rate_schedule_name].is_CARE():
                        rate_update_rules_dictionary_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                        tiered_variable_charge_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                        usage_CARE = calculation['total_tiered_usage']
                        total_revenue_requirement = total_revenue_requirement - tiered_variable_charge_CARE[0][year] * calculation['total_tiered_usage'][0]            
                        CARE = 1
                        total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
                    else:
                        rate_update_rules_dictionary_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                        tiered_variable_charge_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                        usage_NONCARE = calculation['total_tiered_usage']
                        total_revenue_requirement = total_revenue_requirement - tiered_variable_charge_NONCARE[0][year] * calculation['total_tiered_usage'][0]            
                        total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
                if CARE == 0:
                    usage_CARE = [0, 0, 0, 0, 0]
                    tiered_variable_charge_CARE = [tiered_variable_charge_NONCARE[0], 0, 0, 0, 0]
                units_of_T2_NONCARE = usage_CARE[1] * rate_update_rules_dictionary_CARE['T2_CARE_discount'] \
                                      + usage_CARE[2] * rate_update_rules_dictionary_CARE['T2_CARE_discount'] \
                                      + usage_CARE[3] * rate_update_rules_dictionary_CARE['T2_CARE_discount'] \
                                      + usage_CARE[4] * rate_update_rules_dictionary_CARE['T2_CARE_discount'] \
                                      + usage_NONCARE[1] \
                                      + usage_NONCARE[2] \
                                      + usage_NONCARE[3] \
                                      + usage_NONCARE[4]
                tiered_variable_charge_NONCARE[1][year::] = [total_revenue_requirement / units_of_T2_NONCARE] * len(tiered_variable_charge_NONCARE[1][year::])
                tiered_variable_charge_NONCARE[2::] = [total_revenue_requirement / units_of_T2_NONCARE] * 3
                tiered_variable_charge_CARE[1][year::] = [tiered_variable_charge_NONCARE[1][year] * rate_update_rules_dictionary_CARE['T2_CARE_discount']] * len(tiered_variable_charge_CARE[1][year::])
                tiered_variable_charge_CARE[2::] = [tiered_variable_charge_NONCARE[1][year]* rate_update_rules_dictionary_CARE['T2_CARE_discount']] * 3
            else:            
                CARE = 0
                tiered_variable_charge_CARE = []
                tiered_variable_charge_NONCARE = []
                units_of_T3_NONCARE = 0
                for rate_schedule_name, calculation in rate_schedule_calculations.iteritems():
                    if self.rate_schedule_dictionary[rate_schedule_name].is_CARE():
                        rate_update_rules_dictionary_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                        tiered_variable_charge_CARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                        usage_CARE = calculation['total_tiered_usage']
                        
                        total_revenue_requirement = total_revenue_requirement - tiered_variable_charge_CARE[0][year] * calculation['total_tiered_usage'][0] - tiered_variable_charge_CARE[1][year] * calculation['total_tiered_usage'][1]                
                        CARE = 1
                        total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
                    else:
                        rate_update_rules_dictionary_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_rate_update_rules_dictionary()
                        tiered_variable_charge_NONCARE = self.rate_schedule_dictionary[rate_schedule_name].get_tiered_variable_charge()[:]
                        usage_NONCARE = calculation['total_tiered_usage']
                        total_revenue_requirement = total_revenue_requirement - tiered_variable_charge_NONCARE[0][year] * calculation['total_tiered_usage'][0] - tiered_variable_charge_NONCARE[1][year] * calculation['total_tiered_usage'][1]                                
                        total_revenue_requirement = total_revenue_requirement - calculation['total_basic_charge']
                if CARE == 0:
                    usage_CARE = [0, 0, 0, 0, 0]
                    tiered_variable_charge_CARE = [tiered_variable_charge_NONCARE[0][year], tiered_variable_charge_NONCARE[1][year], 0, 0, 0]                                
                units_of_T3_NONCARE = units_of_T3_NONCARE + usage_CARE[2] * rate_update_rules_dictionary_CARE['T3_CARE_discount'] \
                                                          + usage_CARE[3] * rate_update_rules_dictionary_CARE['T4_CARE_discount'] \
                                                          + usage_CARE[4] * rate_update_rules_dictionary_CARE['T5_CARE_discount'] \
                                                          + usage_NONCARE[2] \
                                                          + usage_NONCARE[3] \
                                                          + usage_NONCARE[4]
                total_revenue_requirement = total_revenue_requirement - usage_NONCARE[3] * rate_update_rules_dictionary_NONCARE['T4_T3_delta'] \
                                                                      - usage_NONCARE[4] * ( rate_update_rules_dictionary_NONCARE['T5_T4_delta'] + rate_update_rules_dictionary_NONCARE['T4_T3_delta'] )
                tiered_variable_charge_NONCARE[2] =  total_revenue_requirement / units_of_T3_NONCARE
                tiered_variable_charge_NONCARE[3] = tiered_variable_charge_NONCARE[2] + rate_update_rules_dictionary_NONCARE['T4_T3_delta']
                tiered_variable_charge_NONCARE[4] = tiered_variable_charge_NONCARE[3] + rate_update_rules_dictionary_NONCARE['T5_T4_delta']
                tiered_variable_charge_CARE[2] = tiered_variable_charge_NONCARE[2] * rate_update_rules_dictionary_CARE['T3_CARE_discount']
                tiered_variable_charge_CARE[3] = tiered_variable_charge_NONCARE[2] * rate_update_rules_dictionary_CARE['T4_CARE_discount']
                tiered_variable_charge_CARE[4] = tiered_variable_charge_NONCARE[2] * rate_update_rules_dictionary_CARE['T5_CARE_discount']
            
        for rate_schedule_name, calculation in rate_schedule_calculations.iteritems():
            if self.rate_schedule_dictionary[rate_schedule_name].is_CARE():
                self.rate_schedule_dictionary[rate_schedule_name].set_tiered_variable_charge(tiered_variable_charge_CARE)
            else:
                self.rate_schedule_dictionary[rate_schedule_name].set_tiered_variable_charge(tiered_variable_charge_NONCARE)
            
    def _update_baseline_allocations(self, current_month, reference_start_month, reference_number_of_months):
        for baseline_region in self.baseline_region_dictionary.values():
            number_of_customers = 0
            for customer_category_account in baseline_region.get_customer_category_account_list():
                number_of_customers += customer_category_account.get_number_of_customers() 
            distribution_of_total_summer_usage = []
            for customer_category_account in baseline_region.get_customer_category_account_list():
                distribution_of_total_summer_usage.extend(customer_category_account.get_distribution_of_total_summer_usage(reference_start_month, reference_number_of_months))
            distribution_of_total_summer_usage.sort()
            target_baseline_coverage_of_daily_summer_usage = self.parameter_dictionary['baseline_as_percentage_of_aggregate_usage'] * sum([x[0]*x[1] for x in distribution_of_total_summer_usage])
            baseline_coverage = 0
            summer_baseline_in_kwh_per_day = 0
            number_of_customers_below_baseline = 0
            sorted_usage_iterator = iter(distribution_of_total_summer_usage)
            x = sorted_usage_iterator.next()
            while True:
                summer_baseline_in_kwh_per_day += 0.1
                while x[0] <= summer_baseline_in_kwh_per_day:
                    number_of_customers_below_baseline += x[1]
                    x = sorted_usage_iterator.next()
                baseline_coverage += 0.1 * ( number_of_customers - number_of_customers_below_baseline )
                if baseline_coverage >= target_baseline_coverage_of_daily_summer_usage:
                    break
            distribution_of_total_winter_usage = []
            for customer_category_account in baseline_region.get_customer_category_account_list():
                distribution_of_total_winter_usage.extend(customer_category_account.get_distribution_of_total_winter_usage(reference_start_month, reference_number_of_months))
            distribution_of_total_winter_usage.sort()
            target_baseline_coverage_of_daily_winter_usage = self.parameter_dictionary['baseline_as_percentage_of_aggregate_usage'] * sum([x[0]*x[1] for x in distribution_of_total_winter_usage])
            baseline_coverage = 0
            winter_baseline_in_kwh_per_day = 0
            number_of_customers_below_baseline = 0
            sorted_usage_iterator = iter(distribution_of_total_winter_usage)
            x = sorted_usage_iterator.next()
            while True:
                winter_baseline_in_kwh_per_day += 0.1
                while x[0] <= winter_baseline_in_kwh_per_day:
                    number_of_customers_below_baseline += x[1]
                    x = sorted_usage_iterator.next()
                baseline_coverage += 0.1 * ( number_of_customers - number_of_customers_below_baseline )
                if baseline_coverage >= target_baseline_coverage_of_daily_winter_usage:
                    break
            baseline_region.update_baseline_allocation(current_month + 1, summer_baseline_in_kwh_per_day, winter_baseline_in_kwh_per_day)
            