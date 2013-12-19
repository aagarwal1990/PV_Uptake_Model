from __future__ import division
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
import unittest
import logging
import logging.config
import yaml
import sce_simulation_init

"""

class TestSceSettings(unittest.TestCase):
    
    def test_global_constants(self):
        print '\n-----------------------------------------------------'
        print 'PRINTING GLOBAL CONSTANTS...\n'
        print "NUMBER_OF_HOURS_IN_EACH_MONTH:", sce_settings.NUMBER_OF_HOURS_IN_EACH_MONTH
        print "NUMBER_OF_MINUTES_IN_EACH_MONTH:", sce_settings.NUMBER_OF_MINUTES_IN_EACH_MONTH
        print "NUMBER_OF_SECONDS_IN_EACH_MONTH:", sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH
        print "FIRST_DAY_OF_EACH_MONTH:", sce_settings.FIRST_DAY_OF_EACH_MONTH
        print "FIRST_HOUR_OF_EACH_MONTH:", sce_settings.FIRST_HOUR_OF_EACH_MONTH
        print "FIRST_MINUTE_OF_EACH_MONTH:", sce_settings.FIRST_MINUTE_OF_EACH_MONTH
        print "FIRST_SECOND_OF_EACH_MONTH:", sce_settings.FIRST_SECOND_OF_EACH_MONTH
        sce_settings.set_time_axis(sample_interval = sce_settings.SAMPLE_EVERY_MONTH, sample_length_in_years = 1)
        print "TICK_VALUES:", sce_settings.TICK_VALUES
        print "TICK_INTERVALS:", sce_settings.TICK_INTERVALS
        print "FIRST_INDEX_OF_MONTH:", sce_settings.FIRST_INDEX_OF_MONTH
        print "FIRST_INDEX_OF_YEAR:", sce_settings.FIRST_INDEX_OF_YEAR
        print '\nFINISHED PRINTING GLOBAL CONSTANTS...'
        print '-----------------------------------------------------\n'


class TestTrace(unittest.TestCase):
    
    def setUp(self):
        sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 20)
        self.time_trace_1 = Trace(range(1,13), 0)
        self.time_trace_2 = Trace(range(2,14), 0)
        self.time_trace_3 = Trace(range(1,13), 12)
    
    def test_getter_and_setter(self):
        print '\n-----------------------------------------------------'
        print 'TESTING Trace getter and setter...\n'
        s = sce_settings.FIRST_SECOND_OF_EACH_MONTH
        self.assertEqual(self.time_trace_1.get_list_of_times(), s[0:12])
        self.assertEqual(self.time_trace_1.get_list_of_values(), range(1,13))
        self.assertEqual(self.time_trace_1.get_start_time(), 0)
        self.assertEqual(self.time_trace_1.get_end_time(), s[12])
        self.assertEqual(self.time_trace_3.get_start_month(), 12)
        self.assertEqual(self.time_trace_3.get_end_month(), 24)
        self.assertEqual(self.time_trace_1.get_value_at_time(s[0]), 1)
        self.assertEqual(self.time_trace_1.get_value_at_time(s[1]), 2)
        self.assertEqual(self.time_trace_1.get_value_at_time(s[1]-1), 1)
        self.assertEqual(self.time_trace_1.get_value_at_time(s[12]-1), 12)
        self.assertEqual(self.time_trace_1.get_integral(), sum([x * y for (x,y) in zip(range(1,13),sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)]))
        self.assertEqual(self.time_trace_1.get_integral_over_time(0, s[1]),s[1])
        self.assertEqual(self.time_trace_1.get_integral_over_time(s[1],s[2]), sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[1] * 2)
        self.assertEqual(self.time_trace_1.get_integral_over_time(s[1]-1,s[1]), 1)
        self.assertEqual(self.time_trace_1.get_integral_over_time(s[1]+1,s[1]+2), 2)
        self.assertEqual(self.time_trace_1.get_integral_over_time(s[12]-1,s[12]), 12)
        self.assertEqual(self.time_trace_1.get_trace_over_time(0,s[1]).get_list_of_times(), [0])
        self.assertEqual(self.time_trace_1.get_trace_over_time(0,s[1]).get_list_of_values(), [1])
        self.assertEqual(self.time_trace_1.get_trace_over_time(s[1],s[2]).get_list_of_times(), [s[1]])
        self.assertEqual(self.time_trace_1.get_trace_over_time(s[1],s[2]).get_list_of_values(), [2])
        print '\nFINISHED TESTING Trace getter and setter...'
        print '-----------------------------------------------------\n'
        
    def test_modification_methods(self):
        print '\n-----------------------------------------------------'
        print 'TESTING Trace modification methods...\n'
        s = sce_settings.FIRST_SECOND_OF_EACH_MONTH
        self.assertEqual(self.time_trace_1.append_trace(self.time_trace_3).get_list_of_times(), s[:] + [x + sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR for x in s[1:-1]])
        self.assertEqual(self.time_trace_1.get_list_of_values(), range(1,13) + range(1,13))
        t = self.time_trace_1.remove_trace_before_time(sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR)
        self.assertEqual(t.get_list_of_times(), s[0:12])
        self.assertEqual(t.get_list_of_values(), range(1,13))
        self.assertEqual(self.time_trace_1.get_list_of_times(), [x + sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR for x in s[0:12]])
        self.assertEqual(self.time_trace_1.get_list_of_values(), range(1,13))
        self.time_trace_1 = t
        t = self.time_trace_1 + self.time_trace_2
        self.assertEqual(t.get_integral(), self.time_trace_1.get_integral() + self.time_trace_2.get_integral())
        t = self.time_trace_1 - self.time_trace_2
        self.assertEqual(t.get_integral(), self.time_trace_1.get_integral() - self.time_trace_2.get_integral())
        t = self.time_trace_1 * self.time_trace_2
        self.assertEqual(t.get_integral(), Trace([x * y for (x,y) in zip(range(1,13),range(2,14))],0).get_integral())
        self.time_trace_1 = Trace(range(1,13), 0)
        self.time_trace_2 = Trace(range(2,14), 0)        
        self.time_trace_1.set_value_at_time(0, sce_settings.FIRST_SECOND_OF_EACH_MONTH[1], 0)        
        self.assertEqual(self.time_trace_1.get_value_at_time(0), 0)
        self.time_trace_1.set_value_at_time(0, sce_settings.FIRST_SECOND_OF_EACH_MONTH[1], 1)
        # test empty trace representation
        empty_trace = Trace([], 12)
        self.assertEqual(empty_trace.get_end_time(), sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR)
        self.time_trace_1.append_trace(empty_trace)
        self.assertEqual(self.time_trace_1.get_integral(), sum([x * y for (x,y) in zip(range(1,13),sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)]))
        empty_trace = Trace([], 0)
        empty_trace.append_trace(self.time_trace_1)
        self.assertEqual(empty_trace.get_integral(), sum([x * y for (x,y) in zip(range(1,13),sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH)]))
        t = self.time_trace_1.remove_trace_before_time(sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR)
        self.assertEqual(self.time_trace_1.get_list_of_times(),[])
        self.assertEqual(self.time_trace_1.get_list_of_values(),[])
        self.time_trace_1 = t
        self.time_trace_1.remove_trace_before_time(0)
        self.assertEqual(self.time_trace_1.get_list_of_times(),sce_settings.FIRST_SECOND_OF_EACH_MONTH[0:12])
        self.assertEqual(self.time_trace_1.get_list_of_values(),range(1,13))
        print '\nFINISHED TESTING Trace modification methods...'
        print '-----------------------------------------------------\n'


class TestBaselineRegion(unittest.TestCase):
    
    def setUp(self):
        sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 20)
        self.baseline_region = BaselineRegion('Zone 1', summer_baseline_in_kwh_per_day = 10*3600*24, winter_baseline_in_kwh_per_day = 1*3600*24)
    
    def test_getter_and_setter(self):
        print '\n-----------------------------------------------------'
        print 'TESTING BaselineRegion getter and setter...\n'
        b = self.baseline_region
        self.assertEqual(b.get_name(), 'Zone 1')
        self.assertEqual(b.get_customer_account_list(), [])
        t = b.get_baseline_allocation()
        self.assertEqual(t.get_value_at_time(0), 1)
        self.assertEqual(t.get_value_at_time(sce_settings.FIRST_SECOND_OF_SUMMER), 10)
        self.assertEqual(t.get_value_at_time(sce_settings.FIRST_SECOND_OF_WINTER), 1)
        self.assertEqual(t.get_value_at_time(sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR), 1)
        self.assertEqual(t.get_value_at_time(sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR + sce_settings.FIRST_SECOND_OF_SUMMER), 10)
        self.assertEqual(t.get_value_at_time(sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR + sce_settings.FIRST_SECOND_OF_WINTER), 1)
        a = b.get_baseline_allocation_for_period(sce_settings.FIRST_SECOND_OF_EACH_MONTH[1],sce_settings.FIRST_SECOND_OF_EACH_MONTH[2])
        self.assertEqual(a, sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[1] * 1)
        a = b.get_baseline_allocation_for_period(sce_settings.FIRST_SECOND_OF_SUMMER - 1, sce_settings.FIRST_SECOND_OF_SUMMER)
        self.assertEqual(a, 1)
        a = b.get_baseline_allocation_for_period(sce_settings.FIRST_SECOND_OF_SUMMER, sce_settings.FIRST_SECOND_OF_SUMMER + 1)
        self.assertEqual(a, 10)
        r = TierNetMeterRateSchedule('Schedule D', 
                                     {'basic_charge': 1, 
                                      'tiered_variable_charge': [0.10, 0.20, 0.30, 0.40], 
                                      'net_surplus_compensation_rate': 0.05},
                                     {'annual_percent_increase_in_tier_1': 1.03,
                                      'annual_percent_increase_in_tier_2': 1.03,
                                      'difference_between_tier_3_and_4': 0.40})
        c = CustomerAccount('Desmond', baseline_region = b, current_rate_schedule = r)
        b.add_customer_account(c)
        self.assertEqual(b.get_customer_account_list()[0], c)
        print '\nFINISHED TESTING BaselineRegion getter and setter...'
        print '-----------------------------------------------------\n'
        
    def test_update_baseline_allocation(self):
        print '\n-----------------------------------------------------'
        print 'TESTING BaselineRegion update_baseline_allocation...\n'
        self.baseline_region.update_baseline_allocation(3, summer_baseline_in_kwh_per_day = 1*3600*24, winter_baseline_in_kwh_per_day = 10*3600*24)
        t = self.baseline_region.get_baseline_allocation()
        self.assertEqual(t.get_value_at_time(sce_settings.FIRST_SECOND_OF_EACH_MONTH[0]),10)
        self.assertEqual(t.get_value_at_time(sce_settings.FIRST_SECOND_OF_EACH_MONTH[3]),10)
        self.assertEqual(t.get_value_at_time(sce_settings.FIRST_SECOND_OF_EACH_MONTH[5]),1)
        self.assertEqual(t.get_value_at_time(sce_settings.FIRST_SECOND_OF_EACH_MONTH[8]),1)
        self.assertEqual(t.get_value_at_time(sce_settings.FIRST_SECOND_OF_EACH_MONTH[9]),10)
        print '\nFINISHED TESTING BaselineRegion update_baseline_allocation...'
        print '-----------------------------------------------------\n'
        
        
class TestTierNetMeterRateSchedule(unittest.TestCase):
    
    def setUp(self):
        sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 20)
        self.rate_schedule = TierNetMeterRateSchedule('Schedule D', 
                                                      {'basic_charge': 1, 
                                                       'tiered_variable_charge': [0.10, 0.20, 0.30, 0.40], 
                                                       'net_surplus_compensation_rate': 0.05},
                                                      {'annual_percent_increase_in_tier_1': 1.03,
                                                       'annual_percent_increase_in_tier_2': 1.03,
                                                       'difference_between_tier_3_and_4': 0.40})
    
    def test_getter_and_setter(self):
        print '\n-----------------------------------------------------'
        print 'TESTING TierNetMeterRateSchedule getter and setter...\n'
        r = self.rate_schedule
        self.assertEqual(r.get_name(), 'Schedule D')
        self.assertEqual(r.get_basic_charge(), 1)
        self.assertEqual(r.get_tiered_variable_charge(), [0.10, 0.20, 0.30, 0.40])
        self.assertEqual(r.get_net_surplus_compensation_rate(), 0.05)
        r.set_basic_charge(2)
        r.set_tiered_variable_charge([0.20, 0.30, 0.40, 0.50])
        r.set_net_surplus_compensation_rate(0.10)
        self.assertEqual(r.get_basic_charge(),2)
        self.assertEqual(r.get_tiered_variable_charge(), [0.20, 0.30, 0.40, 0.50])
        self.assertEqual(r.get_net_surplus_compensation_rate(), 0.10)
        print '\nFINISHED TESTING TierNetMeterRateSchedule getter and setter...'
        print '-----------------------------------------------------\n'
        
    def test_generate_utility_bill(self):
        print '\n-----------------------------------------------------'
        print 'TESTING TierNetMeterRateSchedule generate_utility_bill...\n'
        time_trace_1 = Trace(range(1,13), 0)
        baseline_region = BaselineRegion('Zone 1', summer_baseline_in_kwh_per_day = 10*3600*24, winter_baseline_in_kwh_per_day = 1*3600*24)
        bill = TierNetMeterBill('Desmond', -1, {'month_of_relevant_period' : 12,
                                            'usage' : 0,
                                            'cumulative_usage_charge_over_current_relevant_period' : 0,
                                            'cumulative_usage_over_current_relevant_period' : 100,
                                            'baseline_allocation_for_this_month' : 0,
                                            'units_of_basic_charge' : 0,
                                            'units_of_tiered_variable_charge' : 0,
                                            'units_of_net_surplus_compensation' : 0,
                                            'total_basic_charge' : 0,
                                            'total_tiered_variable_charge' : 0,
                                            'basic_charge' : 0,
                                            'tiered_variable_charge' : 0,
                                            'net_surplus_compensation_rate' : 0})
        b = self.rate_schedule.generate_utility_bill('Desmond', 
                                                     time_trace_1, 
                                                     baseline_region.get_baseline_allocation(),
                                                     0, 
                                                     bill)
        usage = sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[0]
        baseline = sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[0]
        self.assertEqual(baseline, usage)
        self.assertEqual(b.get_customer_name(),'Desmond')
        self.assertEqual(b.get_month_of_billing_period(),0)
        self.assertEqual(b.get_usage(), usage)
        self.assertEqual(b.get_cumulative_usage_charge_over_current_relevant_period(), usage * 0.10)
        self.assertEqual(b.get_cumulative_usage_over_current_relevant_period(), usage)
        self.assertEqual(b.get_baseline_allocation_for_this_month(), baseline)
        self.assertEqual(b.get_units_of_basic_charge(), sce_settings.NUMBER_OF_DAYS_IN_EACH_MONTH[0])
        self.assertEqual(b.get_units_of_tiered_variable_charge(), [usage, 0, 0, 0])
        self.assertEqual(b.get_units_of_net_surplus_compensation(), 0)
        self.assertEqual(b.get_basic_charge(), 1)
        self.assertEqual(b.get_tiered_variable_charge(), [0.10, 0.20, 0.30, 0.40])
        self.assertEqual(b.get_net_surplus_compensation_rate(), 0.05)
        # test net_surplus_compensation calculations
        bill = TierNetMeterBill('Desmond', 4, {'month_of_relevant_period' : 11,
                                            'usage' : 0,
                                            'cumulative_usage_charge_over_current_relevant_period' : - sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 6 * 0.10,
                                            'cumulative_usage_over_current_relevant_period' : - sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 6 - 100,
                                            'baseline_allocation_for_this_month' : 0,
                                            'units_of_basic_charge' : 0,
                                            'units_of_tiered_variable_charge' : 0,
                                            'units_of_net_surplus_compensation' : 0,
                                            'total_basic_charge' : 0,
                                            'total_tiered_variable_charge' : 0,
                                            'basic_charge' : 0,
                                            'tiered_variable_charge' : 0,
                                            'net_surplus_compensation_rate' : 0})                                
        b = self.rate_schedule.generate_utility_bill('Desmond', 
                                                     time_trace_1, 
                                                     baseline_region.get_baseline_allocation(),
                                                     5, 
                                                     bill)
        usage = sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 6
        baseline = sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 10
        self.assertEqual(b.get_usage(), usage)
        self.assertEqual(b.get_cumulative_usage_over_current_relevant_period(), -100)
        self.assertEqual(b.get_units_of_net_surplus_compensation(), 100)
        self.assertEqual(b.get_units_of_basic_charge(), sce_settings.NUMBER_OF_DAYS_IN_EACH_MONTH[5])
        self.assertEqual(b.get_cumulative_usage_charge_over_current_relevant_period(), -100 * 0.05)
        # test tiered charge calculations
        baseline_region = BaselineRegion('Zone 1', summer_baseline_in_kwh_per_day = 1*3600*24, winter_baseline_in_kwh_per_day = 1*3600*24)
        bill = TierNetMeterBill('Desmond', 4, {'month_of_relevant_period' : 6,
                                            'usage' : 0,
                                            'cumulative_usage_charge_over_current_relevant_period' : - sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 6 * 0.10,
                                            'cumulative_usage_over_current_relevant_period' : - sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 6 - 100,
                                            'baseline_allocation_for_this_month' : 0,
                                            'units_of_basic_charge' : 0,
                                            'units_of_tiered_variable_charge' : 0,
                                            'units_of_net_surplus_compensation' : 0,
                                            'total_basic_charge' : 0,
                                            'total_tiered_variable_charge' : 0,
                                            'basic_charge' : 0,
                                            'tiered_variable_charge' : 0,
                                            'net_surplus_compensation_rate' : 0})                                
        b = self.rate_schedule.generate_utility_bill('Desmond', 
                                                     time_trace_1, 
                                                     baseline_region.get_baseline_allocation(),
                                                     5, 
                                                     bill)
        usage = sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 6
        baseline = sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 1
        self.assertEqual(b.get_usage(), usage)
        self.assertEqual(b.get_units_of_tiered_variable_charge(),[baseline, 0.3 * baseline, 0.7 * baseline, usage - 2 * baseline])
        self.assertEqual(b.get_cumulative_usage_charge_over_current_relevant_period(), baseline * 0.10 + 0.3 * baseline * 0.20 + 0.7 * baseline * 0.30 + (usage - 2 * baseline) * 0.40 - sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[5] * 6 * 0.10 )
        print '\nFINISHED TESTING TierNetMeterRateSchedule generate_utility_bill...'
        print '-----------------------------------------------------\n'
        
    def test_calculate_total_charge(self):
        print '\n-----------------------------------------------------'
        print 'TESTING TierNetMeterRateSchedule calculate_total_charge...\n'
        time_trace_1 = Trace(range(1,13), 0)
        baseline_region = BaselineRegion('Zone 1', summer_baseline_in_kwh_per_day = 20*3600*24, winter_baseline_in_kwh_per_day = 20*3600*24)
        c = self.rate_schedule.calculate_monthly_charge(time_trace_1, baseline_region.get_baseline_allocation(), 0, 12)
        self.assertEqual(sum(c), time_trace_1.get_integral() * 0.10 + sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR)
        print '\nFINISHED TESTING TierNetMeterRateSchedule calculate_total_charge...'
        print '-----------------------------------------------------\n'

        
class TestCustomerAccount(unittest.TestCase):
    
    def setUp(self):
        sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 20)
        self.baseline_region = BaselineRegion('Zone 1', summer_baseline_in_kwh_per_day = 20, winter_baseline_in_kwh_per_day = 20)
        self.rate_schedule = TierNetMeterRateSchedule('Schedule D', 
                                                      {'basic_charge': 1, 
                                                       'tiered_variable_charge': [0.10, 0.20, 0.30, 0.40], 
                                                       'net_surplus_compensation_rate': 0.05},
                                                      {'annual_percent_increase_in_tier_1': 1.03,
                                                       'annual_percent_increase_in_tier_2': 1.03,
                                                       'difference_between_tier_3_and_4': 0.40})
        self.account = CustomerAccount('Desmond', baseline_region = self.baseline_region, current_rate_schedule = self.rate_schedule)
    
    def test_getter_and_setter(self):
        print '\n-----------------------------------------------------'
        print 'TESTING CustomerAccount getter and setter...\n'
        a = self.account
        self.assertEqual(a.get_customer_account_number(), 'Desmond')
        self.assertEqual(a.get_baseline_region(), self.baseline_region)
        self.assertEqual(a.get_current_rate_schedule(), self.rate_schedule)
        self.assertRaises(KeyError, a.get_bill, 1)
        a.add_note('first_month_of_relevant_period', 1)
        time_trace_1 = Trace([1], 0)
        a.add_load_profile(time_trace_1)
        self.assertEqual(a.get_bill(0).get_cumulative_usage_over_current_relevant_period(),sce_settings.FIRST_SECOND_OF_EACH_MONTH[1])
        self.assertRaises(KeyError, a.get_bill, 1)
        time_trace_1 = Trace([2],1)
        a.add_load_profile(time_trace_1)
        self.assertEqual(a.get_bill(1).get_cumulative_usage_over_current_relevant_period(),sce_settings.FIRST_SECOND_OF_EACH_MONTH[1] + (sce_settings.FIRST_SECOND_OF_EACH_MONTH[2] - sce_settings.FIRST_SECOND_OF_EACH_MONTH[1]) * 2)
        print '\nFINISHED TESTING CustomerAccount getter and setter...'
        print '-----------------------------------------------------\n'


class TestPvTechnology(unittest.TestCase):
    
    def setUp(self):
        sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 20)
        efficiency = Trace([0.9] * 12, 0)
        self.pv = PvTechnology('Pv',{'quantity': 2, 
                                     'purchase_month': 1,
                                     'lifetime_in_months': 10,
                                     'initial_payment': 0,
                                     'monthly_payment': 100,
                                     'conversion_factor': 1,
                                     'efficiency': efficiency})              
        
    def test_getter_and_setter(self):
        print '\n-----------------------------------------------------'
        print 'TESTING PvTechnology getter and setter...\n'
        self.assertEqual(self.pv.get_quantity(), 2)
        self.assertEqual(self.pv.get_purchase_month(), 1)
        self.assertEqual(self.pv.get_lifetime_in_months(), 10)
        self.assertEqual(self.pv.get_initial_payment(), 0)
        self.assertEqual(self.pv.get_monthly_payment(), 100)
        self.assertEqual(self.pv.get_efficiency_at_time(sce_settings.FIRST_SECOND_OF_EACH_MONTH[1]),0.9)
        print '\nFINISHED TESTING PvTechnology getter and setter...'
        print '----------------------------------------------------\n'

    def test_get_reduction_in_load(self):
        print '\n-----------------------------------------------------'
        print 'TESTING PvTechnology get_reduction_in_load...\n'
        solar_intensity_profile = Trace(range(0,12),0)
        reduction_in_load = self.pv.get_reduction_in_load_over_time_index(1, 11, {'solar_intensity_profile': solar_intensity_profile})
        self.assertEqual(reduction_in_load.get_integral(), sum( 0.9 * 2 * x * y for (x,y) in zip(sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[1:11],range(1,11))))
        print '\nFINISHED TESTING PvTechnology get_reduction_in_load...'
        print '-----------------------------------------------------\n'
        

class TestPvInstaller(unittest.TestCase):
    
    def setUp(self):
        sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 20)
        efficiency = Trace([1.0] * 12, 0)
        cost_per_kw = Trace(range(1,13), 0)
        self.pv_installer = PvInstaller('pv installer', {'kw_per_panel': 0.2,
                                           'minimum_number_of_panels': 5,
                                           'maximum_number_of_panels': 20,
                                           'conversion_factor': 1,
                                           'efficiency': efficiency,
                                           'cost_per_kw': cost_per_kw,
                                           'term_in_months': 12,
                                           'annual_interest_rate': 5})
        
    def test_getter_and_setter(self):
        print '\n-----------------------------------------------------'
        print 'TESTING PvInstaller getter and setter...\n'
        self.assertEqual(self.pv_installer.get_kw_per_panel(), 0.2)
        self.assertEqual(self.pv_installer.get_minimum_number_of_panels(), 5)
        self.assertEqual(self.pv_installer.get_maximum_number_of_panels(), 20)
        self.assertEqual(self.pv_installer.get_term_in_months(), 12)
        self.assertEqual(self.pv_installer.get_annual_interest_rate(), 5)
        self.assertEqual(self.pv_installer.get_efficiency_at_time(sce_settings.FIRST_SECOND_OF_EACH_MONTH[1]),1.0)
        self.assertEqual(self.pv_installer.get_cost_per_kw(sce_settings.FIRST_SECOND_OF_EACH_MONTH[1]),2)
        print '\nFINISHED TESTING PvInstaller getter and setter...'
        print '-----------------------------------------------------\n'
        
    def test_get_recommended_quantity(self):
        print '\n-----------------------------------------------------'
        print 'TESTING PvInstaller get_recommended_quantity...\n'
        load_profile = Trace(range(0,12), 0)
        baseline_allocation = Trace([1] * 12, 0)
        rate_schedule = TierNetMeterRateSchedule('Schedule D', 
                                                 {'basic_charge': 1, 
                                                  'tiered_variable_charge': [0.10, 0.20, 0.30, 0.40], 
                                                  'net_surplus_compensation_rate': 0.05},
                                                 {'annual_percent_increase_in_tier_1': 1.03,
                                                  'annual_percent_increase_in_tier_2': 1.03,
                                                  'difference_between_tier_3_and_4': 0.40})
        solar_intensity_profile = Trace(range(0,12), 0)
        (technology, savings) = self.pv_installer.get_recommended_quantity_at_time_index(0, load_profile, baseline_allocation, rate_schedule, {'solar_intensity_profile': solar_intensity_profile})
        self.assertEqual(technology.get_quantity(), 4)
        print '\nFINISHED TESTING PvInstaller get_recommended_quantity...'
        print '-----------------------------------------------------\n'

"""

# class TestSimulatorClock(unittest.TestCase):
#     
#     def setUp(self):
#         sce_settings.set_time_axis(sce_settings.SAMPLE_EVERY_MONTH, 20)
#         self.simulator = Simulator()
#         SimulatorClock(name = 'clock', simulator = self.simulator)
#         
#     def test_simulator_clock(self):
#         print '\n-----------------------------------------------------'
#         print 'TESTING SimulatorClock...\n'
#         self.simulator.execute(time_horizon = 4)
#         print '\nFINISHED TESTING SimulatorClock...'
#         print '-----------------------------------------------------\n'
# 


''' This dictionary is what will persist in the GAE datastore upon the completion of a 
    simulation run '''
    
simulation_dct = {}

class TestAgents(unittest.TestCase):    
    def setUp(self):
       self.test_parser = sce_simulation_init.specparser()
       self.test_parser.main()
       
    def test_agents(self):
        print '\n-----------------------------------------------------'
        print 'TESTING Main Simulation...\n'
#         self.simulator.execute(time_horizon = 24)
        simulation_dct['test_ID'] = self.test_parser.simulator.execute(time_horizon = 60)
        print '\nFINISHED TESTING Main Simulation...'
        print '-----------------------------------------------------\n'
#         acc = self.utility.get_customer_category_account('Customer_0000')
#         acc = self.test_parser.utility_dictionary['utility'].get_customer_category_account('Customer_0000')
        usage_for_each_month = [x * 10000 / sce_settings.NUMBER_OF_SECONDS_IN_ONE_YEAR for x in sce_settings.NUMBER_OF_SECONDS_IN_EACH_MONTH[0:4]]
        total_baseline_allocation_for_each_month = [x * 20000 / sce_settings.NUMBER_OF_DAYS_IN_ONE_YEAR for x in sce_settings.NUMBER_OF_DAYS_IN_EACH_MONTH[0:4]]
        units_of_tiered_usage_for_each_month = [[sce_settings.sign(usage) * min(abs(usage), total_baseline_allocation_for_whole_month), \
                                                 sce_settings.sign(usage) * max(0, min(abs(usage) - total_baseline_allocation_for_whole_month, 0.30 * total_baseline_allocation_for_whole_month)), \
                                                 sce_settings.sign(usage) * max(0, min(abs(usage) - 1.3 * total_baseline_allocation_for_whole_month, 0.70 * total_baseline_allocation_for_whole_month)), \
                                                 sce_settings.sign(usage) * max(0, abs(usage) - 2.0 * total_baseline_allocation_for_whole_month)] for (usage,total_baseline_allocation_for_whole_month) in zip(usage_for_each_month,total_baseline_allocation_for_each_month)]

# RUN SIMULATION
logging.config.dictConfig(yaml.load(open('log_specs.yaml', 'r')))
unittest.main(module=__name__, buffer=False, exit=False)






#        for i in range(120):
#            print acc.get_bill(i).get_usage()
"""
        for i in range(4):
            self.assertEqual(acc.get_bill(i).get_month_of_billing_period(),i)
            self.assertEqual(acc.get_bill(i).get_month_of_relevant_period(),i+1)
            self.assertEqual(round(acc.get_bill(i).get_usage(),2),round(usage_for_each_month[i],2))
            self.assertEqual(acc.get_bill(i).get_cumulative_usage_charge_over_current_relevant_period(),sum([sum([x * y for (x,y) in zip([0.10,0.20,0.30,0.40],units_of_tiered_usage_for_each_month[j])]) for j in range(i+1)]))
            self.assertEqual(acc.get_bill(i).get_cumulative_usage_over_current_relevant_period(),sum(usage_for_each_month[0:i+1]))
            self.assertEqual(round(acc.get_bill(i).get_baseline_allocation_for_this_month(),2),round(total_baseline_allocation_for_each_month[i],2))
            self.assertEqual(acc.get_bill(i).get_units_of_basic_charge(),sce_settings.NUMBER_OF_DAYS_IN_EACH_MONTH[i])
            self.assertEqual([round(x,2) for x in acc.get_bill(i).get_units_of_tiered_variable_charge()],[round(x,2) for x in units_of_tiered_usage_for_each_month[i]])
            self.assertEqual(acc.get_bill(i).get_units_of_net_surplus_compensation(),0)
            self.assertEqual(acc.get_bill(i).get_total_basic_charge(),sce_settings.NUMBER_OF_DAYS_IN_EACH_MONTH[i])
            self.assertEqual(acc.get_bill(i).get_basic_charge(), 1)
            self.assertEqual(round(acc.get_bill(i).get_total_tiered_variable_charge(),2), sum([round(x * y,2) for (x,y) in zip([0.10,0.20,0.30,0.40],units_of_tiered_usage_for_each_month[i])]))
            self.assertEqual(acc.get_bill(i).get_tiered_variable_charge(), [0.10,0.20,0.30,0.40])
            self.assertEqual(acc.get_bill(i).get_net_surplus_compensation_rate(), 0.05)
"""

# if __name__ == '__main__':
#     
# #    main()
# #    assert not hasattr(sys.stdout, "getvalue")

#        output = sys.stdout.getvalue().strip()
