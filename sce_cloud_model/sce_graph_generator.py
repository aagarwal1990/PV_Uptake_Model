# parser for log files
import re
import collections 
import ast
import sce_simulation_init
import sce_test
import traceback, sys
import logging
import logging.config
from operator import itemgetter
import xlwt
 
test_parser = sce_simulation_init.specparser()
test_parser.main()
results_dict = sce_test.simulation_dct['test_ID']
category_names = test_parser.residential_customer_category_dictionary.keys()
pv_tech_sizes = test_parser.technology_size_lst 

def CreateExcelFromResults(results, categories, pvtechs):
    LOG_TUPLE = results
    DCT_CUSTOMER_LOG = LOG_TUPLE['customer_log_dict']
    DCT_UTILITY_LOG = LOG_TUPLE['utility_log_dict']
    CUSTOMER_TIERS = [1, 2, 3, 4]
    CATEGORY_NAMES = categories
    PV_TECH_SIZES = pvtechs
    correct_keys = DCT_CUSTOMER_LOG.keys()

    class graph(object):
       '''
       Choices a user gets to make:
            1. graph_type: sweep (multiple simulations) or time (plot two parameters for one simulation)
            2. operation: total, max, min, average, mode, median, cumulative
            3. y-axis 
            4. x-axis
            5. list of customer_category_names to plot (OPTIONAL)
            6. list of PVTechnology types to plot (OPTIONAL)
            7. list of tiers_of_customer to plot (OPTIONAL)
       '''
       def __init__(self, y_axis, x_axis, operation, lst_of_customer_category_names = CATEGORY_NAMES, lst_of_PVTech_types = PV_TECH_SIZES + [None], lst_of_tiers = CUSTOMER_TIERS, dict_customer_log = DCT_CUSTOMER_LOG, dict_utility_log = DCT_UTILITY_LOG):
            '''
                attributes:
                 number_of_customers: int
                 number_of_pv_adopters: int
                 number_of_customers_in_market_for_pv: int
                 name_of_rate_schedule_in_current_step: string
                 pv_dictionary : dictionary of (PvTechnology, number of customers with this PvTechnology)
                 dictionary_of_load_profile_in_current_step : dictionary of (PvTechnology, (TimeTrace, number of customers with this load profile))
     
                output:
                 'dict_customer_log = {time_step: {customer_category_name: [{attribute_dict}, ....], ....}, ....}'
            '''
        
        
            # Per customer_category & pv_tech_type
            self.dict_customer_log_keys = ['customer_log_number_of_pv_adopters', 
                                           'customer_log_number_of_customers_in_market_for_pv',
                                           'customer_log_load_profile']
        
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

            # Per customer category & pv_tech type
            self.dict_utility_log_keys = ['utility_log_number_of_customers', 
                                          'utility_log_usage', 
                                          'utility_log_cumulative_usage_charge_over_current_relevant_period', 
                                          'utility_log_cumulative_usage_over_current_relevant_period', 
                                          'utility_log_baseline_allocation_for_this_month', 
                                          'utility_log_units_of_basic_charge', 
                                          'utility_log_units_of_net_surplus_compensation', 
                                          'utility_log_total_basic_charge', 
                                          'utility_log_total_tiered_variable_charge', 
                                          'utility_log_total_net_surplus_compensation', 
                                          'utility_log_basic_charge', 
                                          'utility_log_net_surplus_compensation_rate',
                                          'utility_log_tiered_variable_charge',
                                          'utility_log_units_of_tiered_variable_charge',
                                          'utility_log_total_PV_kilowatts']
                                                              
            self.operation_keys = ['total', 'max', 'min', 'average', 'mode', 'median', 'cumulative']
        
            self.dict_customer_log = dict_customer_log
            self.dict_utility_log = dict_utility_log
    
            # pick y_axis parameter to graph
            if y_axis in self.dict_customer_log_keys:
                   self.y_axis_dict = self.dict_customer_log
                   self.y_axis = y_axis
            elif y_axis in self.dict_utility_log_keys:
                   self.y_axis_dict = self.dict_utility_log
                   self.y_axis = y_axis
            else:
                   print "!!!!!Error y_axis input not a valid parameter!!!!!\n"
        
            # pick x_axis parameter to graph       
            if x_axis in self.dict_customer_log_keys:
                   self.x_axis_dict = self.dict_customer_log
                   self.x_axis = x_axis
            elif x_axis in self.dict_utility_log_keys:
                   self.x_axis_dict = self.dict_utility_log
                   self.x_axis = x_axis
            elif x_axis == 'time':
                   self.x_axis_dict = self.y_axis_dict
                   self.x_axis = 'time'
            else:
                   print "!!!!!Error y_axis input not a valid parameter!!!!!\n" 
               
            if operation in self.operation_keys:
                   self.op = operation
            else:
                   print "!!!!!Error operator input not a valid parameter!!!!!\n"
               
            self.customer_category_lst = lst_of_customer_category_names
            self.PVTech_lst = lst_of_PVTech_types
            self.lst_of_tiers = lst_of_tiers
        
       def median_of_lst(self, lst):
            middle_number = len(lst) / 2
            if len(lst) % 2 is not 0:
                return lst[middle_number]
            else:
                return float(lst[middle_number - 1] + lst[middle_number]) / 2.0
               
       def list_operator(self, lst, operator, pop_count = 0):
           if operator is 'total':
               val = sum(lst)
           elif operator is 'max':
               val = max(lst)
           elif operator is 'min':
               val = min(lst)
           elif operator is 'max':
               val = max(lst)
           elif operator is 'average':
               if int(pop_count) is not 0:
                    val = sum(lst)/pop_count
               else:
                    val = 0
           elif operator is 'mode':
               val = collections.Counter(lst).most_common(1)[0][0]
           elif operator is 'cumulative':
                val = sum(lst)
           else:
               val = self.median_of_lst(lst)
           return val
       
       def cumulate_lst_of_tup(self, lst):
            res = [(lst[0][0], lst[0][1])]
            curr_value = lst[0][1]
            for i in range(1, len(lst)):
                curr_value += lst[i][1]
                res.append((lst[i][0], curr_value))
            return res 
        
       def lst_overlap(self, lst1, lst2):
            set1 = set(lst1)
            return any(el in set1 for el in lst2)
        
       def get_customer_category_tier(self, usage_lst):
           for tier in range(len(usage_lst)):
                if usage_lst[tier] == 0:
                    return tier 
           return len(usage_lst)
                 
    class time_graph(graph):
       def __init__(self, y_axis, x_axis, operation, lst_of_customer_category_names = CATEGORY_NAMES, lst_of_PVTech_types = PV_TECH_SIZES + [None], lst_of_tiers = CUSTOMER_TIERS, dict_customer_log = DCT_CUSTOMER_LOG, dict_utility_log = DCT_UTILITY_LOG):
           super(time_graph,self).__init__(y_axis, x_axis, operation, lst_of_customer_category_names, lst_of_PVTech_types, lst_of_tiers, dict_customer_log, dict_utility_log)
           if self.x_axis is not 'time':
                print 'ERROR !!!! x-axis needs to be time !!!!'
           self.graph_list_of_tups = []
       
       # parses one time_step of the customer_log_dct
       def parse_customer_log_key(self, time_step, customer_dct):
                temp_lst = []
                for category_name, attribute_dct_lst in customer_dct.iteritems():
                    # count only if customer_category appears in customer_category inputted
                    if category_name in self.customer_category_lst:
                        if self.y_axis == 'customer_log_number_of_customers_in_market_for_pv':
                            temp_lst.append(attribute_dct_lst[0][self.y_axis])
                        else:
                            if self.y_axis == 'customer_log_number_of_pv_adopters':
                                # count only if pv_tech appears in pv_tech_lst user inputs
                                for pv_tech, number_of_cust in attribute_dct_lst[0]['customer_log_pv_dictionary'].iteritems():
                                    if pv_tech in self.PVTech_lst and pv_tech is not None:
                                            temp_lst.append(number_of_cust)
                            # self.y_axis == 'load_profile'
                            else:
                                for pv_tech, (load_prof, num_cust) in attribute_dct_lst[0]['customer_log_dictionary_of_load_profile_in_current_step'].iteritems():
                                    if pv_tech in self.PVTech_lst:
                                        temp_lst.append(float(load_prof[0]) * float(num_cust))
                return self.list_operator(temp_lst, self.op)  
 
       # parses one time_step of the utility_log_dct           
       def parse_utility_log_key(self, time_step, utility_dct):
                    temp_lst = []
                    population_count = 0
                    for category_name, pv_dct in utility_dct.iteritems():
                        # count only if customer_category appears in customer_category inputted
                        if category_name in self.customer_category_lst:
                            # get tier for customer_category 
                            customer_category_tier = self.get_customer_category_tier(pv_dct[None][0]['utility_log_units_of_tiered_variable_charge'])
                            # count only if customer_category_tier is in list of tiers specified by user
                            if customer_category_tier in self.lst_of_tiers:
                                for pv_tech, attribute_dct_lst in pv_dct.iteritems():
                                    # count only if  pv_tech appears in pv_tech_lst user inputs
                                    if pv_tech in self.PVTech_lst:  
                                        if self.y_axis == 'utility_log_number_of_customers':
                                            temp_lst.append(attribute_dct_lst[0][self.y_axis])
                                        elif self.y_axis == 'utility_log_total_PV_kilowatts':
                                            if pv_tech is not None:
                                                temp_lst.append(pv_tech * attribute_dct_lst[0]['utility_log_number_of_customers'])
                                                population_count += attribute_dct_lst[0]['utility_log_number_of_customers']
                                        else:
                                            temp_lst.append(attribute_dct_lst[0][self.y_axis] * attribute_dct_lst[0]['utility_log_number_of_customers'])
                                            population_count += attribute_dct_lst[0]['utility_log_number_of_customers']
#                                             print category_name, attribute_dct_lst[0]['utility_log_number_of_customers'], population_count
                    return self.list_operator(temp_lst, self.op, population_count)     
                                                
       def main(self):
                    if self.y_axis_dict == self.dict_customer_log:
                          for time_step, customer_dct in self.dict_customer_log.iteritems():
                             res = self.parse_customer_log_key(time_step, customer_dct)
                             self.graph_list_of_tups.append((time_step, res))      
                    else:
                         for time_step, utility_dct in self.dict_utility_log.iteritems():
                             if self.y_axis == 'utility_log_tiered_variable_charge' or self.y_axis == 'utility_log_units_of_tiered_variable_charge':
                                    temp_lst = []
                                    pv_tech_dict = utility_dct[utility_dct.keys()[0]]
                                    attribute_dct_lst = pv_tech_dict[pv_tech_dict.keys()[0]]
                                    tiered_variable_charge_lst = attribute_dct_lst[0][self.y_axis]
                                    for i in self.lst_of_tiers:
                                        temp_lst.append(tiered_variable_charge_lst[i - 1])
                                    res =  self.list_operator(temp_lst, self.op)  
                             else:
                                    res = self.parse_utility_log_key(time_step, utility_dct)
                             self.graph_list_of_tups.append((time_step, res))
                    
                    self.graph_list_of_tups.sort()
                    if self.op == 'cumulative':
                        self.graph_list_of_tups = self.cumulate_lst_of_tup(self.graph_list_of_tups)
                                                                    
    class sweep_graph(graph):
       def __init__(self, y_axis, x_axis, operation, time_step, lst_of_customer_category_names = CATEGORY_NAMES, lst_of_PVTech_types = PV_TECH_SIZES + [None], lst_of_tiers = CUSTOMER_TIERS, dict_customer_log = DCT_CUSTOMER_LOG, dict_utility_log = DCT_UTILITY_LOG):
           super(sweep_graph,self).__init__(y_axis, x_axis, operation, lst_of_customer_category_names, lst_of_PVTech_types, lst_of_tiers, dict_customer_log, dict_utility_log)
           self.time_step = time_step
       
       # parses one time_step of the customer_log_dct
       def parse_customer_log_key(self, customer_dct, y_axis, x_axis):
                temp_dct = {}
                for category_name, attribute_dct_lst in customer_dct.iteritems():
                    # count only if customer_category appears in customer_category inputted
                    if category_name in self.customer_category_lst:
                       for attribute_dct in attribute_dct_lst:
                            if y_axis == 'customer_log_number_of_customers_in_market_for_pv':
                                    output_value = attribute_dct[y_axis]
                            else:
                                if y_axis == 'customer_log_number_of_pv_adopters':
                                    # count only if pv_tech appears in pv_tech_lst user inputs
                                    for pv_tech, number_of_cust in attribute_dct['customer_log_pv_dictionary'].iteritems():
                                        if pv_tech in self.PVTech_lst and pv_tech is not None:
                                                output_value = number_of_cust
                                # y_axis == 'load_profile'
                                else:
                                    for pv_tech, (load_prof, num_cust) in attribute_dct['customer_log_dictionary_of_load_profile_in_current_step'].iteritems():
                                        if pv_tech in self.PVTech_lst:
                                                output_value = float(load_prof[0]) * float(num_cust)
                                        
                            sweep_value = attribute_dct[x_axis] 
                            if sweep_value in temp_dct:
                                 temp_dct[sweep_value].append(output_value)
                            else:
                                 temp_dct[sweep_value] = [output_value]       
                return temp_dct
          
       # parses one time_step of the utility_log_dct           
       def parse_utility_log_key(self, utility_dct, y_axis, x_axis):
                    temp_dct = {}
                    for category_name, pv_dct in utility_dct.iteritems():
                        # count only if customer_category appears in customer_category inputted
                        if category_name in self.customer_category_lst:
                            # get tier for customer_category 
                            customer_category_tier = self.get_customer_category_tier(pv_dct[None][0]['utility_log_units_of_tiered_variable_charge'])
                            # count only if customer_category_tier is in list of tiers specified by user
                            if customer_category_tier in self.lst_of_tiers:
                                for pv_tech, attribute_dct_lst in pv_dct.iteritems():
                                    # count only if  pv_tech appears in pv_tech_lst user inputs
                                    if pv_tech in self.PVTech_lst:  
                                        for attribute_dct in attribute_dct_lst:
                                            if y_axis == 'utility_log_number_of_customers':
                                                output_value = attribute_dct[y_axis]
                                            elif y_axis == 'utility_log_total_PV_kilowatts':
                                                output_value = pv_tech * attribute_dct['utility_log_number_of_customers']
                                            elif y_axis == 'utility_log_tiered_variable_charge' or y_axis == 'utility_log_units_of_tiered_variable_charge':
                                                 tiered_variable_charge_lst = attribute_dct[y_axis]
                                                 output_value = 0
                                                 for i in self.lst_of_tiers:
                                                        output_value += tiered_variable_charge_lst[i - 1]
                                            else:
                                               output_value = attribute_dct[y_axis] * attribute_dct['utility_log_number_of_customers']
      
                                            if x_axis == 'utility_log_number_of_customers':
                                                sweep_value = attribute_dct[y_axis]
                                            elif x_axis == 'utility_log_total_PV_kilowatts':
                                                sweep_value = pv_tech * attribute_dct['utility_log_number_of_customers']
                                            elif x_axis == 'utility_log_tiered_variable_charge' or x_axis == 'utility_log_units_of_tiered_variable_charge':
                                                 tiered_variable_charge_lst = attribute_dct[x_axis]
                                                 sweep_value = 0
                                                 for i in self.lst_of_tiers:
                                                        sweep_value += tiered_variable_charge_lst[i - 1]
                                            else:
                                               print x_axis
                                               print attribute_dct[x_axis]
                                               sweep_value = attribute_dct[x_axis] * attribute_dct['utility_log_number_of_customers']
                                           
                                            if sweep_value in temp_dct:
                                                 temp_dct[sweep_value].append(output_value)
                                            else:
                                                 temp_dct[sweep_value] = [output_value]    
                                    
                                           
                    return temp_dct

       def main(self):
                    self.graph_list_of_tups = []
                    if self.y_axis_dict == self.dict_customer_log:
                        temp_dct = self.parse_customer_log_key(self.dict_customer_log[self.time_step], self.y_axis, self.x_axis)
                        for key, value in temp_dct.iteritems():
                             temp_dct[key] = self.list_operator(value, self.op)
                             self.graph_list_of_tups.append((key, temp_dct[key])) 
                    else:
                        temp_dct = self.parse_utility_log_key(self.dict_utility_log[self.time_step], self.y_axis, self.x_axis)
                        for key, value in temp_dct.iteritems():
                             temp_dct[key] = self.list_operator(value, self.op)
                             self.graph_list_of_tups.append((key, temp_dct[key]))  
                            
                    self.graph_list_of_tups.sort()


    # GENERATE GRAPHS
    # Create different filters for consumption & rates
    def get_middle_text(line, string_start, string_end):
        temp = line.split(string_start)[1]
        return temp.split(string_end)[0]
    
    category_by_consumption = {}
    category_by_rates = {}

    for consumption_category in CATEGORY_NAMES:
            household_tenure = get_middle_text(consumption_category, 'Tenure:', 'RateSchedule:')
            consumption_bin = get_middle_text(consumption_category, 'Consumption:', '<')
            rate = get_middle_text(consumption_category, 'RateSchedule:', 'Consumption:')
            # Create list of categories by consumption_bin
            if consumption_bin in category_by_consumption.keys():
                category_by_consumption[consumption_bin].append(consumption_category)
            else:
                category_by_consumption[consumption_bin] = [consumption_category]
            # Create list of categories by rate
            if rate in category_by_rates.keys():
                category_by_rates[rate].append(consumption_category)
            else:
                category_by_rates[rate] = [consumption_category]

    # Create list of categories by filter [(filter, categories) ....] 
    all_filters = [('All_Customers', CATEGORY_NAMES)]
    for k, v in category_by_consumption.iteritems():
        tup = (k, v)
        all_filters.append(tup)
    for k, v in category_by_rates.iteritems():
        tup = (k, v)
        all_filters.append(tup)
    for i in CUSTOMER_TIERS:
        tup = ('Tier' + str(i), 0)
        all_filters.append(tup)
                
    Tech_types = PV_TECH_SIZES
    
    def write_sorted_tups(lst_of_tups, col, arg_sheet):
        print_lst = [(x,y) for x, y in lst_of_tups if x in correct_keys]
        temp = sorted(print_lst,key=itemgetter(0))
        temp = [y for x, y in temp]
        row = 1
        for val in temp:
            arg_sheet.write(row, col, val)
            row += 1
            
    # Write Results into an Excel Sheet
    book = xlwt.Workbook(encoding="utf-8")
    
    # SetUp Adoption Sheet 
    adoption_sheet = book.add_sheet("Adoption_Numbers", cell_overwrite_ok=True)
    # Set time column in Adoption Sheet
    adoption_sheet.write(0, 0, "Time_Step")
    a = time_graph('utility_log_number_of_customers', 'time', 'total')
    a.main()
    print_lst = [(x,y) for x, y in a.graph_list_of_tups if x in correct_keys]
    temp = sorted(print_lst,key=itemgetter(0))
    time_values = [x for x, y in temp]
    row = 1
    for n in time_values:
        adoption_sheet.write(row, 0, n)  
        row += 1

    col = 1   
    for filter, category_lst in all_filters:
        if 'Tier' not in filter:
            adoption_sheet.write(0, col, "No. of Customers in " + filter)
            a = time_graph('utility_log_number_of_customers', 'time', 'total', lst_of_customer_category_names = category_lst)
            a.main()
            write_sorted_tups(a.graph_list_of_tups, col, adoption_sheet)
            col += 1
        
            adoption_sheet.write(0, col, "No. of PV Adopters in " + filter)
            a = time_graph('customer_log_number_of_pv_adopters', 'time', 'total', lst_of_PVTech_types = Tech_types, lst_of_customer_category_names = category_lst)
            a.main()
            write_sorted_tups(a.graph_list_of_tups, col, adoption_sheet)
            col += 1
            
    # SetUp Load Profile Sheet
    load_profile_sheet = book.add_sheet("Load_Profile", cell_overwrite_ok=True)
    # Set time column in Load Profile Sheet
    load_profile_sheet.write(0, 0, "Time_Step")
    a = time_graph('utility_log_number_of_customers', 'time', 'total')
    a.main()
    print_lst = [(x,y) for x, y in a.graph_list_of_tups if x in correct_keys]
    temp = sorted(print_lst,key=itemgetter(0))
    time_values = [x for x, y in temp]
    row = 1
    for n in time_values:
        load_profile_sheet.write(row, 0, n)  
        row += 1

    col = 1   
    for filter, category_lst in all_filters:
        if 'Tier' not in filter:
            load_profile_sheet.write(0, col, "Average Load profile for Non Adopters in " + filter)
            a = time_graph('utility_log_usage', 'time', 'average', lst_of_PVTech_types = [None], lst_of_customer_category_names = category_lst)
            a.main()
            write_sorted_tups(a.graph_list_of_tups, col, load_profile_sheet)
            col += 1
        
            load_profile_sheet.write(0, col, "Average Load profile for Adopters in "+ filter)
            a = time_graph('utility_log_usage', 'time', 'average', lst_of_PVTech_types = Tech_types, lst_of_customer_category_names = category_lst)
            a.main()
            write_sorted_tups(a.graph_list_of_tups, col, load_profile_sheet)
            col += 1
            
    # SetUp Tiered Variable Profile Sheet
    tiered_variable_sheet = book.add_sheet("Tiered_Variable_Charge", cell_overwrite_ok=True)
    # Set time column in Load Profile Sheet
    tiered_variable_sheet.write(0, 0, "Time_Step")
    a = time_graph('utility_log_number_of_customers', 'time', 'total')
    a.main()
    print_lst = [(x,y) for x, y in a.graph_list_of_tups if x in correct_keys]
    temp = sorted(print_lst,key=itemgetter(0))
    time_values = [x for x, y in temp]
    row = 1
    for n in time_values:
        tiered_variable_sheet.write(row, 0, n)  
        row += 1

    col = 1   
    for filter, category_lst in all_filters:
        if 'Tier' in filter:
            tier = int(filter.split('Tier')[1])
            tiered_variable_sheet.write(0, col, "Average Tiered Variable Charge in " + filter)
            a = time_graph('utility_log_tiered_variable_charge', 'time', 'total', lst_of_tiers = [tier])
            a.main()
            write_sorted_tups(a.graph_list_of_tups, col, tiered_variable_sheet)
            col += 1
                        
    # SetUp Total PV KiloWatt Production Sheet
    pv_production_sheet = book.add_sheet("Total_PV_Kilowatt_Production", cell_overwrite_ok=True)
    # Set time column in Load Profile Sheet
    pv_production_sheet.write(0, 0, "Time_Step")
    a = time_graph('utility_log_number_of_customers', 'time', 'total')
    a.main()
    print_lst = [(x,y) for x, y in a.graph_list_of_tups if x in correct_keys]
    temp = sorted(print_lst,key=itemgetter(0))
    time_values = [x for x, y in temp]
    row = 1
    for n in time_values:
        pv_production_sheet.write(row, 0, n)  
        row += 1

    col = 1   
    for filter, category_lst in all_filters:
        if 'Tier' not in filter:
            pv_production_sheet.write(0, col, "Average PV Kilowatt Production in " + filter)
            a = time_graph('utility_log_total_PV_kilowatts', 'time', 'total', lst_of_PVTech_types = Tech_types, lst_of_customer_category_names = category_lst)
            a.main()
            write_sorted_tups(a.graph_list_of_tups, col, pv_production_sheet)
            col += 1
            
        
    book.save('Rossi_test.xls')

    print '--------------- Tiered Variable Charge vs. Time ---------------------'
    a = time_graph('utility_log_tiered_variable_charge', 'time', 'total')
    a.main()
    print_lst = [(x,y) for x, y in a.graph_list_of_tups if x in correct_keys]
    temp = sorted(print_lst,key=itemgetter(0))
    temp = [y for x, y in temp]
    print temp
    
    return book

CreateExcelFromResults(results_dict, category_names, pv_tech_sizes)

#             tiered_variable_sheet.write(0, col, "Average Tiered Variable Charge in " + filter)
#             a = time_graph('utility_log_total_tiered_variable_charge', 'time', 'average', lst_of_PVTech_types = Tech_types, lst_of_customer_category_names = category_lst)
#             a.main()
#             write_sorted_tups(a.graph_list_of_tups, col, tiered_variable_sheet)
#             col += 1
        


