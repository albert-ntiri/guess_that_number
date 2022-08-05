"""
The log.py module is part of the infrastructure package.  It contains one class that configures logs for
the app and another that uses that first class to create a number of logs for different purposes.

Classes:
    Logger
    LogFactory
"""


import logging
from resources.infrastructure.subsystem import BaseClass, Manager



class Logger(BaseClass):
    """
    The Logger is the base class for all the logs of the app.  It establishes how the logs are set up.
    """
    
    def __init__(self, log_name, log_file_name):
        super().__init__()
        self._name = log_name
        
        self._obj_id_method = self._get_name
        self._standardized_method = self.add_entry
        
        self.logger = logging.getLogger(__name__ + self._name)
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter("%(asctime)s     %(message)s\n")
        
        activity_file_handler = logging.FileHandler(filename=log_file_name, mode='w')
        activity_file_handler.setFormatter(formatter)
        
        self.logger.addHandler(activity_file_handler)
        
        self.add_entry("**************************************** NEW SESSION ****************************************\n\n")
        self.add_entry(f"LOG NAME: {self._name.title()} Log\n")
    
    def add_entry(self, message):
        self.logger.info(message)
    
    def _get_name(self):
        return self._name



class LogFactory(Manager):
    """
    The LogFactory class is composed on various logs for the app.  Each log captures activity from a
    different perspective and focus.  All log objects inherit from Logger.
    """
    
    def __init__(self):
        self._main_log = self._add_log(name='main', file_name='resources/logs/high_level_log.log')
        self._class_log = self._add_log(name='class', file_name='resources/logs/class_log.log')
        self._db_log = self._add_log(name='database', file_name='resources/logs/db_log.log')
        self._text_log = self._add_log(name='text', file_name='resources/logs/text_log.log')
        self._hint_log = self._add_log(name='hints', file_name='resources/logs/hint_log.log')
        self._feedback_log = self._add_log(name='feedback', file_name='resources/logs/feedback_log.log')
        self._user_metrics_log = self._add_log(name='metrics', file_name='resources/logs/user_metrics_log.log')
        self._prediction_log = self._add_log(name='prediction', file_name='resources/logs/prediction_log.log')
        super().__init__(Logger)
        
        self.log_dict = self._get_log_dict()
        
        self._enter_beginning_logs()
    
    def _enter_beginning_logs(self):
        self._class_log.add_entry("New Object\tClass: GuessThatNumberGame\t\t\t\tInstantiator: GuessThatNumberGame")
        self._class_log.add_entry("New Object\tClass: ObjectManager\tObject: objects\t\t\tInstantiator: GuessThatNumberGame")
        self._class_log.add_entry("New Object\tClass: LogFactory\tObject: logs\t\t\tInstantiator: ObjectManager")
    
    def _add_log(self, name, file_name):
        log = Logger(log_name=name, log_file_name=file_name)
        return log
    
    def _get_log_dict(self):
        return self._subclass_dict