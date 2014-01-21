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
        simulation_dct['test_ID'] = self.test_parser.simulator.execute(time_horizon = 36)
        print '\nFINISHED TESTING Main Simulation...'
        print '-----------------------------------------------------\n'

# RUN SIMULATION
logging.config.dictConfig(yaml.load(open('log_specs.yaml', 'r')))
unittest.main(module=__name__, buffer=False, exit=False)
