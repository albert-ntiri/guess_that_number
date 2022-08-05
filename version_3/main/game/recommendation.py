"""
The recommendation.py module is part of the game package.  It is for forming recommendations for the user's
next game based on their performance in the game, compared to a predicted score and outcome of that same game.

Classes:
    Recommendation
"""


from resources.infrastructure.log_entries import PredictionLogEntry, RecommendationTypeLogEntry



class Recommendation:
    """
    The Recommendation class is instantiated by the GameFeedback class.  It is for when there is a recommendation
    for the user's next game.  That recommendation can come in the form of a target score or a higher level
    of difficulty.
    """
    
    def __init__(self, objects, score):
        self._objects = objects
        self._games = self._objects.get_object("games")
        self._session = self._objects.get_object("session")
        self._analytics = self._objects.get_object("analytics")
        self._settings = self._objects.get_object("settings")
        self._logs = self._objects.get_object("logs")
        self._db = self._session.get_database()
        
        self._game_score = score
        self._score_threshold = self._get_score_threshold()
        self._current_game_id = self._session.current_game_id
    
    def get_recommendation(self):
        """This method gets a predicted score and predicted outcome for the user and returns a recommendation 
        based on comparing the predicted score to the actual score.  If the user has played more than 1 game and 
        performed well enough, the user is recommended the next level of difficulty."""
        
        predicted_score, target_score = self._get_score_prediction()
        predicted_outcome = self._get_outcome_prediction()
        
        recommendation = self._derive_recommendation(predicted_score, target_score, predicted_outcome)
        predicted_field, recommendation_type = self._get_recommendation_type(recommendation)
        recommendation_type_log_entry = RecommendationTypeLogEntry(self._logs, recommendation_type, recommendation)
        recommendation_type_log_entry.add_log_entry("prediction")
        
        return predicted_field, recommendation
    
    def _derive_recommendation(self, predicted_score, target_score, predicted_outcome):
        if self._games.get_game_count() > 1:
            if predicted_outcome == "win" and self._game_score > predicted_score and target_score > self._score_threshold:
                next_level_of_difficulty = self._get_next_level_of_difficulty()
                recommendation = next_level_of_difficulty
            else:
                recommendation = target_score
        else:
            recommendation = target_score
        
        return recommendation
    
    def _get_score_prediction(self):
        predicted_score = self._analytics.predict("score", self._current_game_id)
        
        if predicted_score > 100:
            target_score = 100
        elif self._game_score < predicted_score:
            target_score = predicted_score
        else:
            target_score = self._game_score
            
        prediction_log_entry = PredictionLogEntry(self._logs, "score", predicted_score, self._game_score, target_score)
        prediction_log_entry.add_log_entry("prediction")
        
        return predicted_score, target_score
    
    def _get_outcome_prediction(self):
        predicted_outcome = self._analytics.predict("outcome", self._current_game_id)
        prediction_log_entry = PredictionLogEntry(self._logs, "outcome", predicted_outcome)
        prediction_log_entry.add_log_entry("prediction")
        
        return predicted_outcome
    
    def _get_recommendation_type(self, recommendation):
        predicted_field = "target score" if isinstance(recommendation, int) else "level of difficulty"
        recommendation_type = "score" if predicted_field == "target score" else "outcome"
        return predicted_field, recommendation_type
    
    def _get_next_level_of_difficulty(self):
        """This method returns the level of difficulty that is one level higher than that of the most recent 
        game.  If the most recent level is the highest, it returns that same level."""
        
        level_id_query = self._session.build_query("level_of_difficulty_type_id", "game", "game_id", str(self._current_game_id))
        level_id = self._db.run_query(level_id_query, fetch='one')[0]
        
        next_level_id = int(level_id) + 1 if level_id < 4 else 4
        
        next_level_query = self._session.build_query("code", "level_of_difficulty_type", "id", str(next_level_id))
        next_level = self._db.run_query(next_level_query, fetch='one')[0]
        
        return next_level
    
    def _get_score_threshold(self):
        return 100 - (self._settings.get_setting("penalty") * 2)