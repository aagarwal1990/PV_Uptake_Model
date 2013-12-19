
from __future__ import division
from sim_structure import Simulator, Aggregator
from sce_non_agent_specs import Trace, \
                                BaselineRegion, \
                                TierNetMeterBill, \
                                CustomerAccount, \
                                TierNetMeterRateSchedule, \
                                PvTechnology, \
                                PvInstaller
from sce_agent_specs import SimulatorClock, ResidentialCustomer, Utility
import sce_settings
import unittest
import logging
import logging.config
import yaml
import spec_parser
import time

def run_1():
    logging.config.dictConfig(yaml.load(open('log_specs.yaml', 'r')))
    test_parser = spec_parser.specparser()
    print "Parsing YAML specs"
    start = time.clock()
    test_parser.main()
    print "Completed parsing of YAML specs in " + str(time.clock() - start) + " seconds"
    print "Running simulation"
    start = time.clock()
    test_parser.simulator.execute(time_horizon = 72)
    print "Completed simulation in " + str(time.clock() - start) + " seconds"

if __name__ == '__main__':
    run_1()

#    a = time_graph('technology_quantity', 'time', 'cumulative')
#    a.main()
#    print a.graph_list_of_tups
    
    