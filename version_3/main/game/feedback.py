"""
The feedback.py module is part of the game package.  It is for collecting and displaying feedback to the
user based on guesses and hints during a game.  The feedback occurs after guesses and after the conclusion
of a game.

Classes:
    Feedback
    GuessFeedback
    GameFeedback
    FeedbackManager
"""


import pandas as pd
from game.improvement import Improvement
from game.recommendation import Recommendation
from resources.infrastructure.log_entries import IndividualFeedbackLogEntry



class Feedback:
    """
    The Feedback class is the base class for the different types of feedback displayed to the user.  It is
    not meant to be instantiated directly.
    """
    
    def __init__(self, objects, feedback):
        self._objects = objects
        self._session = self._objects.get_object("session")
        self._feedback = feedback
    
    def get_feedback(self):
        pass



class GuessFeedback(Feedback):
    """
    The GuessFeedback class is for feedback after a guess, based on whether the guess is in line with
    the hint provided.  It inherits from Feedback.
    """
    
    def __init__(self, objects, feedback, guess):
        super().__init__(objects, feedback)
        self._guess = guess
        self._last_hint_type, self._last_hint = self._session.get_last_hint()
        self._logs = self._objects.get_object("logs")
    
    def get_feedback(self, guess_concepts):
        feedback_number, feedback_ind = self._generate_guess_feedback(guess_concepts)
        self._record_guess_feedback(feedback_number, feedback_ind)
        return feedback_ind
    
    def _generate_guess_feedback(self, guess_concepts):
        feedback_ind = guess_concepts.evaluate_guess(self._last_hint_type, self._guess, self._last_hint)
        
        if not len(self._feedback):
            feedback_number = 1
        else:
            feedback_number = len(self._feedback) + 1
        
        return feedback_number, feedback_ind
    
    def _record_guess_feedback(self, feedback_number, feedback_ind):
        self._feedback.loc[feedback_number] = [self._last_hint_type, self._last_hint, self._guess, feedback_ind]
        if self._logs:
            ind_feedback_log_entry = IndividualFeedbackLogEntry(self._logs, self._last_hint_type, self._last_hint,
                                                            self._guess, feedback_ind)
            ind_feedback_log_entry.add_log_entry("feedback")



class GameFeedback(Feedback):
    """
    The GameFeedback class is for feedback after the conclusion of a game.  It consists of either an improvement
    area, backed by a definition and an example from the game, or a recommendation for the user's next game.  It
    inherits from Feedback.
    """
    
    def __init__(self, objects, feedback, score):
        super().__init__(objects, feedback)
        self._games = self._objects.get_object("games")
        self._text_display = self._objects.get_object("text_display")
        self._score = score
        self._feedback_type = None
    
    def get_feedback(self):
        self._games.update_aggregate_feedback(self._feedback)
        improvement_areas = self._feedback[(self._feedback.feedback_ind == "bad") & 
                                           (~self._feedback.hint_type.isin(["greater_less", "perfect_cube"]))]
        
        if len(improvement_areas):
            self._process_feedback()
        elif self._score and self._session.get_session_count() >= 10 and self._games.get_game_count() > 1:
            self._process_recommendation()
    
    def _process_feedback(self):
        data_obj = self._objects.get_object("data")
        improvement_obj = Improvement(self._objects, data_obj.get_data_object("hint_types"))
        self._text_display.display_text("dynamic", "feedback_text", improvement_obj.get_feedback())
        self._feedback_type = "improvement"
        self._record_game_feedback(improvement_area_id=improvement_obj.get_improvement_area_id())
    
    def _process_recommendation(self):
        recommendation_obj = Recommendation(self._objects, self._score)
        predicted_field, recommendation = recommendation_obj.get_recommendation()
        self._text_display.display_text("text", "feedback_text", "recommendation", predicted_field, recommendation)
        self._feedback_type = "recommendation"
        self._record_game_feedback(recommendation_type=predicted_field)
    
    def _record_game_feedback(self, improvement_area_id=None, recommendation_type=None):
        db_update_params = {"entry_type": "Updated", "update_type": "feedback", "feedback_type": self._feedback_type,
                            "improvement_area_id": improvement_area_id, "recommendation_type": recommendation_type}
        self._session.update_database("outcome", db_update_params)



class FeedbackManager:
    """
    The FeedbackManager class stores the feedback collected during a game and manages the type of feedback
    provided by delegating feedback collection to the appropriate Feedback subclasses.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._session = self._objects.get_object("session")
        self._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
    
    def get_guess_feedback(self, guess, guess_concepts):
        if self._session.get_total_hints_given()[0]:
            guess_feedback = GuessFeedback(self._objects, self._feedback, guess)
            feedback_ind = guess_feedback.get_feedback(guess_concepts)
            return feedback_ind
    
    def get_game_feedback(self, score):
        game_feedback = GameFeedback(self._objects, self._feedback, score)
        game_feedback.get_feedback()
    
    def get_feedback_df(self):
        return self._feedback