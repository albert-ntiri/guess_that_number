"""
The user_metrics.py module is part of the analytics package.  It consists of classes for deriving
data points that indicate how well a user is performing during a session.  These metrics are used
for predictive modeling.

Classes:
    UserMetric
    PositiveFeedbackPercent
    HintChessScore
    WinGamePercent
    UserMetricsManager
"""


import pandas as pd
import numpy as np
from game.game_stats import Stat
from resources.infrastructure.subsystem import Manager
from resources.infrastructure.log_entries import UserMetricLogEntry, PosFeedbackPercCalcLogEntry
from resources.infrastructure.log_entries import HintChessScoreCalcLogEntry, WinGamePercentCalcLogEntry



class UserMetric(Stat):
    """
    The UserMetric class is the base class for all user metrics.  It inherits from Stat, which is defined
    in the game_stats.py module in the game package.
    """
    
    def __init__(self, objects):
        super().__init__(objects)
        self._logs = self._objects.get_object("logs")
    
    def update_stat(self, context):
        if context == "new guess":
            super().update_stat()
        elif context == "end game":
            self.value = self._derive_end_game_metric() if self._meets_criteria() else self._set_default_value()
        else:
            self.value = self._set_default_value()
        
        if self._meets_criteria():
            self._log_metric_value()
    
    def _get_new_value(self):
        return self._derive_metric() if self._meets_criteria() else self._value
    
    def _log_metric_value(self):
        user_metric_log_entry = UserMetricLogEntry(self._logs, self.get_name(), self._value)
        user_metric_log_entry.add_log_entry("metrics")
    
    def _log_metric_calculation(self):
        pass
    
    def _meets_criteria(self):
        pass



class PositiveFeedbackPercent(UserMetric):
    """
    The PositiveFeedbackPercent class represents the percentage of guesses a user entered that is in line
    with the hint given.  It inherits from UserMetric.
    """
    
    def __init__(self, objects):
        super().__init__(objects)
        self._name = "positive feedback percentage"
        self._game_feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
        self._agg_feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
        self._positive_feedback_count = 0
        self._total_feedback_count = 0
    
    def _set_default_value(self):
        feedback = self._objects.get_object("feedback")
        self._game_feedback = feedback.get_feedback_df()
        games = self._objects.get_object("games")
        self._agg_feedback = games.get_aggregate_feedback()
        return 1
    
    def _derive_metric(self):
        self._total_feedback_count += 1
        last_feedback_ind = self._game_feedback.loc[-1, "feedback_ind"]
        if last_feedback_ind == "good":
            self._positive_feedback_count += 1
        
        value = self._positive_feedback_count / self._total_feedback_count
        
        self._log_metric_calculation(self._positive_feedback_count, self._total_feedback_count)
        
        return value
    
    def _derive_end_game_metric(self):
        return self._derive_metric()
    
    def _log_metric_calculation(self, positive_count, total_count):
        user_metric_log_entry = PosFeedbackPercCalcLogEntry(self._logs, self._meets_criteria(), positive_count, total_count)
        user_metric_log_entry.add_log_entry("metrics")
    
    def _meets_criteria(self):
        return (len(self._game_feedback) or len(self._agg_feedback)) and isinstance(self._value, float)



class HintChessScore(UserMetric):
    """
    The HintChessScore class represents how quickly a user captures new information about the winning
    number.  It inherits from UserMetric.
    """
    
    def __init__(self, objects):
        super().__init__(objects)
        self._name = "hint chess score"
        self._hints = self
        self._original_hint_count = 0
        self._previous_values = []
    
    def _set_default_value(self):
        self._hints = self._objects.get_object("hints")
        self._original_hint_count = self._hints.get_hint_count("relevant")
        return 1
    
    def _derive_metric(self):
        current_hint_chess_score = self._calc_current_hint_chess_score()
        if self._previous_values:
            hint_chess_score = np.mean(self._previous_values + [current_hint_chess_score])
        else:
            hint_chess_score = current_hint_chess_score
        
        return hint_chess_score
    
    def _derive_end_game_metric(self):
        current_hint_chess_score = self._calc_current_hint_chess_score()
        self._previous_values.append(current_hint_chess_score)
        return current_hint_chess_score
    
    def _calc_current_hint_chess_score(self):
        hints_given = self._hints.get_hint_count("given")
        percent_hints_captured = (self._original_hint_count - self._hints.get_hint_count("relevant")) / self._original_hint_count
        current_hint_chess_score = percent_hints_captured / hints_given
        
        self._log_metric_calculation(percent_hints_captured, hints_given)
        
        return current_hint_chess_score
    
    def _log_metric_calculation(self, percent_hints_captured, hints_given):
        meets_criteria = True if self._meets_criteria() else False
        user_metric_log_entry = HintChessScoreCalcLogEntry(self._logs, meets_criteria, percent_hints_captured, hints_given,
                                                           self._previous_values)
        user_metric_log_entry.add_log_entry("metrics")
    
    def _meets_criteria(self):
        return self._hints.get_hint_count("given")



class WinGamePercent(UserMetric):
    """
    The WinGamePercent class represents the percentage of games a user won during a particular session.
    It inherits from UserMetric.
    """
    
    def __init__(self, objects):
        super().__init__(objects)
        self._name = "win game percentage"
        self._games = None
        self._games_played = 0
        self._games_won = 0
    
    def _set_default_value(self):
        return 1
    
    def _derive_metric(self):
        pass
    
    def _derive_end_game_metric(self):
        outcome = self._games.get_current_game_outcome()
        if outcome in ["win", "lose"]:
            self._games_played += 1
            
            if outcome == "win":
                self._games_won += 1
            
            self._log_metric_calculation(self._games_won, self._games_played)
            
            return self._games_won / self._games_played
    
    def _log_metric_calculation(self, games_won, games_played):
        meets_criteria = True if self._meets_criteria() else False
        user_metric_log_entry = WinGamePercentCalcLogEntry(self._logs, meets_criteria, games_won, games_played)
        user_metric_log_entry.add_log_entry("metrics")
    
    def _meets_criteria(self):
        self._games = self._objects.get_object("games")
        return self._games.get_game_count()



class UserMetricsManager(Manager):
    """
    The UserMetricsManager class manages the updates to the UserMetric subclasses and provides a way for
    other objects to access the current value of game stats.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._feedback_percent = PositiveFeedbackPercent(self._objects)
        self._hint_chess_score = HintChessScore(self._objects)
        self._win_game_percent = WinGamePercent(self._objects)
        super().__init__(UserMetric)
    
    def update_user_metrics(self, context):
        if context in ["new game", "new guess"]:
            for metric in ["positive feedback percentage", "hint chess score"]:
                self.run_subclass_method(metric, context)
        else:
            self.run_all_subclass_methods(context)
    
    def get_metric_values(self):
        metric_values = (self._feedback_percent.value, self._win_game_percent.value)
        return metric_values