import sce_settings
from category_count import category_count_dict
    
def generate_sce_data_yaml():
    f = open('sce_data_run_1.yaml','wb')
    
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
    f.write('                    list_of_values : ' + create_string_from_list([(7.13 - (0.42/12)*x)*1000*0.7 for x in range(0,48)] + [(7.13 - (0.42/12)*x)*1000 for x in range(49,241)]) + '\n')
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
    for consumption_category in range(1,10):
        f.write('    consumption_profile_' + str(consumption_category) + ' :\n')
        f.write('        specs : \n')
        f.write('            type : Trace\n')
        f.write('            name : Consumption Profile ' + str(consumption_category) + '\n')
        f.write('            parameter_dictionary :\n')
        f.write('                trace :\n')
        f.write('                    list_of_values : ' + create_string_from_list([x*consumption_category*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
        f.write('                    index_of_begin_tick : 0\n')
    
    consumption_category = 13
    f.write('    consumption_profile_' + str(10) + ' :\n')
    f.write('        specs : \n')
    f.write('            type : Trace\n')
    f.write('            name : Consumption Profile ' + str(10) + '\n')
    f.write('            parameter_dictionary :\n')
    f.write('                trace :\n')
    f.write('                    list_of_values : ' + create_string_from_list([x*consumption_category*sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR/y for (x,y) in zip([99.4550, 88.7206, 90.9491, 84.5422, 86.4829, 92.1024, 123.9677, 128.1275, 109.5865, 95.7523, 91.3362, 108.9776],sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)] * 30) + '\n')
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



#monthly consumption for 100kWh average
# 99.4550   88.7206   90.9491   84.5422   86.4829   92.1024  123.9677  128.1275
#  109.5865   95.7523   91.3362  108.9776

#monthly generation for 1514kwh yearly generation
# 69.9565   79.2319  122.4210  146.9754  163.7903  177.4794  187.9472  172.8724
#  135.2222  107.3685   80.8907   69.8445

#ObjRate.vec_RateComponent(1).BaselineSummer = 12.26;
#ObjRate.vec_RateComponent(1).BaselineWinter = 10.11;

#vec_ObjExpense(1).vec_OperatingFixed =   2.580065606616279e9*[1 (1+DistInc/100).^(1:30)];
#vec_ObjExpense(1).vec_OperatingVariable = 0.08205*ones(8760,1);

# distribution of average monthly consumption     
#    X = [ 152825 514066 599871 650102 538394 ...
#      413408 346548 194827 170615 88875 ...
#      117678 55506 49652 52475 29767 ...
#      8743 10383 8649 14959 8630]';

# distribution of customers who cannot use pv
#   Y = [152825 446402 441955 393393 283276 217515 182337 102508 89769 46761 58819 27743 24817 26229 14878 4370 5190 4323 7477 4314]

# initial consumption by tier
# [36074000.065321565, 7542393.274697243, 11247886.555195004, 10646120.104788888] => delivery revenue requirement is 2743400485.93

    # define residential customer categories
#     consumption_distribution = [152825, 514066, 599871, 650102, 538394, 413408, 346548, 194827, 170615, 88875, 117678, 55506, 49652, 52475, 29767, 8743, 10383, 8649, 14959, 8630]
#     consumption_distribution = [int(float(x)/1) for x in consumption_distribution]
#     consumption_distribution_non_pv_customers = [152825, 446402, 441955, 393393, 283276, 217515, 182337, 102508, 89769, 46761, 58819, 27743, 24817, 26229, 14878, 4370, 5190, 4323, 7477, 4314]
#     consumption_distribution_non_pv_customers = [int(float(x)/1) for x in consumption_distribution_non_pv_customers]
#     consumption_distribution_potential_pv_customers = [x - y for (x,y) in zip(consumption_distribution,consumption_distribution_non_pv_customers)]
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
            f.write('                adoption_parameter_p : 0.2\n')
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
            f.write('                adoption_parameter_p : 0.2\n')
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
    