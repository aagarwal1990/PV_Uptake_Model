import math
import re

def get_middle_text(line, string_start, string_end):
    temp = line.split(string_start)[1]
    return temp.split(string_end)[0]

# Generate number of customers in each category
category_count_dct = {'Tenure:HOMEOWNERSRateSchedule:NONCAREConsumption:Bin1': 194504, 'Tenure:HOMEOWNERSRateSchedule:NONCAREConsumption:Bin2': 497789, 'Tenure:HOMEOWNERSRateSchedule:NONCAREConsumption:Bin3': 572780, 'Tenure:HOMEOWNERSRateSchedule:NONCAREConsumption:Bin4': 431410, 'Tenure:HOMEOWNERSRateSchedule:NONCAREConsumption:Bin5': 266229, 'Tenure:HOMEOWNERSRateSchedule:NONCAREConsumption:Bin6': 307382, 'Tenure:HOMEOWNERSRateSchedule:CAREConsumption:Bin4': 159003, 'Tenure:HOMEOWNERSRateSchedule:CAREConsumption:Bin5': 89890, 'Tenure:HOMEOWNERSRateSchedule:CAREConsumption:Bin6': 86202, 'Tenure:HOMEOWNERSRateSchedule:CAREConsumption:Bin1': 46515, 'Tenure:HOMEOWNERSRateSchedule:CAREConsumption:Bin2': 198215, 'Tenure:HOMEOWNERSRateSchedule:CAREConsumption:Bin3': 228942, 'Tenure:RENTERSRateSchedule:CAREConsumption:Bin1': 86540, 'Tenure:RENTERSRateSchedule:CAREConsumption:Bin3': 114354, 'Tenure:RENTERSRateSchedule:CAREConsumption:Bin2': 200566, 'Tenure:RENTERSRateSchedule:CAREConsumption:Bin5': 20924, 'Tenure:RENTERSRateSchedule:CAREConsumption:Bin4': 50262, 'Tenure:RENTERSRateSchedule:CAREConsumption:Bin6': 13756, 'Tenure:RENTERSRateSchedule:NONCAREConsumption:Bin6': 14800, 'Tenure:RENTERSRateSchedule:NONCAREConsumption:Bin5': 19499, 'Tenure:RENTERSRateSchedule:NONCAREConsumption:Bin4': 47204, 'Tenure:RENTERSRateSchedule:NONCAREConsumption:Bin3': 108252, 'Tenure:RENTERSRateSchedule:NONCAREConsumption:Bin2': 210049, 'Tenure:RENTERSRateSchedule:NONCAREConsumption:Bin1': 151708}

total_population = 0
for count in category_count_dct.itervalues():
    total_population += count

tenure_rate_ratio = {}
tenure_rate_bin_ratio = {}
household_number = 1

for consumption_category, customer_count in category_count_dct.iteritems(): 
    household_tenure = get_middle_text(consumption_category, 'Tenure:', 'RateSchedule:')
    consumption_bin = int(float(get_middle_text(consumption_category, 'Consumption:Bin', '<')))
    rate = get_middle_text(consumption_category, 'RateSchedule:', 'Consumption:')
    rate_schedule_str = 'Schedule D'
    if re.search('NONCARE', rate) == None:
        rate_schedule_str = 'Schedule D CARE'

#     key1 = household_tenure + rate_schedule_str
#     if key1 in tenure_rate_ratio.keys():
#         tenure_rate_ratio[key1] += customer_count
#     else:
#         tenure_rate_ratio[key1] = customer_count
#         
    key2 = household_tenure + rate_schedule_str 
    if key2 in tenure_rate_bin_ratio.keys():
        tenure_rate_bin_ratio[key2][consumption_bin - 1] += customer_count
    else:
        tenure_rate_bin_ratio[key2] = [0] * 6
        tenure_rate_bin_ratio[key2][consumption_bin - 1] += customer_count

testing = 0
for key, value in tenure_rate_bin_ratio.iteritems():
    category_pop = sum(value)
    testing += value[2]
    temp = [0.0] * 6
    for i in range(len(value)):
        temp[i] = float(value[i]) / category_pop
    print key, value[2], temp, category_pop

print testing
    
# percent = 0.0  
# for key, value in tenure_rate_ratio.iteritems():
#     v = float(value) / total_population
#     print key, v
#     percent += v
# print percent, total_population
            
