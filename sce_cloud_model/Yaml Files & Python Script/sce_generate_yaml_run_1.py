import sce_settings
import math

pv_prices_lst = [7.13 * 0.7 * 1000] * 12
for i in range(1, 20):
    if i <= 3:
        temp_lst = [7.13 * 0.7 * math.pow(0.95, i) * 1000] * 12 
    else:
        temp_lst = [7.13 * math.pow(0.95, i) * 1000] * 12 
    pv_prices_lst.extend(temp_lst)
pv_prices_lst.append(temp_lst[0])

income_fraction_dict = {'IncomeHigh': 0.33, 'IncomeMedium': 0.33, 'IncomeLow': 0.34}
house_fraction_dict = {'House': 0.70, 'Rent': 0.30}
consumption_fraction_dict = {'Bin1': 0.24, 'Bin2': 0.28, 'Bin3': 0.21, 'Bin4': 0.05, 'Bin5': 0.22}

total_customer_number = 2 * math.pow(10, 6)
category_count_dict = {}

def populate_category_count_dict(income_fraction_dict, house_fraction_dict, consumption_fraction_dict):
    for income, inc_frac in income_fraction_dict.iteritems():
        for tenure, ten_frac in house_fraction_dict.iteritems():
            for consumption, con_frac in consumption_fraction_dict.iteritems():
                key = '1:' + tenure + '2:' + income + '3:' + consumption
                value = inc_frac * ten_frac * con_frac
                category_count_dict[key] = value
    for key, frac in category_count_dict.iteritems():
        category_count_dict[key] *= total_customer_number

populate_category_count_dict(income_fraction_dict, house_fraction_dict, consumption_fraction_dict)

def generate_sce_data_yaml():
    f = open('Scenario_1_Standard_Run.yaml','wb')
    f.write('# Simulation 1: Base Case Run\n')
    f.write('# Constant across all runs\n')
    f.write('#    A. Percentage of households at different income levels: High, Medium, Low = [33, 33, 34]\n')
    f.write('#    B. Percentage of residences that are owned or rented: owned/rented = [70, 30]\n')
    f.write('#    C. Consumption categories: [0 to 300, 301 to 500, 501 to 700, 701 to 1000, 1001+ ]\n')
    f.write('#    C. Consumption categories: [0 to 300, 301 to 500, 501 to 700, 701 to 1000, 1001+ ]\n')
    f.write('# Parameters that vary across runs\n')
    f.write('#    1. Percentage of customers in each consumption category: [24, 28, 21, 5, 22]\n')
    f.write('#    2. Percentage of innovators (adoptions per year) at each income and each consumption level: 0.6\n')
    f.write('\n')
    
    # define technology installer
    f.write('- technology_installer_dictionary :\n')
    f.write('    installer_1 :\n')
    f.write('        specs :\n')
    f.write('            type : PvInstaller\n')
    f.write('            name : Pv Installer\n')
    f.write('            parameter_dictionary:\n')
    f.write('                kw_per_panel : 1\n')
    f.write('                minimum_number_of_panels : 3\n')
    f.write('                maximum_number_of_panels : 7\n')
    f.write('                conversion_factor : 1\n')
    f.write('                efficiency : \n')
    f.write('                    list_of_values : ' + create_string_from_list([(1 - (0.0/12)*x) for x in range(0,240)]) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    f.write('                cost_per_kw :\n')
    f.write('                    list_of_values : ' + create_string_from_list(pv_prices_lst) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    f.write('                term_in_months : 240\n')
    f.write('                annual_interest_rate : 5\n')
    f.write('\n')

    # define technology dictionary
    f.write('- technology_dictionary :\n')
    f.write('    technology_1 :\n')
    f.write('        specs :\n')
    f.write('            type : PvTechnology\n')
    f.write('            name : PV\n')
    f.write('            parameter_dictionary :\n')
    f.write('                conversion_factor : 1\n')
    f.write('                quantity_min : 5\n')
    f.write('                quantity_max : 5\n')
    f.write('\n')
    
    # define consumption profiles
    f.write('- consumption_profile_dictionary :\n')
    f.write('    consumption_profile_1: \n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Consumption Profile 1\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*2*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    
    f.write('    consumption_profile_2: \n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Consumption Profile 2\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*4*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    
    f.write('    consumption_profile_3: \n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Consumption Profile 3\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*6*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    
    f.write('    consumption_profile_4: \n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Consumption Profile 4\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*8*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    
    f.write('    consumption_profile_5: \n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Consumption Profile 5\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*13*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    f.write('\n')
    
    # define solar intensity profiles
    f.write('- solar_intensity_profile_dictionary :\n')
    f.write('    solar_intensity_profile_1 :\n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Solar Intensity Profile 1\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([69.9565, 79.2319, 122.4210, 146.9754, 163.7903, 177.4794, 187.9472, 172.8724, 135.2222, 107.3685, 80.8907, 69.8445],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    f.write('    solar_intensity_profile_2 :\n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Solar Intensity Profile 2\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([0] * 12,sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
    f.write('                    index_of_begin_tick : 0\n')
    f.write('\n')
    
    # define baseline regions
    f.write('- baseline_region_dictionary :\n')
    f.write('    baseline_region_1 :\n')
    f.write('        specs :\n')
    f.write('            type : BaselineRegion\n')
    f.write('            name : Zone 1\n')
    f.write('            summer_baseline_in_kwh_per_year : ' + str(12.2*sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR) + '\n')
    f.write('            winter_baseline_in_kwh_per_year : ' + str(10.1*sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR) + '\n')
    f.write('\n')
    
    # define rate schedules
    f.write('- rate_schedule_dictionary :\n')
    f.write('    rate_schedule_1 :\n')
    f.write('        specs :\n')
    f.write('            type : TierNetMeterRateSchedule\n')
    f.write('            name : Schedule D\n')
    f.write('            rate_component_dictionary :\n')
    f.write('                basic_charge : 0\n')
    f.write('                tiered_variable_charge :\n')
    f.write('                    - 0.13\n')
    f.write('                    - 0.16\n')
    f.write('                    - 0.27\n')
    f.write('                    - 0.31\n')
    f.write('                net_surplus_compensation_rate : 0.035\n')
    f.write('            rate_update_rules_dictionary :\n')
    f.write('                annual_percent_increase_in_tier_1 : 1.01\n')
    f.write('                annual_percent_increase_in_tier_2 : 1.01\n')
    f.write('                difference_between_tier_3_and_4 : 0.04\n')
    f.write('\n')
    
    # define utility
    f.write('- utility_dictionary :\n')
    f.write('    utility_1 :\n')
    f.write('        specs :\n')
    f.write('            type : Utility\n')
    f.write('            name : utility\n')
    f.write('            parameter_dictionary :\n')
    f.write('                baseline_as_percentage_of_aggregate_usage : 0.55\n')
    f.write('                delivery_revenue_requirement_per_year : ' + str(2.74340048593 * (10**9)) + '\n')
    f.write('                generation_revenue_requirement_per_kwh : 0.08205\n')
    f.write('\n')

    f.write('- residential_customer_category_dictionary :\n')
    household_number = 1
    for consumption_category, customer_count in category_count_dict.iteritems():
        household_tenure = get_middle_text(consumption_category, '1:', '2:')
        income_group = get_middle_text(consumption_category, '2:', '3:')
        consumption_bin = int(float(get_middle_text(consumption_category, '3:Bin', '<')))
        
        name = str(household_tenure) + str(income_group) + 'ConsumptionBin' + str(consumption_bin)
        if household_tenure == 'House':
            f.write('    residential_customer_category_' + name + ':\n')
            f.write('        specs :\n')
            f.write('            type : ResidentialCustomerCategory\n')
            f.write('            parameter_dictionary :\n')
            f.write('                customer_category_name : Customer_Category_' + name + '\n')
            f.write('                number_of_customers : ' + str(customer_count) + '\n')
            f.write('                consumption_profile : Consumption Profile ' + str(consumption_bin) + '\n')
            f.write('                solar_intensity_profile : Solar Intensity Profile 1\n')
            f.write('                name_of_rate_schedule : Schedule D\n')
            f.write('                pv_installer : Pv Installer\n')
            f.write('                adoption_parameter_p : 0.006\n')
            f.write('                adoption_parameter_b : 0.0001\n')
            f.write('                name_of_baseline_region : Zone 1\n')
        else:
            f.write('    residential_customer_category_' + name + ':\n')
            f.write('        specs :\n')
            f.write('            type : ResidentialCustomerCategory\n')
            f.write('            parameter_dictionary :\n')
            f.write('                customer_category_name : Customer_Category_' + name + '\n')
            f.write('                number_of_customers : ' + str(customer_count) + '\n')
            f.write('                consumption_profile : Consumption Profile ' + str(consumption_bin) + '\n')
            f.write('                solar_intensity_profile : Solar Intensity Profile 2\n')
            f.write('                name_of_rate_schedule : Schedule D\n')
            f.write('                pv_installer : Pv Installer\n')
            f.write('                adoption_parameter_p : 0.006\n')
            f.write('                adoption_parameter_b : 0.0001\n')
            f.write('                name_of_baseline_region : Zone 1\n')            
    f.write('\n')
    
    f.close()
    
def create_string_from_list(list_of_values):
    s = '[' + ', '.join(str(l) for l in list_of_values) + ']'
    return s
    
def get_middle_text(line, string_start, string_end):
    temp = line.split(string_start)[1]
    return temp.split(string_end)[0]

if __name__ == '__main__':
    generate_sce_data_yaml()
    