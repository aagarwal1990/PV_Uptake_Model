import xlrd 
import sce_settings
import math
import re

def get_middle_text(line, string_start, string_end):
    temp = line.split(string_start)[1]
    return temp.split(string_end)[0]

specs = []

workbook = xlrd.open_workbook('ExcelMockup_AccurateValues.xlsm')
adoption_model = workbook.sheet_by_name('Adoption_Model')
consumption_categories = workbook.sheet_by_name('Category_Names')
pv_parameters = workbook.sheet_by_name('PV_Parameters')
tariff_structures = workbook.sheet_by_name('Executive_Summary')
utility_costs = workbook.sheet_by_name('Annual_Utility_Tier_Prices')

runTime = tariff_structures.cell_value(1, 7)

""" generate_yaml_dct """
yaml_dct = {}
technology_installer_dictionary = {}
technology_dictionary = {}
consumption_profile_dictionary = {}
solar_intensity_profile_dictionary = {}
baseline_region_dictionary = {}
rate_schedule_dictionary = {}
utility_dictionary = {}
residential_customer_category_dictionary = {}

""" Parse Adoption Model Worksheet """
# Get list of Rates
rate_lst = []
rate_col = 0
rate_row = 1
while adoption_model.cell_value(rate_row, rate_col) is not '':
    rate_lst.append(adoption_model.cell_value(rate_row, rate_col))
    rate_row += 1

# Get Model Type and parameters
adoption_model_dct = {}
model_row = 8
model_col = 3
adoption_model_dct['model_type'] = adoption_model.cell_value(model_row, model_col)
adoption_model_dct['model_type_pClassic'] = float(adoption_model.cell_value(model_row, model_col + 1))
adoption_model_dct['model_type_qClassic'] = float(adoption_model.cell_value(model_row, model_col + 2))
adoption_model_dct['model_type_bClassic'] = float(adoption_model.cell_value(model_row, model_col + 3))
adoption_model_dct['model_type_p_bin_1'] = float(adoption_model.cell_value(model_row, model_col + 4))
adoption_model_dct['model_type_q_bin_1'] = float(adoption_model.cell_value(model_row, model_col + 5))
adoption_model_dct['model_type_p_bin_2'] = float(adoption_model.cell_value(model_row, model_col + 6))
adoption_model_dct['model_type_q_bin_2'] = float(adoption_model.cell_value(model_row, model_col + 7))
adoption_model_dct['model_type_p_bin_3'] = float(adoption_model.cell_value(model_row, model_col + 8))
adoption_model_dct['model_type_q_bin_3'] = float(adoption_model.cell_value(model_row, model_col + 9))
adoption_model_dct['initial_adopters']  = int(consumption_categories.cell_value(1, 2))
adoption_model_dct['total_population'] = int(consumption_categories.cell_value(1, 0))
adoption_model_dct['shading_assumption']  = 1 - float(pv_parameters.cell_value(20, 0))


""" Parse Consumption Categories Worksheet """
customer_categories_dct = {}
# Get consumption_categories and percentage population
total_population = int(consumption_categories.cell_value(1, 0))
for cat_row in range(7, 11):
    category_col = 0
    Tenure = consumption_categories.cell_value(cat_row, category_col)
    category_col += 1
    Rate =  consumption_categories.cell_value(cat_row, category_col)
    category_col += 1
    aggregate_population = float(consumption_categories.cell_value(cat_row, category_col)) * 0.01
    category_col += 1
    for bin in range(1, 7):
        temp_population = float(consumption_categories.cell_value(cat_row, category_col)) * 0.01
        category_population = temp_population * aggregate_population
        category_name = 'Tenure:' + Tenure.upper() + 'RateSchedule:' + Rate.upper() + 'Consumption:Bin' + str(bin)
        customer_categories_dct[category_name] = int(category_population * total_population)
        category_col += 1
        
solar_customer_categories_dct = {}
# Get consumption_categories and percentage population
solar_total_population = int(consumption_categories.cell_value(1, 2))
for solar_cat_row in range(16, 20):
    solar_category_col = 0
    solar_Tenure = consumption_categories.cell_value(solar_cat_row, solar_category_col)
    solar_category_col += 1
    solar_Rate =  consumption_categories.cell_value(solar_cat_row, solar_category_col)
    solar_category_col += 1
    solar_aggregate_population = float(consumption_categories.cell_value(solar_cat_row, solar_category_col)) * 0.01
    solar_category_col += 1
    for solar_bin in range(1, 7):
        solar_temp_population = float(consumption_categories.cell_value(solar_cat_row, solar_category_col)) * 0.01
        solar_category_population = solar_temp_population * solar_aggregate_population
        solar_category_name = 'Tenure:' + solar_Tenure.upper() + 'RateSchedule:' + solar_Rate.upper() + 'Consumption:Bin' + str(solar_bin)
        solar_customer_categories_dct[solar_category_name] = int(solar_category_population * solar_total_population)
        solar_category_col += 1
        
""" Parse PV Parameters Worksheet """
pv_parameters_dct = {}
# Get PV Prices
pv_row = 2
pv_col = 1
pv_parameters_dct['pv_prices_lst'] = []
for pv_col in range(pv_col, pv_parameters.ncols):
    pv_price = float(pv_parameters.cell_value(pv_row, pv_col))
    annual_price_lst = [pv_price] * 12
    pv_parameters_dct['pv_prices_lst'].extend(annual_price_lst)
    pv_col += 1
pv_parameters_dct['power_production'] =  int(pv_parameters.cell_value(8, 0))

consumptionBin_systemSize = {}
for pv_row in range(12, 18):
    consumptionBin_systemSize[int(pv_parameters.cell_value(pv_row, 0))] = pv_parameters.cell_value(pv_row, 1)
    
""" Parse Tariff Structures Worksheet """
tariff_structure_dct = {}
# Get Number of Tiers
tariff_col = 1
if tariff_structures.cell_value(1, tariff_col) == "Ratio":
    tariff_structure_dct['number_of_tiers'] = tariff_structures.cell_value(1, tariff_col)
else:
    tariff_structure_dct['number_of_tiers'] = int(tariff_structures.cell_value(1, tariff_col))

# Get T1 and T2 Annual Increase &  Get T3/T4 and T4/T5 Delta
tariff_structure_dct['T1_increase'] = float(tariff_structures.cell_value(2, tariff_col))
tariff_structure_dct['T2_increase'] = float(tariff_structures.cell_value(3, tariff_col))
tariff_structure_dct['T4-T3_delta'] = float(tariff_structures.cell_value(4, tariff_col))
tariff_structure_dct['T5-T4_delta'] = float(tariff_structures.cell_value(5, tariff_col))

# Get Ratio of Tier rates
tariff_structure_dct['T2_T1_ratio'] = float(tariff_structures.cell_value(6, tariff_col))
tariff_structure_dct['T3_T1_ratio'] = float(tariff_structures.cell_value(7, tariff_col))
tariff_structure_dct['T4_T1_ratio'] = float(tariff_structures.cell_value(8, tariff_col))
tariff_structure_dct['T5_T1_ratio'] = float(tariff_structures.cell_value(9, tariff_col))

# Get Baseline Charges
tariff_structure_dct['summer_and_winter_baseline'] = float(tariff_structures.cell_value(12, tariff_col))
tariff_structure_dct['T2/Baseline'] = float(tariff_structures.cell_value(13, tariff_col))
tariff_structure_dct['T3/Baseline'] = float(tariff_structures.cell_value(14, tariff_col))
tariff_structure_dct['T4/Baseline'] = float(tariff_structures.cell_value(15, tariff_col))
tariff_structure_dct['T5/Baseline'] = float(tariff_structures.cell_value(16, tariff_col))

# Get Minimum Charges
tariff_structure_dct['minimum_charge_CARE'] = float(tariff_structures.cell_value(19, tariff_col))
tariff_structure_dct['minimum_charge_nonCARE'] = float(tariff_structures.cell_value(20, tariff_col))

# Get Customer Charges
tariff_structure_dct['customer_charge_type'] = tariff_structures.cell_value(23, tariff_col)
tariff_structure_dct['flat_customer_charge'] = float(tariff_structures.cell_value(24, tariff_col))
tariff_structure_dct['demand_differentiated_break_point'] = int(tariff_structures.cell_value(25, tariff_col))
tariff_structure_dct['customer_charge_above_break_point'] = float(tariff_structures.cell_value(26, tariff_col))

# Get CARE Discounts
tariff_structure_dct['T1_energy_CARE_discount'] = float(tariff_structures.cell_value(30, tariff_col))
tariff_structure_dct['T2_energy_CARE_discount'] = float(tariff_structures.cell_value(31, tariff_col))
tariff_structure_dct['T3_energy_CARE_discount'] = float(tariff_structures.cell_value(32, tariff_col))
tariff_structure_dct['T4_energy_CARE_discount'] = float(tariff_structures.cell_value(33, tariff_col))
tariff_structure_dct['T5_energy_CARE_discount'] = float(tariff_structures.cell_value(34, tariff_col))
tariff_structure_dct['fixed_charge_CARE_discount'] = float(tariff_structures.cell_value(35, tariff_col))

# Get Tier Rates
tariff_col_2 = 5
tariff_structure_dct['T1_rate'] = float(tariff_structures.cell_value(1, tariff_col_2))
tariff_structure_dct['T2_rate'] = float(tariff_structures.cell_value(2, tariff_col_2))
tariff_structure_dct['T3_rate'] = float(tariff_structures.cell_value(3, tariff_col_2))
tariff_structure_dct['T4_rate'] = float(tariff_structures.cell_value(4, tariff_col_2))
tariff_structure_dct['T5_rate'] = float(tariff_structures.cell_value(5, tariff_col_2))
tariff_structure_dct['net_surplus_compensation_rate'] = float(tariff_structures.cell_value(6, tariff_col_2))

""" Parse Utility Costs worksheet """
utility_costs_dct = {}
utility_col = 1
utility_costs_dct['generation_marginal_energy_cost_summer_on_peak'] = float(utility_costs.cell_value(0, utility_col))
utility_costs_dct['generation_marginal_energy_cost_summer_mid_peak'] = float(utility_costs.cell_value(1, utility_col))
utility_costs_dct['generation_marginal_energy_cost_summer_off_peak'] = float(utility_costs.cell_value(2, utility_col))
utility_costs_dct['generation_marginal_energy_cost_winter_on_peak'] = float(utility_costs.cell_value(3, utility_col))
utility_costs_dct['generation_marginal_energy_cost_winter_off_peak'] = float(utility_costs.cell_value(4, utility_col))
utility_costs_dct['total_system_delivery_costs'] = float(utility_costs.cell_value(8, utility_col))


# initialize technology installer dictionary    
tech_installer_parameter_dictionary = {}
tech_installer_parameter_dictionary['kw_per_panel'] = 1
tech_installer_parameter_dictionary['minimum_number_of_panels'] = 3
tech_installer_parameter_dictionary['maximum_number_of_panels'] = 10
tech_installer_parameter_dictionary['conversion_factor'] = 1 
tech_installer_parameter_dictionary['efficiency'] = {}
tech_installer_parameter_dictionary['efficiency']['list_of_values'] = [(1 - (0.0/12)*x) for x in range(0,240)]
tech_installer_parameter_dictionary['efficiency']['index_of_begin_tick'] = 0
tech_installer_parameter_dictionary['cost_per_kw'] = {}
tech_installer_parameter_dictionary['cost_per_kw']['list_of_values'] = pv_parameters_dct['pv_prices_lst']
tech_installer_parameter_dictionary['cost_per_kw']['index_of_begin_tick'] = 0
tech_installer_parameter_dictionary['term_in_months'] = 240
tech_installer_parameter_dictionary['annual_interest_rate'] = 5
tech_installer_parameter_dictionary['consumptionBin_systemSize'] = consumptionBin_systemSize

tech_installer_specs = {}
tech_installer_specs['type'] = 'PvInstaller'
tech_installer_specs['name'] = 'Pv Installer'
tech_installer_specs['parameter_dictionary'] = tech_installer_parameter_dictionary

technology_installer_dictionary['installer_1'] = {}
technology_installer_dictionary['installer_1']['specs'] = tech_installer_specs

specs.append({'technology_installer_dictionary': technology_installer_dictionary})

# initialize technology dictionary
tech_parameter_dictionary = {}
tech_parameter_dictionary['conversion_factor'] = 1
tech_parameter_dictionary['quantity_min'] = 1
tech_parameter_dictionary['quantity_max'] = 10

tech_specs = {}
tech_specs['type'] = 'PvTechnology'
tech_specs['name'] = 'PV'
tech_specs['parameter_dictionary'] = tech_parameter_dictionary

technology_dictionary['technology_1'] = {}
technology_dictionary['technology_1']['specs'] = tech_specs

specs.append({'technology_dictionary': technology_dictionary})

# define consumption profiles
consumption_vals = {1: 1.3, 2: 3.0, 3: 5.0, 4: 6.9, 5: 8.9, 6: 13.0}
for bin in range(1, 7):
    consumption_ratio = consumption_vals[bin]
    consum_parameter_dictionary = {}
    consum_parameter_dictionary['trace'] = {}
    consum_parameter_dictionary['trace']['list_of_values'] = [x * consumption_ratio * sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30
    consum_parameter_dictionary['trace']['index_of_begin_tick'] = 0
    
    consum_specs = {}
    consum_specs['type'] = 'Trace'
    consum_specs['name'] = 'Consumption Profile ' + str(bin)
    consum_specs['parameter_dictionary'] = consum_parameter_dictionary
    
    consumption_profile_name = ''
    consumption_profile_name = 'consumption_profile_' + str(bin)
    consumption_profile_dictionary[consumption_profile_name] = {}
    consumption_profile_dictionary[consumption_profile_name]['specs'] = consum_specs

specs.append({'consumption_profile_dictionary': consumption_profile_dictionary})
    
# define solar intensity profiles - climate zone 6
power_production_ratio = float(pv_parameters_dct['power_production']) / 150

solar_parameter_dictionary = {}
solar_parameter_dictionary['trace'] = {}
solar_parameter_dictionary['trace']['list_of_values'] = [x * power_production_ratio * sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([69.9565, 79.2319, 122.4210, 146.9754, 163.7903, 177.4794, 187.9472, 172.8724, 135.2222, 107.3685, 80.8907, 69.8445],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30
solar_parameter_dictionary['trace']['index_of_begin_tick'] = 0

solar_specs = {}
solar_specs['type'] = 'Trace'
solar_specs['name'] = 'Solar Intensity Profile 1' 
solar_specs['parameter_dictionary'] = solar_parameter_dictionary

solar_intensity_profile_dictionary['solar_intensity_profile_1'] = {}
solar_intensity_profile_dictionary['solar_intensity_profile_1']['specs'] = solar_specs
    
solar_parameter_dictionary = {}
solar_parameter_dictionary['trace'] = {}
solar_parameter_dictionary['trace']['list_of_values'] = [x*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([0] * 12,sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30
solar_parameter_dictionary['trace']['index_of_begin_tick'] = 0

solar_specs = {}
solar_specs['type'] = 'Trace'
solar_specs['name'] = 'Solar Intensity Profile 2' 
solar_specs['parameter_dictionary'] = solar_parameter_dictionary

solar_intensity_profile_dictionary['solar_intensity_profile_2'] = {}
solar_intensity_profile_dictionary['solar_intensity_profile_2']['specs'] = solar_specs

specs.append({'solar_intensity_profile_dictionary': solar_intensity_profile_dictionary})

# define baseline regions
baseline_specs = {}
baseline_specs['type'] = 'BaselineRegion'
baseline_specs['name'] = 'Zone 1' 
baseline_specs['summer_baseline_in_kwh_per_year'] = 12.2*sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR 
baseline_specs['winter_baseline_in_kwh_per_year'] = 10.1*sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR

baseline_region_dictionary['baseline_region_1'] = {}
baseline_region_dictionary['baseline_region_1']['specs'] = baseline_specs

specs.append({'baseline_region_dictionary': baseline_region_dictionary})

# define rate schedules
# NONCARE Rate Schedule
rate_component_dictionary = {}
if tariff_structure_dct['customer_charge_type'].lower() == "Demand Differentiated".lower():
    rate_component_dictionary['customer_charge_demand_differentiated_flag'] = 1
else:
    rate_component_dictionary['customer_charge_demand_differentiated_flag'] = 0
rate_component_dictionary['demand_differentiated_break_point'] = int(tariff_structures.cell_value(25, tariff_col))
rate_component_dictionary['customer_charge_above_break_point'] = float(tariff_structures.cell_value(26, tariff_col))    
rate_component_dictionary['customer_charge'] = tariff_structure_dct['flat_customer_charge']
rate_component_dictionary['number_of_tiers'] = tariff_structure_dct['number_of_tiers']
rate_component_dictionary['T2_usage_baseline'] = tariff_structure_dct['T2/Baseline']
rate_component_dictionary['T3_usage_baseline'] = tariff_structure_dct['T3/Baseline']
rate_component_dictionary['T4_usage_baseline'] = tariff_structure_dct['T4/Baseline']
rate_component_dictionary['T5_usage_baseline'] = tariff_structure_dct['T5/Baseline']
rate_component_dictionary['T1_rate'] = tariff_structure_dct['T1_rate']
rate_component_dictionary['T2_rate'] = tariff_structure_dct['T2_rate']
rate_component_dictionary['T3_rate'] = tariff_structure_dct['T3_rate']
rate_component_dictionary['T4_rate'] = tariff_structure_dct['T4_rate']
rate_component_dictionary['T5_rate'] = tariff_structure_dct['T5_rate']
rate_component_dictionary['net_surplus_compensation_rate'] = tariff_structure_dct['net_surplus_compensation_rate']

rate_update_rules_dictionary = {}
rate_update_rules_dictionary['CARE_flag'] = 0
if tariff_structure_dct['number_of_tiers'] == "Ratio":
    rate_update_rules_dictionary['ratio_flag'] = 1
else:
    rate_update_rules_dictionary['ratio_flag'] = 0
    
rate_update_rules_dictionary['T1_increase'] = tariff_structure_dct['T1_increase'] + 1
rate_update_rules_dictionary['T2_increase'] = tariff_structure_dct['T2_increase'] + 1
rate_update_rules_dictionary['T4_T3_delta'] = tariff_structure_dct['T4-T3_delta']
rate_update_rules_dictionary['T5_T4_delta'] = tariff_structure_dct['T5-T4_delta']

rate_update_rules_dictionary['T2_T1_ratio'] = tariff_structure_dct['T2_T1_ratio']
rate_update_rules_dictionary['T3_T1_ratio'] = tariff_structure_dct['T3_T1_ratio']
rate_update_rules_dictionary['T4_T1_ratio'] = tariff_structure_dct['T4_T1_ratio']
rate_update_rules_dictionary['T5_T1_ratio'] = tariff_structure_dct['T5_T1_ratio']

rate_update_rules_dictionary['T1_CARE_discount'] = 1 - tariff_structure_dct['T1_energy_CARE_discount']
rate_update_rules_dictionary['T2_CARE_discount'] = 1 - tariff_structure_dct['T2_energy_CARE_discount']
rate_update_rules_dictionary['T3_CARE_discount'] = 1 - tariff_structure_dct['T3_energy_CARE_discount']
rate_update_rules_dictionary['T4_CARE_discount'] = 1 - tariff_structure_dct['T4_energy_CARE_discount']
rate_update_rules_dictionary['T5_CARE_discount'] = 1 - tariff_structure_dct['T5_energy_CARE_discount']
rate_update_rules_dictionary['fixed_charge_CARE_discount'] = tariff_structure_dct['fixed_charge_CARE_discount']

rate_specs = {}
rate_specs['type'] = 'TierNetMeterRateSchedule'
rate_specs['name'] = 'Schedule D'
rate_specs['rate_component_dictionary'] = rate_component_dictionary
rate_specs['rate_update_rules_dictionary'] = rate_update_rules_dictionary

rate_schedule_dictionary['rate_schedule_1'] = {}
rate_schedule_dictionary['rate_schedule_1']['specs'] = rate_specs

# CARE Rate Schedule
rate_component_dictionary = {}
if tariff_structure_dct['customer_charge_type'].lower() == "Demand Differentiated".lower():
    rate_component_dictionary['customer_charge_demand_differentiated_flag'] = 1
else:
    rate_component_dictionary['customer_charge_demand_differentiated_flag'] = 0
rate_component_dictionary['demand_differentiated_break_point'] = 0
rate_component_dictionary['customer_charge_above_break_point'] = 0
rate_component_dictionary['customer_charge'] = tariff_structure_dct['flat_customer_charge']
rate_component_dictionary['number_of_tiers'] = tariff_structure_dct['number_of_tiers']
rate_component_dictionary['T2_usage_baseline'] = tariff_structure_dct['T2/Baseline']
rate_component_dictionary['T3_usage_baseline'] = tariff_structure_dct['T3/Baseline']
rate_component_dictionary['T4_usage_baseline'] = tariff_structure_dct['T4/Baseline']
rate_component_dictionary['T5_usage_baseline'] = tariff_structure_dct['T5/Baseline']
rate_component_dictionary['T1_rate'] = tariff_structure_dct['T1_rate'] * (1 - tariff_structure_dct['T1_energy_CARE_discount'])
rate_component_dictionary['T2_rate'] = tariff_structure_dct['T2_rate'] * (1 - tariff_structure_dct['T2_energy_CARE_discount'])
rate_component_dictionary['T3_rate'] = tariff_structure_dct['T3_rate'] * (1 - tariff_structure_dct['T3_energy_CARE_discount'])
rate_component_dictionary['T4_rate'] = tariff_structure_dct['T3_rate'] * (1 - tariff_structure_dct['T4_energy_CARE_discount'])
rate_component_dictionary['T5_rate'] = tariff_structure_dct['T3_rate'] * (1 - tariff_structure_dct['T5_energy_CARE_discount'])
rate_component_dictionary['net_surplus_compensation_rate'] = tariff_structure_dct['net_surplus_compensation_rate']

rate_update_rules_dictionary = {}
rate_update_rules_dictionary['CARE_flag'] = 1
if tariff_structure_dct['number_of_tiers'] == "Ratio":
    rate_update_rules_dictionary['ratio_flag'] = 1
else:
    rate_update_rules_dictionary['ratio_flag'] = 0
    
rate_update_rules_dictionary['T1_increase'] = tariff_structure_dct['T1_increase'] + 1
rate_update_rules_dictionary['T2_increase'] = tariff_structure_dct['T2_increase'] + 1
rate_update_rules_dictionary['T4_T3_delta'] = tariff_structure_dct['T4-T3_delta']
rate_update_rules_dictionary['T5_T4_delta'] = tariff_structure_dct['T5-T4_delta']

rate_update_rules_dictionary['T2_T1_ratio'] = tariff_structure_dct['T2_T1_ratio']
rate_update_rules_dictionary['T3_T1_ratio'] = tariff_structure_dct['T3_T1_ratio']
rate_update_rules_dictionary['T4_T1_ratio'] = tariff_structure_dct['T4_T1_ratio']
rate_update_rules_dictionary['T5_T1_ratio'] = tariff_structure_dct['T5_T1_ratio']

rate_update_rules_dictionary['T1_CARE_discount'] = 1 - tariff_structure_dct['T1_energy_CARE_discount']
rate_update_rules_dictionary['T2_CARE_discount'] = 1 - tariff_structure_dct['T2_energy_CARE_discount']
rate_update_rules_dictionary['T3_CARE_discount'] = 1 - tariff_structure_dct['T3_energy_CARE_discount']
rate_update_rules_dictionary['T4_CARE_discount'] = 1 - tariff_structure_dct['T4_energy_CARE_discount']
rate_update_rules_dictionary['T5_CARE_discount'] = 1 - tariff_structure_dct['T5_energy_CARE_discount']
rate_update_rules_dictionary['fixed_charge_CARE_discount'] = tariff_structure_dct['fixed_charge_CARE_discount']

rate_specs = {}
rate_specs['type'] = 'TierNetMeterRateSchedule'
rate_specs['name'] = 'Schedule D CARE'
rate_specs['rate_component_dictionary'] = rate_component_dictionary
rate_specs['rate_update_rules_dictionary'] = rate_update_rules_dictionary

rate_schedule_dictionary['rate_schedule_2'] = {}
rate_schedule_dictionary['rate_schedule_2']['specs'] = rate_specs
specs.append({'rate_schedule_dictionary': rate_schedule_dictionary})

# define utility
util_parameter_dictionary = {}
util_parameter_dictionary['baseline_as_percentage_of_aggregate_usage'] = tariff_structure_dct['summer_and_winter_baseline']
util_parameter_dictionary['delivery_revenue_requirement_per_year'] = utility_costs_dct['total_system_delivery_costs']
util_parameter_dictionary['generation_revenue_requirement_per_kwh'] = utility_costs_dct['generation_marginal_energy_cost_summer_mid_peak']

util_specs = {}
util_specs['type'] = 'Utility'
util_specs['name'] = 'utility'
util_specs['parameter_dictionary'] = util_parameter_dictionary

utility_dictionary['utility_1'] = {}
utility_dictionary['utility_1']['specs'] = util_specs
specs.append({'utility_dictionary': utility_dictionary})

# define residential customer categories
for consumption_category, customer_count in customer_categories_dct.iteritems(): 
    cust_parameter_dictionary = {}
    household_tenure = get_middle_text(consumption_category, 'Tenure:', 'RateSchedule:')
    consumption_bin = int(float(get_middle_text(consumption_category, 'Consumption:Bin', '<')))
    rate = get_middle_text(consumption_category, 'RateSchedule:', 'Consumption:')
    rate_schedule_str = 'Schedule D'
    if re.search('NONCARE', rate) == None:
        rate_schedule_str = 'Schedule D CARE'
    cust_parameter_dictionary['customer_category_name'] = 'Customer_Category_' + consumption_category  
    cust_parameter_dictionary['number_of_customers'] = customer_count
    cust_parameter_dictionary['consumption_profile'] =  'Consumption Profile ' + str(consumption_bin)
    if household_tenure == 'HOMEOWNERS':
        cust_parameter_dictionary['solar_intensity_profile'] = 'Solar Intensity Profile 1'
    else:
        cust_parameter_dictionary['solar_intensity_profile'] = 'Solar Intensity Profile 2'
    cust_parameter_dictionary['name_of_rate_schedule'] = rate_schedule_str
    cust_parameter_dictionary['pv_installer'] = 'Pv Installer'
    cust_parameter_dictionary['model_type'] = adoption_model_dct['model_type']
    cust_parameter_dictionary['adoption_parameter_pClassic'] = adoption_model_dct['model_type_pClassic']
    cust_parameter_dictionary['adoption_parameter_qClassic'] = adoption_model_dct['model_type_qClassic']
    cust_parameter_dictionary['adoption_parameter_bClassic'] = adoption_model_dct['model_type_bClassic']
    cust_parameter_dictionary['adoption_parameter_p_bin_1']  = adoption_model_dct['model_type_p_bin_1']
    cust_parameter_dictionary['adoption_parameter_q_bin_1']  = adoption_model_dct['model_type_q_bin_1']
    cust_parameter_dictionary['adoption_parameter_p_bin_2']  = adoption_model_dct['model_type_p_bin_2']
    cust_parameter_dictionary['adoption_parameter_q_bin_2']  = adoption_model_dct['model_type_q_bin_2']
    cust_parameter_dictionary['adoption_parameter_p_bin_3']  = adoption_model_dct['model_type_p_bin_3']
    cust_parameter_dictionary['adoption_parameter_q_bin_3']  = adoption_model_dct['model_type_q_bin_3']
    cust_parameter_dictionary['name_of_baseline_region'] = 'Zone 1'
    cust_parameter_dictionary['initial_adopters'] = adoption_model_dct['initial_adopters']
    cust_parameter_dictionary['total_population'] = adoption_model_dct['total_population']
    cust_parameter_dictionary['shading_assumption'] = adoption_model_dct['shading_assumption']     
    cust_specs = {}
    cust_specs['type'] = 'ResidentialCustomerCategory'
    cust_specs['parameter_dictionary'] = cust_parameter_dictionary
    
    category_name = 'residential_customer_category_' + consumption_category
    residential_customer_category_dictionary[category_name] = {}
    residential_customer_category_dictionary[category_name]['specs'] = cust_specs

specs.append({'residential_customer_category_dictionary': residential_customer_category_dictionary})