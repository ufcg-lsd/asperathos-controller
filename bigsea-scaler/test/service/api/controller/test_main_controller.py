import unittest
import time

from mock.mock import MagicMock
from service.api.controller.main_controller import Main_Controller
from service.api.controller.plugins.single_application_controller import Single_Application_Controller


class Test_Main_Controller(unittest.TestCase):


    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        
        self.plugin = "single"

        self.instance_1 = "instance-1"
        self.instance_2 = "instance-2"
        self.instances = [self.instance_1, self.instance_2]
        
        self.check_interval = 2
        self.trigger_down = 10
        self.trigger_up = 100
        self.min_cap = 10
        self.max_cap = 100
        self.actuation_size = 20
        self.metric_rounding = 2
        self.actuator = "kvm"
        self.metric_source = "nop"
        
        self.parameters = {}
        self.parameters["instances"] = self.instances
        self.parameters["check_interval"] = self.check_interval
        self.parameters["trigger_down"] = self.trigger_down
        self.parameters["trigger_up"] = self.trigger_up
        self.parameters["min_cap"] = self.min_cap
        self.parameters["max_cap"] = self.max_cap
        self.parameters["actuation_size"] = self.actuation_size
        self.parameters["metric_rounding"] = self.metric_rounding
        self.parameters["actuator"] = self.actuator
        self.parameters["metric_source"] = self.metric_source
        self.parameters["plugin"] = self.plugin
        
        self.controller = Single_Application_Controller(self.application_id_0, self.parameters)
        self.controller_2 = Single_Application_Controller(self.application_id_1, self.parameters)
        self.main_controller = Main_Controller()

    def controllers(self, name, application_id, parameters):
        return {self.application_id_0:self.controller, self.application_id_1:self.controller_2}[application_id]
        
    def test_start_and_stop_scaling_1_application(self):
        #
        # Starting scaling
        #
        
        # Setting up mocks
        self.main_controller.controller_builder.get_controller = MagicMock()
        self.main_controller.controller_builder.get_controller.side_effect = self.controllers
        self.controller.start_application_scaling = MagicMock(return_value=None)
        self.controller.stop_application_scaling = MagicMock(return_value=None)
        
        # Start scaling for application 0
        self.main_controller.start_application_scaling(self.application_id_0, self.parameters)
        
        time.sleep(5)
        
        # The builder was called to get a new controller
        self.main_controller.controller_builder.get_controller.assert_called_once_with("single", self.application_id_0, self.parameters)
        
        # The controller was started and added to the pool
        self.controller.start_application_scaling.assert_called_once()
        self.assertEquals(1, len(self.main_controller.controller_thread_pool.items()))
        self.assertTrue(self.main_controller.controller_thread_pool.has_key(self.application_id_0))
        self.assertEquals(self.controller, self.main_controller.controller_thread_pool[self.application_id_0])
        
        #
        # Stopping scaling
        #
        self.main_controller.controller_builder.get_controller = MagicMock(return_value=self.controller)
        
        # Stop scaling for application 0
        self.main_controller.stop_application_scaling(self.application_id_0)

        # The builder was not called
        self.main_controller.controller_builder.get_controller.assert_not_called()
        
        # The controller was stopped and removed from the pool
        self.controller.stop_application_scaling.assert_called_once()
        self.assertEquals(0, len(self.main_controller.controller_thread_pool.items()))
        
    def test_start_and_stop_scaling_2_applications(self):
        #
        # Starting scaling
        #
        
        # Setting up mocks
        self.main_controller.controller_builder.get_controller = MagicMock()
        self.main_controller.controller_builder.get_controller.side_effect = self.controllers
        self.controller.start_application_scaling = MagicMock(return_value=None)
        self.controller.stop_application_scaling = MagicMock(return_value=None)
        self.controller_2.start_application_scaling = MagicMock(return_value=None)
        self.controller_2.stop_application_scaling = MagicMock(return_value=None)
        
        # Starting scaling for application 0
        self.main_controller.start_application_scaling(self.application_id_0, self.parameters)
        
        time.sleep(5)
        
        # The builder was called to get a new controller
        self.main_controller.controller_builder.get_controller.assert_any_call("single", self.application_id_0, self.parameters)
        
        # The controller is started and added to the pool
        self.controller.start_application_scaling.assert_called_once()
        self.assertEquals(1, len(self.main_controller.controller_thread_pool.items()))
        self.assertTrue(self.main_controller.controller_thread_pool.has_key(self.application_id_0))
        self.assertEquals(self.controller, self.main_controller.controller_thread_pool[self.application_id_0])
        
        # Starting scaling for application 1
        self.main_controller.start_application_scaling(self.application_id_1, self.parameters)
        
        # The builder was called to get a new controller
        self.main_controller.controller_builder.get_controller.assert_any_call("single", self.application_id_1, self.parameters)
        self.assertEquals(2, self.main_controller.controller_builder.get_controller.call_count)
        self.controller_2.start_application_scaling.assert_called_once()
        
        # The controller is started and added to the pool
        self.assertEquals(2, len(self.main_controller.controller_thread_pool.items()))
        self.assertTrue(self.main_controller.controller_thread_pool.has_key(self.application_id_0))
        self.assertEquals(self.controller, self.main_controller.controller_thread_pool[self.application_id_0])
        self.assertTrue(self.main_controller.controller_thread_pool.has_key(self.application_id_1))
        self.assertEquals(self.controller_2, self.main_controller.controller_thread_pool[self.application_id_1])
        
        #
        # Stopping scaling
        #
        self.main_controller.controller_builder.get_controller = MagicMock(return_value=self.controller)
        
        # Stopping scaling for application 0
        self.main_controller.stop_application_scaling(self.application_id_0)
        
        # The controller is stopped and removed from the pool
        self.controller.stop_application_scaling.assert_called_once()
        self.assertEquals(1, len(self.main_controller.controller_thread_pool.items()))
        self.assertTrue(self.main_controller.controller_thread_pool.has_key(self.application_id_1))
        self.assertEquals(self.controller_2, self.main_controller.controller_thread_pool[self.application_id_1])
        
        # Stopping scaling for application 1
        self.main_controller.stop_application_scaling(self.application_id_1)
        
        # The controller is stopped and removed from the pool
        self.controller_2.stop_application_scaling.assert_called_once()
        self.assertEquals(0, len(self.main_controller.controller_thread_pool.items()))
        
        self.main_controller.controller_builder.get_controller.assert_not_called()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()