import unittest
import datetime
from service.api.controller.metric_source_builder import Metric_Source_Builder
from service.api.actuator.plugins.instance_locator import Instance_Locator
from utils.ssh_utils import SSH_Utils
from service.api.actuator.plugins.remote_kvm import Remote_KVM
from service.api.actuator.plugins.kvm_actuator import KVM_Actuator
from service.api.controller.plugins.proportional.proportional_alarm import Proportional_Alarm
from mock.mock import MagicMock

class Test_Proportional_Alarm(unittest.TestCase):

    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"

        self.timestamp_1 = datetime.datetime.strptime("2000-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_2 = datetime.datetime.strptime("2000-01-01T00:05:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_3 = datetime.datetime.strptime("2000-01-01T00:10:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_4 = datetime.datetime.strptime("2000-01-01T00:15:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')

        self.instance_name_1 = "instance1"
        self.instance_name_2 = "instance2"

        self.trigger_down = 30.0
        self.trigger_up = 10.0
        self.min_cap = 10.0
        self.max_cap = 100.0
        self.actuation_size = 10.0
        self.allocated_resources = 50
        self.metric_round = 2

        compute_nodes = []
        compute_nodes_key = "key"
        self.instances = [self.instance_name_1, self.instance_name_2]
        self.metric_source = Metric_Source_Builder().get_metric_source("nop", {})
        self.instance_locator = Instance_Locator(SSH_Utils({}), compute_nodes, compute_nodes_key)
        self.remote_kvm = Remote_KVM(SSH_Utils({}), compute_nodes_key)
        self.actuator = KVM_Actuator(self.instance_locator, self.remote_kvm)

        self.conservative_factor = 1
        self.heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":self.conservative_factor}

        self.progress_error = {self.application_id_0:-20.0, self.application_id_1:0.00, self.application_id_2:30.0}
        
        self.timestamps = [self.timestamp_1, self.timestamp_2, self.timestamp_3, self.timestamp_4]

    # normal cases
    # application 0 -> job progress < time progress -> scale up
    # application 1 -> job progress = time progress -> do nothing
    # application 2 -> job progress > time progress -> scale down

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        if metric_name == Proportional_Alarm.ERROR_METRIC_NAME:
            return self.timestamp_1, self.progress_error[application_id]

    def metrics_different_timestamps(self, metric_name, options):
        application_id = options["application_id"]
        
        timestamp = self.timestamps.pop(0)

        if metric_name == Proportional_Alarm.ERROR_METRIC_NAME:
            return timestamp, self.progress_error[application_id]

    def test_alarm_gets_metrics_and_scales_down_error_proportional(self):
        #
        # Case 1: normal scale down
        #
        conservative_factor = 1
        heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":conservative_factor}
        
        self.alarm = Proportional_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.metric_round, heuristic_options)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_2})
        
        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        
        # Remove resources
        error = self.metrics(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_2})[1]
        new_cap = self.allocated_resources - self.conservative_factor*error
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
        #
        # Case 2: calculated cap is too low. Use min cap instead
        #
        conservative_factor = 3
        heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":conservative_factor}
        
        self.alarm = Proportional_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.metric_round, heuristic_options)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_2})
        
        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        
        # Remove resources
        new_cap = self.min_cap
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        

    def test_alarm_gets_metrics_and_scales_up_error_proportional(self):
        #
        # Case 1: normal scale up
        #
        conservative_factor = 1
        heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":conservative_factor}
        
        self.alarm = Proportional_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.metric_round, heuristic_options)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_0, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Add resources
        error = self.metrics(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_0})[1]
        new_cap = self.allocated_resources + conservative_factor*abs(error)
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
        #
        # Case 2: calculated cap is too high. Use max cap instead
        #
        conservative_factor = 3
        heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":conservative_factor}
        
        self.alarm = Proportional_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.metric_round, heuristic_options)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_0, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Add resources
        new_cap = self.max_cap
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})

    def test_alarm_does_nothing(self):
        conservative_factor = 1
        heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":conservative_factor}
        
        self.alarm = Proportional_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.metric_round, heuristic_options)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_1, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_1})

        # The method doesn't try to get the amount of allocated resources 
        self.actuator.get_allocated_resources.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_does_not_reuse_metrics_with_same_timestamp(self):
        conservative_factor = 1
        heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":conservative_factor}
        
        self.alarm = Proportional_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.metric_round, heuristic_options)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_0, self.instances)
        
        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_0})
        
        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Add resources
        error = self.metrics(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_0})[1]
        new_cap = self.allocated_resources + conservative_factor*abs(error)
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
        #
        # 2nd call. The method checks if the metric is new and does not act
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_0, self.instances)
        
        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_0})

        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()
        
    def test_alarm_metrics_with_different_timestamps(self):
        conservative_factor = 1
        heuristic_options = {"heuristic-name":"error-proportional",
                                  "conservative-factor":conservative_factor}
        
        self.alarm = Proportional_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.metric_round, heuristic_options)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics_different_timestamps

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Remove resources
        error = self.metrics(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_2})[1]
        new_cap = self.allocated_resources - self.conservative_factor*error
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
        #
        # 2nd call. The method checks if the metric is new and acts
        #
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics_different_timestamps

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Remove resources
        
        error = self.metrics(Proportional_Alarm.ERROR_METRIC_NAME, {"application_id":self.application_id_2})[1]
        new_cap = self.allocated_resources - self.conservative_factor*error
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()