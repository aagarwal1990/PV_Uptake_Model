# parse contents of specs.yaml to create objects
from sim_structure import Simulator, Aggregator 
from sce_non_agent_specs import Trace, \
                                BaselineRegion, \
                                TierNetMeterBill, \
                                CustomerCategoryAccount, \
                                TierNetMeterRateSchedule, \
                                PvTechnology, \
                                PvInstaller 
from sce_agent_specs import SimulatorClock, ResidentialCustomerCategory, Utility 
import sce_settings
import yaml
import sys, traceback
import logging
import logging.config
import sce_generate_yaml_dct 
                             
class specparser(object):
    def __init__(self):
        self.technology_installer_dictionary = {}
        self.technology_dictionary = {}
        self.consumption_profile_dictionary = {}
        self.baseline_region_dictionary = {}
        self.solar_intensity_profile_dictionary = {}
        self.utility_dictionary = {}
        self.residential_customer_category_dictionary = {}
        self.rate_schedule_dictionary = {}
        sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 50)
        self.simulator = Simulator()
            
    def main(self, yaml_specs):
#           try:
                SimulatorClock('clock', self.simulator)
                #specs = sce_generate_yaml_dct.specs
                
                specs = yaml_specs
                                
                # parse yaml file and create dictionaries for each type of object
                for index, dct in enumerate(specs):
                        # append all technology installers to self.technology_installer_dictionary
                        if 'technology_installer_dictionary' in dct.keys():
                                for key, value in dct['technology_installer_dictionary'].items():
                                    pv_installer_dictionary = dict()
                                    if value['specs']['type'] == 'PvInstaller':
                                        pv_installer_dictionary[value['specs']['name']] = PvInstaller.parse_yaml(value['specs'])
                                self.technology_installer_dictionary['PvInstaller'] = pv_installer_dictionary
                                
                        # append all technology to self.technology_dictionary
                        if 'technology_dictionary' in dct.keys():
                                for key, value in dct['technology_dictionary'].items():
                                    pv_dictionary = dict() 
                                    self.technology_size_lst = []
                                    if value['specs']['type'] == 'PvTechnology':
                                        for c in range(value['specs']['parameter_dictionary']['quantity_min'],value['specs']['parameter_dictionary']['quantity_max'] + 1): 
                                            pv_dictionary[PvTechnology(value['specs']['name'], {'quantity': c, 'conversion_factor': value['specs']['parameter_dictionary']['conversion_factor']})] = 0
                                            self.technology_size_lst.append(c)
                                self.technology_dictionary['PvTechnology'] = pv_dictionary
                                    
                        # append all consumption profiles to consumption_profile_dictionary        
                        if 'consumption_profile_dictionary' in dct.keys():
                                for key, value in dct['consumption_profile_dictionary'].items():
                                    if value['specs']['type'] == 'Trace':                                                                      
                                        self.consumption_profile_dictionary[value['specs']['name']] =  Trace([float(x)/sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR for x in value['specs']['parameter_dictionary']['trace']['list_of_values']], value['specs']['parameter_dictionary']['trace']['index_of_begin_tick'])
                                                        
                        # append all solar intensity profiles to solar_intensity_profile_dictionary      
                        if 'solar_intensity_profile_dictionary' in dct.keys():
                                for key, value in dct['solar_intensity_profile_dictionary'].items():
                                    if value['specs']['type'] == 'Trace':
                                        self.solar_intensity_profile_dictionary[value['specs']['name']] = Trace([float(x)/sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR for x in value['specs']['parameter_dictionary']['trace']['list_of_values']], value['specs']['parameter_dictionary']['trace']['index_of_begin_tick'])
                                                                                                    
                        # append all baseline regions to baseline_region_dictionary                                                    
                        if 'baseline_region_dictionary' in dct.keys():
                                  for key, value in dct['baseline_region_dictionary'].items():
                                    if value['specs']['type'] == 'BaselineRegion':
                                        self.baseline_region_dictionary[value['specs']['name']] = BaselineRegion.parse_yaml(value['specs'])
         
                        # append all rate_schedule to rate_schedule_dictionary                                                    
                        if 'rate_schedule_dictionary' in dct.keys():
                                for key, value in dct['rate_schedule_dictionary'].items():
                                    if value['specs']['type'] == 'TierNetMeterRateSchedule':
                                        self.rate_schedule_dictionary[value['specs']['name']] = TierNetMeterRateSchedule.parse_yaml(value['specs'])
                                                     
                        # append all utilities to utility_dictionary                                                    
                        if 'utility_dictionary' in dct.keys():
                                for key, value in dct['utility_dictionary'].items():
                                    if value['specs']['type'] == 'Utility':
                                        self.utility_dictionary[value['specs']['name']] = Utility.parse_yaml(value['specs'], self.simulator) 
                                                            
                                # append all rate_schedules and baseline_regions to utility dictionaries                                             
                                for key_util, value_util in self.utility_dictionary.items():
                                    for key_base, value_base in self.baseline_region_dictionary.items():
                                         value_util.add_baseline_region(value_base)
                                    for key_rate, value_rate in self.rate_schedule_dictionary.items():
                                         value_util.add_rate_schedule(value_rate)
                 
                        # append all residential_customers to residential_customer_category_dictionary
                        if 'residential_customer_category_dictionary' in dct.keys():   
                                for key, value in dct['residential_customer_category_dictionary'].items():
                                    if value['specs']['type'] == 'ResidentialCustomerCategory':
                                        self.residential_customer_category_dictionary[value['specs']['parameter_dictionary']['customer_category_name']] = ResidentialCustomerCategory.parse_yaml(value['specs'], 
                                                                                                                                                         self.simulator,
                                                                                                                                                         self.consumption_profile_dictionary,
                                                                                                                                                         self.solar_intensity_profile_dictionary,
                                                                                                                                                         self.technology_installer_dictionary['PvInstaller'],
                                                                                                                                                         self.technology_dictionary['PvTechnology'])
                                                                         
                                # append customers to utility dictionaries with specified baseline_regions                                            
                                for key_util, value_util in self.utility_dictionary.items():
                                    for key_cust, value_cust in self.residential_customer_category_dictionary.items():
                                         value_util.add_customer_category(value_cust, value_cust.parameter_dictionary['name_of_baseline_region'])
                         
#                         else:
#                             raise Exception('unrecognized object type in YAML file')
                            
                # connect utility, customer agents and clock                        
                # create aggregate variables
                Aggregator('dictionary_of_rate_schedule', self.simulator, 'dict')
                for key_util, value_util in self.utility_dictionary.items():
                    for value_sched in value_util.rate_schedule_dictionary.itervalues():
                                self.simulator.connect_variable(value_util.__name__, value_sched.name, 'dictionary_of_rate_schedule', 'in')
                
                Aggregator('dictionary_of_load_profile_in_current_step', self.simulator, 'dict')
                for key_cust, value_cust in self.residential_customer_category_dictionary.items():
                                self.simulator.connect_variable(value_cust.get_customer_category_name(), 'dictionary_of_load_profile_in_current_step', 'dictionary_of_load_profile_in_current_step', 'in')

                Aggregator('total_number_of_pv_installations', self.simulator, 'sum') 
                Aggregator('number_of_households_in_pv_market', self.simulator, 'sum') 
                for key_cust, value_cust in self.residential_customer_category_dictionary.items():
                        self.simulator.connect_variable(value_cust.get_customer_category_name(), 'number_of_customers_with_pv', 'total_number_of_pv_installations', 'in')   
                        self.simulator.connect_variable('total_number_of_pv_installations', 'out', value_cust.get_customer_category_name(), 'total_number_of_pv_installations') 
                        self.simulator.connect_variable(value_cust.get_customer_category_name(), 'number_of_customers_in_market_for_pv', 'number_of_households_in_pv_market', 'in') 
                        self.simulator.connect_variable('number_of_households_in_pv_market', 'out', value_cust.get_customer_category_name(), 'number_of_households_in_pv_market')

        
                # connect utility and customer agents
                for key_cust, value_cust in self.residential_customer_category_dictionary.items():
                                self.simulator.connect_variable('dictionary_of_rate_schedule', 'out', value_cust.get_customer_category_name(), 'rate_schedule_dictionary')           

                for key_util, value_util in self.utility_dictionary.items():
                    for key_cust, value_cust in self.residential_customer_category_dictionary.items():
                                self.simulator.connect_variable(value_util.__name__, value_cust.get_name_of_baseline_region(), value_cust.get_customer_category_name(), 'baseline_allocation')
                
                for key_util, value_util in self.utility_dictionary.items():
                    self.simulator.connect_variable('dictionary_of_load_profile_in_current_step', 'out', value_util.__name__, 'customer_current_load_profile_dictionary')
     
                # connect customers and clock
                for key_cust, value_cust in self.residential_customer_category_dictionary.items():
                                self.simulator.connect_variable('clock', 'index_of_start_time_of_current_step', value_cust.get_customer_category_name(), 'index_of_start_time_of_current_step')

                for key_cust, value_cust in self.residential_customer_category_dictionary.items():
                                self.simulator.connect_variable('clock', 'index_of_end_time_of_current_step', value_cust.get_customer_category_name(), 'index_of_end_time_of_current_step')
                                
                # connect utility and clock
                for key_util, value_util in self.utility_dictionary.items():
                    self.simulator.connect_variable('clock', 'index_of_start_time_of_current_step', value_util.__name__, 'index_of_start_time_of_current_step')
    
                for key_util, value_util in self.utility_dictionary.items():
                    self.simulator.connect_variable('clock', 'index_of_end_time_of_current_step', value_util.__name__, 'index_of_end_time_of_current_step')
                    
#           except Exception:  
#                 error_line = traceback.format_exc()
#                 
#                 # Log error  
#                 error_logger = logging.getLogger('errorLogger')
#                 error_logger.error('ERROR PARSING YAML\n' + error_line)
#                 
#                 # Print error to stdout
#                 print ''
#                 print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
#                 print 'ERROR PARSING YAML' 
#                 print error_line
#                 print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
#                 print ''
                
                
                
#logging.config.dictConfig(yaml.load(open('log_specs.yaml', 'r')))                    
#a = specparser()
#a.main()

# print (a.technology_installer_dictionary)
# print (a.technology_dictionary)
# print (a.consumption_profile_dictionary) 
# print (a.solar_intensity_profile_dictionary) 
# print (a.baseline_region_dictionary) 
# print (a.rate_schedule_dictionary) 
# print (a.utility_dictionary) 
# print (a.residential_customer_category_dictionary)           
# a.simulator.print_agent_and_aggregator_names()
# a.simulator.print_write_variables_for_all_agents_and_aggregators()
# a.simulator.print_read_variables_for_all_agents_and_aggregators()         