"""
The iterable_log_entries.py module is part of the infrastructure package.  It is similar to log_entries.py,
except its entries include a variable that is iterable.  It has a base class for each format the iterable
variable takes.  The remainder of classes are for specific types of log entries.

Classes:
    IterableLogEntry
    IterableListLogEntry
    IterableDictLogEntry
    IterableDFLogEntry
    various subclasses
"""


from resources.infrastructure.log_entries import LogEntry
import pandas as pd



class IterableLogEntry(LogEntry):
    """
    The IterableLogEntry class is the base class for all iterable log entries.  It inherits from LogEntry.
    It defines a split_by_line method for specifiing how the content of the iterable variable should be
    laid out.  The implementation of this method is deferred to its subclasses.
    """
    
    def __init__(self, logs):
        super().__init__(logs)
        self._initial_message = ""
    
    @staticmethod
    def split_by_line(initial_message, iterable):
        pass



class IterableListLogEntry(IterableLogEntry):
    """
    The IterableListLogEntry is for log entries where the variable is in a list format.  It inherits from
    IterableLogEntry.
    """
    
    @staticmethod
    def split_by_line(initial_message, iterable):
        log_message = initial_message
        for entry in iterable:
            log_message = log_message + f"{entry}\n"
        
        return log_message



class IterableDictLogEntry(IterableLogEntry):
    """
    The IterableDictLogEntry is for log entries where the variable is in a dictionary format.  It inherits from
    IterableLogEntry.
    """
    
    @staticmethod
    def split_by_line(initial_message, iterable):
        log_message = initial_message
        for col, val in iterable.items():
            tab = "\t" if len(col) > 23 else "\t\t" if len(col) > 15 else "\t\t\t" if len(col) > 7 else "\t\t\t\t"
            log_message = log_message + f"{col}" + tab + f"{val}\n"
        
        return log_message



class IterableDFLogEntry(IterableLogEntry):
    """
    The IterableDFLogEntry is for log entries where the variable is in a dataframe format.  It inherits from
    IterableLogEntry.
    """
    
    @staticmethod
    def split_by_line(initial_message, iterable):
        log_message = f"{initial_message}\n\n{iterable}"
        return log_message



class DBCreatedLogEntry(IterableListLogEntry):
    def __init__(self, logs, tables):
        super().__init__(logs)
        self._initial_message = "Database Tables\n\n"
        self._log_message = self.split_by_line(tables)
    
    def split_by_line(self, tables):
        log_message = self._initial_message
        for table in tables:
            log_message = log_message + f"{table[1]} {table[-1]}\n"
        
        return log_message



class DBQueryLogEntry(IterableDFLogEntry):
    def __init__(self, logs, result_name, query_results):
        super().__init__(logs)
        self._initial_message = f"{result_name}:"
        self._log_message = self.split_by_line(self._initial_message, query_results)



class DBRecordLogEntry(IterableDictLogEntry):
    def __init__(self, logs, record_type, entry_type, parameters):
        super().__init__(logs)
        self._initial_message = f"{record_type} Record {entry_type}\n\n\nData:\n\n"
        self._log_message = self.split_by_line(self._initial_message, parameters)



class NewHintsLogEntry(IterableListLogEntry):
    def __init__(self, logs, hints):
        super().__init__(logs)
        self._initial_message = "New Hint Pool\n\n\tAll Hints:\n\n"
        self._log_message = self.split_by_line(self._initial_message, sorted(hints))



class RemainingHintsLogEntry(IterableListLogEntry):
    def __init__(self, logs, new_guess_log_entry, remaining_hints, redundant_hints, hint_pool):
        super().__init__(logs)
        self._initial_message = new_guess_log_entry._log_message + "\n\n\tRemaining Hints:\n\n"
        self._log_message = self.split_by_line(self._initial_message, sorted(remaining_hints))
        self._log_message = self.split_by_line(self._log_message + "\n\n\tRedundant Hints:\n\n", sorted(redundant_hints))
        self._log_message = self.split_by_line(self._log_message + "\n\n\tTotal Hint Pool:\n\n", sorted(hint_pool))



class ImprovementAreasLogEntry(IterableDFLogEntry):
    def __init__(self, logs, scope, improvement_areas, ranked=False):
        super().__init__(logs)
        self._initial_message = f"{scope} Improvement Areas"
        if ranked:
            self._initial_message = self._initial_message + " Ranked:"
        self._log_message = self.split_by_line(self._initial_message, improvement_areas)



class FeatureMeansLogEntry(IterableDictLogEntry):
    def __init__(self, logs, target, feature_means):
        super().__init__(logs)
        self._initial_message = f"{target.title()} Feature Means\n\n"
        self._log_message = self.split_by_line(self._initial_message, feature_means)



class ModelMetricsLogEntry(IterableDictLogEntry):
    def __init__(self, logs, target, model_metrics):
        super().__init__(logs)
        self._initial_message = f"{target.title()} Model Metrics\n\n"
        self._log_message = self.split_by_line(self._initial_message, model_metrics)



class ModelCoefficientsLogEntry(IterableDFLogEntry):
    def __init__(self, logs, target, coefficients):
        super().__init__(logs)
        self._initial_message = f"{target.title()} Model Coefficients"
        self._log_message = self.split_by_line(self._initial_message, coefficients)



class PredictionFeaturesLogEntry(IterableDictLogEntry):
    def __init__(self, logs, target, game_info):
        super().__init__(logs)
        self._initial_message = f"{target.title()} Features\n\n"
        self._log_message = self.split_by_line(self._initial_message, game_info)