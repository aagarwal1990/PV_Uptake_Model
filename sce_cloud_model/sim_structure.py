'''
Created on Apr 18, 2013

@author: mani
'''
#!/usr/bin/env python
'''
This module contains classes that define the structure of this time-stepped simulator.
              

'''
import logging
import logging.config
import traceback, sys

class WriteVariable(object):
    
    def __init__(self, writing_agent, write_variable_name):
        if writing_agent is None:
            error_line = ('Error in WriteVariable initialization: writing_agent is None')
            raise Exception(error_line)
        if write_variable_name is None: 
            error_line = ('Error in WriteVariable initialization: write_variable_name is None')
            raise Exception(error_line)
        self.writing_agent = writing_agent
        self.write_variable_name = write_variable_name
        self.__name__ = writing_agent.__name__ + ' : ' + write_variable_name
        
    def set(self, new_value):
        self.writing_agent.write(self.write_variable_name, new_value)
        
    def write(self, new_value):
        self.writing_agent.write(self.write_variable_name, new_value)
        
    def get(self):
        error_line = ('Error: Cannot read a write variable\n' 
              + 'Agent name: ' + '%s\n' % (str(self.writing_agent.__name__))
              + 'Variable name: ' + str(self.write_variable_name))
        raise Exception(error_line)
                
    def read(self):
        error_line = ('Error: Cannot read a write variable\n' 
              + 'Agent name: ' + '%s\n' % (str(self.writing_agent.__name__))
              + 'Variable name: ' + str(self.write_variable_name))
        raise Exception(error_line)
              
        
class ReadVariable(object):
    
    def __init__(self, reading_agent, read_variable_name):
        if reading_agent is None:
            error_line = ('Error in ReadVariable initialization: reading_agent is None')
            raise Exception(error_line)
        if read_variable_name is None:
            error_line = ('Error in ReadVariable initialization: read_variable_name is None')
            raise Exception(error_line)            
        self.reading_agent = reading_agent
        self.read_variable_name = read_variable_name
        self.__name__ = reading_agent.__name__ + ' : ' + read_variable_name
        
    def set(self, new_value):
        error_line = ('Error: Cannot write a read variable\n' 
              + 'Agent name: ' + '%s\n' % (str(self.reading_agent.__name__))
              + 'Variable name: ' + str(self.read_variable_name))
        raise Exception(error_line)
        
    def write(self, new_value):
        error_line = ('Error: Cannot write a read variable\n' 
              + 'Agent name: ' + '%s\n' % (str(self.reading_agent.__name__))
              + 'Variable name: ' + str(self.read_variable_name))
        raise Exception(error_line)
        
    def get(self):
        return self.reading_agent.read(self.read_variable_name)
    
    def read(self):
        return self.reading_agent.read(self.read_variable_name)
        
        
class Agent(object):
    """
    An abstract class for an agent. Agent classes in applications are subclasses of this class. 
    
    
    Attributes
    ----------
    __name__ : str
               The name of the agent.
    parameter_dictionary : dict
               Each agent has a collection of named parameters stored in parameter_dictionary.
               The parameters may or may not be used in an application.
    simulator: Simulator
               Each agent executes within a simulator. 
               The main program may execute multiple simulators concurrently.
    write_variables : dict
               An agent writes values into its write variables at each time step. 
               The value written could be None to signify no output on a given time step.
               write_variables[write_variable_name] is the write variable object with the specified name.
    read_variables : dict
               An agent reads values from its read variables at each time step.
               If the value read is None then that signifies no input in that times step.
               read_variables[read_variable_name] is the read variable object with the specified name.
    
    """
    
    def __init__(self, name, simulator = None, parameter_dictionary = None):
        self.__name__ = self.name = name
        self.parameter_dictionary = parameter_dictionary
        self.simulator = simulator
        self.simulator.register_agent(self)
        self.write_variables = dict()
        self.read_variables = dict()

        # Every agent that runs within a simulator must be registered with that simulator.
    
        
              
    def step_forward(self):
        """
        Update the agent's local state and assign write variables as time moves forward by one step, .
        
        """
    
    def step_write_variables_forward(self):
        """
        Update the agent's write variables forward by one step.
        
        A write variable has two components: a value read and the value
        written (concurrently) in a given time step. When the agents
        have written and read values of these (shared) variables,
        this method sets the state of this variable for the 
        next iteration.
        
        """
        
        for write_variable in self.write_variables.values():
            write_variable.step_forward()
            
    def create_write_variable(self, write_variable_name, initial_value = None):
        """
        Create a new write variable for this agent with the specified name.
        
        The new write variable is a SharedVariable object that can be
        written by this agent, and this agent only, but can be read by
        any number of agents.
        
        Initialize the value of the write variable to initial_value
        
        """
        if write_variable_name is None:
            error_line = ('ERROR in Agent.create_write_variable(), write_variable_name is None')
            raise Exception(error_line)
        shared_variable_for_write_variable = SharedVariable(write_variable_name, writing_agent_name = self.__name__)
        self.write_variables[write_variable_name] = shared_variable_for_write_variable
        # Initialize the shared variable
        shared_variable_for_write_variable.write(initial_value)
        return WriteVariable(self, write_variable_name)
        
    def create_read_variable(self, read_variable_name):
        """
        Create a new read variable with the specified name.
        
        The initial value of this read variable is None.
        
        """
        if read_variable_name is None:
            error_line = ('ERROR in Agent.create_read_variable(), read_variable_name is None')
            raise Exception(error_line)
        self.read_variables[read_variable_name] = None
        return ReadVariable(self, read_variable_name)
        
    def write(self, write_variable_name, new_value):
        """
        Assign new_value to the write_variable with name: write_variable_name.
        
        """
        if write_variable_name is None:
            error_line = ('ERROR in Agent.write(), write_variable_name is None')
            raise Exception(error_line)
        self.write_variables[ write_variable_name ].write(new_value)
    
    def read(self, read_variable_name):
        """
        Return the value of the read variable with the specified name.
        
        """
        if read_variable_name is None:
            error_line = ('ERROR in Agent.read(), read_variable_name is None\n' 
                          + "Agent: " + str(self.__name__))
            raise Exception(error_line)
        if self.read_variables is None:
            error_line = ('ERROR in Agent.read(): read_variables dictionary is None\n' 
                          + "Agent: " + str(self.__name__))
            raise Exception(error_line)
        if self.read_variables[ read_variable_name ] is None:
            error_line = ('ERROR in Agent.read(): read_variables[ read_variable_name ] is None\n' 
                          + 'read_variable_name: ' + '%s\n' % (str(read_variable_name)) 
                          + 'Agent: ' + '%s\n' % (str(self.__name__))
                          + 'read_variables dictionary:\n' 
                          + str(self.read_variables))
            raise Exception(error_line)
        return self.read_variables[ read_variable_name ].read()
    
    def set_of_write_variable_names(self):
        return set(self.write_variables.keys())
    
    def set_of_read_variable_names(self):
        return set(self.read_variables.keys())


class Aggregator(Agent):
    """
    A special agent that aggregates data from multiple writers and produces a single aggregate write value.
    
    This class enables the simulation of networks with fan-in in which more than one writer assigns values
    to a single variable. An aggregator has a single read (i.e.input) variable and a single write (i.e. output) variable; 
    they are called 'in' and 'out' respectively. 
    An arbitrary number of write variables of other agents may be connected to the single read variable 
    of an aggregator. 
    This is the only mechanism in the simulator for connecting multiple write variables to a single 
    read variable.
    The aggregator aggregates all the values on write variables connected to its single read variable,
    using an aggregation operation which must be one of 'dict', 'sum', 'avg', 'min', 'max', 'list', 'set'. 
    
    If the aggregation operation is 'dict' the aggregated value is a dictionary whose keys are tuples
    (writing_agent_name, write_variable_name) and whose values are the values written by the agent
    with name 'writing_agent_name' on the variable with name 'write_variable_name'.
    
    The other aggregation operations are self-evident except for 'avg' which stands for average.
    For example, if the operation is 'avg' then the aggregated value is the average of all the
    values written to the aggregator.
    
    Attributes
    ----------
    name, simulator : see attributes of Agent class
    aggregation_operation : {'dict', 'sum', 'avg', 'min', 'max', 'list', 'set'}
    read_variables : dict
            read_variables has only one key: 'in' representing the single input
    read_variables['in'] : dict
            The keys of read_variables['in'] are tuples: (writing_agent_name, write_variable_name).
            The values of read_variables['in'] are values written by agent with name
            writing_agent_name on the variable with name write_variable_name.
    
    
    """
    def __init__(self, name, simulator, aggregation_operation):
        super(Aggregator,self).__init__(name, simulator)
        self.op = aggregation_operation
        if self.op  not in ('dict', 'sum', 'avg', 'min', 'max', 'list', 'set'):
            error_line = ('ERROR IN Aggregator: aggregation_operation' + str(aggregation_operation) + 'is not recognized')
            raise Exception(error_line)
        self.create_read_variable(read_variable_name = 'in')
        self.create_write_variable(write_variable_name = 'out')
        self.read_variables['in'] = dict()
        self.simulator.register_aggregator(self)

            
        
    def step_forward(self):
        """
        Step the state of the aggregator forward for time advancing by a single step.
        
        The aggregator reads all the write_variables connected to the aggregator's
        single read variable 'in'; computes their aggregated value; and then
        writes the aggregated value on the aggregator's single write_variable.
        
        Note: In the simulation, the aggregator's operation takes zero time
        because the aggregator is like a special fan-in variable which aggregates
        instantaneously. The transference of data from the write_variables 
        connected to the aggregator to the read_variables connected to the aggregator
        takes place in the same time step.
        
        """
        # Create a dictionary called 'output' whose keys are tuples
        # (writing_agent_name, write_variable_name) and whose values are the values 
        # written by the agent with name 'writing_agent_name' on the variable with 
        # name 'write_variable_name'.
        output = dict()
        for writer, shared_variable in self.read_variables['in'].items():
            output[writer] = shared_variable.read()
            
        # Compute the aggregated value, 'val', from the aggregation operation and the dictionary 'output'.
        if self.op is 'dict':
            val = output
        elif self.op is 'sum':
            val = sum(output.values())
        elif self.op is 'avg':
            val = sum(output.values())/len(output.values())
        elif self.op is 'min':
            val = min(output.values())
        elif self.op is 'max':
            val = max(output.values())
        elif self.op is 'list':
            val = list(output.values())
        elif self.op is 'set':
            val = set(output.values())
        else:
            error_line = ('ERROR IN Aggregator.step_forward()')
            raise Exception(error_line)
            
        # Set the single write variable to the aggregated value 'val',
        # The new value, 'val', is assigned to the shared variable's read_value
        # field rather than to its write_value field. This is because
        # the aggregated value must be read in the same time step that
        # all other shared variables are read.
        # Note that a reader of the aggregator's output must read the
        # aggregated output in the same time step that the aggregator
        # reads the values written by all the writing agents connected
        # to the aggregator.
        self.write_variables['out'].read_value = val
    
    
class SharedVariable(object):
    """
    Variables that are written by at most one agent, but that may be read by arbitrarily many agents.
    
    The only shared variables (except for Aggregator --- see below) are written by one agent and are
    read by arbitrarily many agents.
    (Multiple writers may write variables that are aggregated by Aggregator objects with the aggregated 
    values read by multiple readers.)
    
    Attributes
    ----------
    write_variable_name : str
          The name of the write_variable associated with this shared variable.
    writing_agent_name : str
          The name of the agent that writes the write variable associated with this shared variable.
          This shared variable can only be written by this agent when it writes to the variable
          with name write_variable_name.
    read_value : object
          The value of this shared variable read by agents on a given time step.
    write_value : object
          The value assigned to this shared variable on a given time step.
          Note that an agent my assign a new value to the shared variable in the same time step
          that another agent is reading the current value of this shared variable.
          read_value and write_value are distinct because on a given time step
          read_value remains unchanged and write_value gets modified.
    
    
    """
    
    def __init__(self, write_variable_name, writing_agent_name = None):
        self.write_variable_name = write_variable_name
        self.writing_agent_name = writing_agent_name
        self.read_value = None
        self.write_value = None
        self.connected = False
        
    def step_forward(self):
        """
        Step the state of the shared variable forward.
        
        The value written on the current time step becomes the value read on
        the next time step.
        No value written is equivalent to writing the value None.
        
        """
        self.read_value = self.write_value
        self.write_value = None

    def write(self, new_value):
        """
        Assign new_value to the shared variable.
        
        Assign new_value to the write_value attribute of the shared variable
        while the read_value attribute remains unchanged in this time step.
        
        """
        self.write_value   = new_value
        
    def read(self):
        """
        Read and return the value of the shared variable.
        
        Read the read_value attribute of the shared variable while the
        write_value attribute is being modified.
        
        """
        return self.read_value
    
class Simulator(object):
    def __init__(self, name = None):
        self.__name__ = name
        self.agent_dictionary = dict()
        self.aggregator_dictionary = dict()
        self.error_logger = logging.getLogger('errorLogger')
        
    def execute(self, time_horizon):
        try:
            self.time_horizon = time_horizon
            for t in range(time_horizon):
                for agent in self.agent_dictionary.values():
                    agent.step_write_variables_forward()
                for aggregator in self.aggregator_dictionary.values():
                    aggregator.step_forward()
                for agent in self.agent_dictionary.values():
                    agent.step_forward()
            import sce_settings
            log_dict = {'customer_log_dict': sce_settings.dict_customer_log, 'utility_log_dict': sce_settings.dict_utility_log}
            return log_dict
        except:
                error_line = traceback.format_exc()
                # Log error  
                error_logger = logging.getLogger('errorLogger')
                error_logger.error('ERROR DURING SIMULATION\n' + error_line)
                # Print error to stdout
                print ''
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                print 'ERROR DURING SIMULATION' 
                print error_line
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                print ''
            
    def register_agent(self, agent):
        if agent is None:
            error_line = 'Error in Simulator.register_agent. The agent is None'
            raise Exception(error_line)
        
        if agent.__name__ in self.agent_dictionary:
            error_line = ('Error in Simulator.register_agent. The same agent is registered more than once.\n' 
                          + 'Agent name: ' + str(agent.__name__))
            raise Exception(error_line)
            
        self.agent_dictionary[agent.__name__] = agent
        
    def register_aggregator(self, aggregator):
        if aggregator is None:
            error_line = 'Error in Simulator.register_aggregator. The aggregator is None'
            raise Exception(error_line)
            
        if aggregator.__name__ in self.aggregator_dictionary:
            print '*********** WARNING in Simulator.register_aggregator.'
            print 'The same aggregator is registered more than once.'
            print 'Aggregator name: ', aggregator.__name__
            self.error_logger.warning('*********** WARNING in Simulator.register_aggregator.\n'
                                       + 'The same aggregator is registered more than once.\n'
                                       + 'Aggregator name: ' + str(aggregator.__name__))
        self.aggregator_dictionary[aggregator.__name__] = aggregator
        

    def connect_variable( self, writing_agent_name, write_variable_name, reading_agent_name, read_variable_name):
        shared_variable = self.check_parameters_for_connect_variable(writing_agent_name, 
                                                                     write_variable_name, 
                                                                     reading_agent_name, 
                                                                     read_variable_name)
        reading_agent = self.agent_dictionary.get(reading_agent_name, None)
        shared_variable.connected = True
        if reading_agent.__class__.__name__ is 'Aggregator':
            read_variable = reading_agent.read_variables.get(read_variable_name, None)
            read_variable[ (writing_agent_name, write_variable_name) ] = shared_variable
        else:
            reading_agent.read_variables[read_variable_name] = shared_variable
            
                    
            
    # All exceptions handled through sce_simulation_init     
    def check_parameters_for_connect_variable(self, writing_agent_name, write_variable_name, reading_agent_name, read_variable_name):
        if None in (writing_agent_name, write_variable_name, reading_agent_name, read_variable_name):
            error_line = ('ERROR in simulator.connect_variable. Function parameter is None\n' 
                         + 'writing_agent_name: ' + '%s\n' % (str(writing_agent_name)) 
                         + 'write_variable_name: ' + '%s\n' % (str(write_variable_name))
                         + 'reading_agent_name: ' + '%s\n' % (str(reading_agent_name))
                         + 'read_variable_name: ' + '%s' % (str(read_variable_name)))
            raise Exception(error_line)
            
        writing_agent = self.agent_dictionary.get(writing_agent_name, None)
        if writing_agent is None:
            error_line = ('ERROR in Simulator.connect_variable; writing agent name does not exist in agent dictionary: ' 
                         + str(writing_agent_name))
            raise Exception(error_line)
            
        write_variable = writing_agent.write_variables.get(write_variable_name, None)
        if write_variable is None:
            error_line = ('ERROR in Simulator.connect_variable; write variable name does not exist in write variables dictionary\n' 
                         + 'Writing_agent is: ' + '%s\n' % (str(writing_agent_name)) 
                         + 'Write variable is: ' + '%s' % (str(write_variable_name)))
            raise Exception(error_line)
                        
        reading_agent = self.agent_dictionary.get(reading_agent_name, None)
        if reading_agent is None:
            error_line = ('ERROR in Simulator.connect_variable; reading agent name does not exist in agent dictionary: ' 
                         + str(reading_agent_name)) 
            raise Exception(error_line)

        shared_variable = writing_agent.write_variables[write_variable_name]
        return shared_variable
    
    def agent_and_aggregator_names(self):
        return set(self.agent_dictionary.keys())
    
    def aggregator_names(self):
        return set(self.aggregator_dictionary.keys())
    
    def agent_names(self):
        return self.agent_and_aggregator_names() - self.aggregator_names()
    
    def names_of_write_variables_and_agents_for_all_agents_and_aggregators(self):
        result = set()
        for agent_name in self.agent_and_aggregator_names():
            for write_variable_name in self.agent_dictionary[agent_name].set_of_write_variable_names():
                result.add((agent_name, write_variable_name))
        return result
    
    def names_of_read_variables_and_agents_for_all_agents_and_aggregators(self):
        result = set()
        for agent_name in self.agent_and_aggregator_names():
            for read_variable_name in self.agent_dictionary[agent_name].set_of_read_variable_names():
                result.add((agent_name, read_variable_name))
        return result
    
    def names_of_unconnected_read_variables_and_agents(self):
        result = set()
        for agent_name in self.agent_names():
            agent = self.agent_dictionary[agent_name]
            for read_variable_name, read_variable in agent.read_variables.items():
                if read_variable is None:
                    result.add( (agent_name, read_variable_name) )
        for aggregator_name in self.aggregator_names():
            aggregator = self.aggregator_dictionary[aggregator_name]
            for read_variable_name, read_variable in aggregator.read_variables.items():
                if read_variable == dict():
                    result.add( (aggregator_name, read_variable_name) )
        return result
    
    def print_names_of_unconnected_read_variables_and_agents(self):
        if self.names_of_unconnected_read_variables_and_agents() == set([]):
            print 'All read variables are connected to write variables'
            print ''
            return
        else:
            print ''
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print 'WARNING: The following (agent, read_variable) is not connected to a write variable'
            for read_agent_name_and_read_variable_name in self.names_of_unconnected_read_variables_and_agents():
                print read_agent_name_and_read_variable_name
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print ''
            
            
            
    def names_of_unconnected_write_variables_and_agents(self):
        result = set()
        for agent_name in self.agent_names():
            agent = self.agent_dictionary[agent_name]
            for write_variable_name, shared_variable in agent.write_variables.items():
                print 'writing agent: ', agent_name
                print 'write variable: ', write_variable_name
                print 'shared_variable.connected', shared_variable.connected
                if not shared_variable.connected:
                    result.add( (agent_name, write_variable_name) )
        for aggregator_name in self.aggregator_names():
            aggregator = self.aggregator_dictionary[aggregator_name]
            for write_variable_name, shared_variable in aggregator.write_variables.items():
                if not shared_variable.connected:
                    result.add( (aggregator_name, write_variable_name) )
        return result
    
    def print_names_of_unconnected_write_variables_and_agents(self):
        if self.names_of_unconnected_write_variables_and_agents() == set([]):
            print 'All write variables are connected to read variables'
            print ''
            return
        else:
            print ''
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print 'WARNING: The following (agent, write_variable) is not connected to a read variable'
            for writing_agent_name_and_write_variable_name in self.names_of_unconnected_write_variables_and_agents():
                print writing_agent_name_and_write_variable_name
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print ''
            
            
        
    def print_agent_and_aggregator_names(self):
        print ''
        print 'PRINTING AGENT AND AGGREGATOR NAMES'
        for name in self.agent_and_aggregator_names():
            print name
        print 'FINISHED PRINTING AGENT AND AGGREGATOR NAMES'
        print ''
        
    def print_aggregator_names(self):
        print ''
        print 'PRINTING AGGREGATOR NAMES'
        for name in self.aggregator_names():
            print name
        print 'FINISHED PRINTING AGGREGATOR NAMES'
        print ''
        
    def print_agent_names(self):
        print ''
        print 'PRINTING AGENT NAMES'
        for name in self.agent_names():
            print name
        print 'FINISHED PRINTING AGENT NAMES'
        print ''
        
    def print_write_variables_for_all_agents_and_aggregators(self):
        print ''
        print 'PRINTING WRITE VARIABLES FOR ALL AGENTS AND AGGREGATORS'
        for name in self.names_of_write_variables_and_agents_for_all_agents_and_aggregators():
            print name
        print 'FINISHED PRINTING WRITE VARIABLES FOR ALL AGENTS AND AGGREGATORS'
        print ''
        
    def print_read_variables_for_all_agents_and_aggregators(self):
        print ''
        print 'PRINTING READ VARIABLES FOR ALL AGENTS AND AGGREGATORS'
        for name in self.names_of_read_variables_and_agents_for_all_agents_and_aggregators():
            print name
        print 'FINISHED PRINTING READ VARIABLES FOR ALL AGENTS AND AGGREGATORS'
        print ''
        
        
        
        
        

            
            
            
        
        
        