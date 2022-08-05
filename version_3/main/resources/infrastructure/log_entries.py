"""
The log_entries.py module is part of the infrastructure package.  It consists of classes that lay out
templates for various types of log messages.  Each class represents a template for a specific type of
log entry.  These templates allow for use of variables to customize messages.

Classes:
    LogEntry
    various subclasses
"""


from resources.infrastructure.log import LogFactory



class LogEntry:
    """
    The LogEntry class is the base class for all log entries.  It specifies how a message is put together
    and added to the appropriate log.
    """
    
    def __init__(self, logs):
        self.logs = logs
        self._log_message = ""
    
    def add_log_entry(self, log_name, *args):
        log = self.logs.log_dict[log_name]
        log_message = self._get_log_message(*args)
        log.add_entry(log_message)
    
    def log_all(self, *args):
        for log_name in self.logs.log_dict.keys():
            self.add_log_entry(log_name, *args)
    
    def _get_log_message(self, *args):
        log_message = self._log_message.format(*args) if args else self._log_message
        return log_message



class ClassLogEntry(LogEntry):
    def __init__(self, logs, class_name, obj_name, instantiator):
        super().__init__(logs)
        tab1 = "\t" if len(class_name) > 8 else "\t\t"
        tab2 = "\t" if len(obj_name) > 16 else "\t\t" if len(obj_name) > 7  else "\t\t\t"
        self._log_message = f"New Object\tClass: {class_name}" + tab1 + f"Object: {obj_name}" + tab2 + f"Instantiator: {instantiator}"



class TextLogEntry(LogEntry):
    def __init__(self, logs, page, var_name, content):
        super().__init__(logs)
        self._log_message = f"Page: {page.title()}\tVariable: {var_name}\tText: {content}"



class DBConnectorLogEntry(LogEntry):
    def __init__(self, logs, connector_type):
        super().__init__(logs)
        self._log_message = f"{connector_type} DB Connector Established"



class DBScriptorLogEntry(LogEntry):
    def __init__(self, logs, scriptor_type):
        super().__init__(logs)
        self._log_message = f"{scriptor_type} Ran\n\n"



class DBTableLogEntry(LogEntry):
    def __init__(self, logs, table, entry_type):
        super().__init__(logs)
        self._log_message = f"{table} table {entry_type}"



class HintsPopulatedLogEntry(LogEntry):
    def __init__(self, logs, max_number):
        super().__init__(logs)
        self._log_message = f"hints 1 to {max_number} populated"



class NewSessionLogEntry(LogEntry):
    def __init__(self, logs, session_id):
        super().__init__(logs)
        self._log_message = f"Session {session_id} Entered"



class NewGameLogEntry(LogEntry):
    def __init__(self, logs, settings):
        super().__init__(logs)
        level = settings.get_setting("level of difficulty name")
        num_range = settings.get_setting("number range")
        winning_number = settings.get_setting("winning number")
        
        if len(str(num_range)) > 8:
            self._log_message = f"NEW GAME\t\tLevel: {level.title()}\tRange: {num_range}\tWinning Number: {winning_number}"
        else:
            self._log_message = f"NEW GAME\t\tLevel: {level.title()}\tRange: {num_range}\t\tWinning Number: {winning_number}"



class RangeErrorLogEntry(LogEntry):
    def __init__(self, logs, user_entry, error_message):
        super().__init__(logs)
        self._log_message = f"Range Error\t\tEntry: {user_entry}\tError Message: {error_message}"



class NewGuessLogEntry(LogEntry):
    def __init__(self, logs, guess_count, guess, message=None, message_type=None):
        super().__init__(logs)
        self._log_message = f"Guess #{guess_count}\t\tGuess: {guess}"
        if message:
            self._log_message = self._log_message + f"\t{message_type.title()}: {message}"



class IndividualFeedbackLogEntry(LogEntry):
    def __init__(self, logs, hint_type, hint, guess, feedback_ind):
        super().__init__(logs)
        self._log_message = f"New Feedback\n\n\nHint Type\t\t{hint_type}\nHint\t\t\t{hint}\nGuess\t\t\t{guess}\nFeedback Indicator\t{feedback_ind.title()}"



class UserMetricLogEntry(LogEntry):
    def __init__(self, logs, metric_name, metric_value):
        super().__init__(logs)
        tab = "\t" if len(metric_name) > 23 else "\t\t" if len(metric_name) > 15 else "\t\t\t" if len(metric_name) > 7 else "\t\t\t\t"
        self._log_message = f"{metric_name.title()}" + tab + f"{metric_value}"



class EndGameLogEntry(LogEntry):
    def __init__(self, logs, outcome, score=None, feedback=None):
        super().__init__(logs)
        self._log_message = f"Game Ended\t\tOutcome: {outcome.title()}"
        if score:
            self._log_message = self._log_message + f"\tScore: {score}"
        if feedback:
            self._log_message = self._log_message + f"\n\n\n{feedback}\n"



class PlayAgainLogEntry(LogEntry):
    def __init__(self, logs):
        super().__init__(logs)
        self._log_message = "Play Again\n\n\n"



class TopImprovementAreaLogEntry(LogEntry):
    def __init__(self, logs, top_improvement_area):
        super().__init__(logs)
        self._log_message = f"Top Improvement Area: {top_improvement_area}"



class FeedbackComponentLogEntry(LogEntry):
    def __init__(self, logs, component_type, feedback):
        super().__init__(logs)
        self._log_message = f"{component_type.title()} Feedback:\n\n{feedback}"



class PosFeedbackPercCalcLogEntry(LogEntry):
    def __init__(self, logs, meets_criteria, positive_count, total_count):
        super().__init__(logs)
        self._log_message = f"Positive Feedback Percentage\t\tMeets Criteria - {meets_criteria}\n\n"
        self._log_message = self._log_message + f"Positive Count\t\t{positive_count}\nTotal Count\t\t{total_count}"



class HintChessScoreCalcLogEntry(LogEntry):
    def __init__(self, logs, meets_criteria, perc_hints_captured, hints_given, previous_values):
        super().__init__(logs)
        self._log_message = f"Hint Chess Score\t\tMeets Criteria - {meets_criteria}\n\n"
        self._log_message = self._log_message + f"Percent Hints Captured\t\t{perc_hints_captured}\nHints Given\t\t{hints_given}"
        if previous_values:
            self._log_message = self._log_message + f"\nPrevious Values\t\t{previous_values}"



class WinGamePercentCalcLogEntry(LogEntry):
    def __init__(self, logs, meets_criteria, games_won, games_played):
        super().__init__(logs)
        self._log_message = f"Win Game Percentage\t\tMeets Criteria - {meets_criteria}\n\n"
        self._log_message = self._log_message + f"Games Won\t\t{games_won}\nGames Played\t\t{games_played}"



class TrainingDataLogEntry(LogEntry):
    def __init__(self, logs, score_data_size, outcome_data_size):
        super().__init__(logs)
        self._log_message = f"Training Data\t\tScore Predictor - {score_data_size} rows\tOutcome Predictor - {outcome_data_size} rows"



class PredictionLogEntry(LogEntry):
    def __init__(self, logs, pred_type, prediction, score=None, target_score=None):
        super().__init__(logs)
        if pred_type == "score":
            self._log_message = f"Prediction\t\t\tActual Score - {score}\tPredicted Score - {prediction}\tTarget Score - {target_score}"
        else:
            self._log_message = f"Prediction\t\t\tActual Outcome - win\tPredicted Outcome - {prediction}"



class RecommendationTypeLogEntry(LogEntry):
    def __init__(self, logs, recommendation_type, recommendation):
        super().__init__(logs)
        self._log_message = f"Recommendation Type\t\t{recommendation_type.title()}\t\tRecommendation\t\t{recommendation}"