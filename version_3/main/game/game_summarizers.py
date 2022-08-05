"""
The game_summarizers.py module is part of the game package.  It is for concluding a game, which involves
determining the outcome, generating and displaying feedback, and inserting game data into the database.

Classes:
    GameSummarizer
    WinGameSummarizer
    LoseGameSummarizer
    QuitGameSummarizer
    EndGameManager
"""


from resources.infrastructure.log_entries import EndGameLogEntry



class GameSummarizer:
    """
    The GameSummarizer class is the base class for the different game summarizers.  It is not meant to be
    instantiated directly.
    """
    
    def __init__(self, objects, outcome):
        self._objects = objects
        self._session = self._objects.get_object("session")
        self._text_display = self._objects.get_object("text_display")
        self._feedback = self._objects.get_object("feedback")
        self._logs = self._objects.get_object("logs")
        self._outcome_obj = self._get_outcome_object(outcome)
        self._score = self._get_score()
    
    def run_game_summary(self):
        self._update_database()
        self._get_game_feedback()
        self._get_end_game_message()
        self._update_user_metrics()
        if self._logs:
            self._log_game_summary()
    
    def _update_database(self):
        self._session.update_database("outcome", {"entry_type": "New", "outcome_obj": self._outcome_obj})
    
    def _get_game_feedback(self):
        pass
    
    def _get_end_game_message(self):
        self._text_display.display_text("data", "last_msg", self._outcome_obj)
    
    def _update_user_metrics(self):
        analytics = self._objects.get_object("analytics")
        if analytics:
            analytics.update_user_metrics("end game")
    
    def _log_game_summary(self):
        feedback = self._text_display.get_text("feedback_text")
        end_game_log_entry = EndGameLogEntry(self._logs, self._outcome_obj.get_name(), self._score, feedback)
        end_game_log_entry.log_all()
        
        game_data_query = f"""
        SELECT *
        FROM game gm
            LEFT JOIN guess gs ON gm.game_id = gs.game_id
            LEFT JOIN outcome o ON gm.game_id = o.game_id
        WHERE gm.game_id = (SELECT MAX(game_id) FROM game WHERE session_id = {self._session.session_id})
        ORDER BY gm.game_id, gs.guess_id
        ;"""
        db_manager = self._objects.get_object("db_manager")
        db_manager.log_query_result(game_data_query, "Game Data")
    
    def _get_outcome_object(self, outcome):
        data = self._objects.get_object("data")
        outcome_obj = data.get_sub_data_object("outcomes", outcome)
        return outcome_obj
    
    def _get_score(self):
        pass



class WinGameSummarizer(GameSummarizer):
    """
    The WinGameSummarizer class is used when the user successfully guesses the winning number.  It
    inherits from GameSummarizer.
    """
    
    def _get_game_feedback(self):
        self._feedback.get_game_feedback(self._score)
    
    def _get_score(self):
        stats = self._objects.get_object("stats")
        score = stats.get_value("score")
        self._outcome_obj.score = score
        return score



class LoseGameSummarizer(GameSummarizer):
    """
    The LoseGameSummarizer class is used when the user runs out of tries.  It inherits from
    GameSummarizer.
    """
    
    def _get_game_feedback(self):
        self._feedback.get_game_feedback(self._score)



class QuitGameSummarizer(GameSummarizer):
    """
    The QuitGameSummarizer class is used when the user runs selects the quit option before the game
    concludes.  It inherits from GameSummarizer.
    """



class EndGameManager:
    """
    The EndGameManager class is instantiated by a Game object when a game concludes.  It determines
    the appropriate GameSummarizer subclass to instantiate based on the outcome that is passed in.
    """
    
    def __init__(self, objects, outcome):
        self._objects = objects
        self._outcome = outcome
        self._game_summarizers = {
            "win": WinGameSummarizer,
            "lose": LoseGameSummarizer,
            "quit": QuitGameSummarizer
        }
    
    def run_game_summary(self):
        game_summarizer = self._get_game_summarizer()
        game_summarizer.run_game_summary()
    
    def _get_game_summarizer(self):
        try:
            summarizer_class = self._game_summarizers[self._outcome]
            game_summarizer = summarizer_class(self._objects, self._outcome)
            return game_summarizer
        except KeyError:
            return