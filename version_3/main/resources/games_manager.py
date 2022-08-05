"""
The games_manager.py module is part of the resources package.  It is for management of Game objects and
aggregate-level data across multiple games within a session of the app.  It is also the bridge between the
classes in the guess_that_number.py file and the specific functionality of each game a user plays.

Classes:
    GamesManager
"""


from game.game import Game
import pandas as pd



class GamesManager:
    """
    The GamesManager class takes in commands from the WelcomePage, GamePage, and FarewellPage classes and
    redirects them to the appropriate Game class when the user initiates an action.  It also holds aggregate
    data for a session.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._data = self._objects.get_object("data")
        
        self._games = []
        self._current_game = None
        self._aggregate_feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
    
    def add_game(self):
        self._current_game = self._objects.create_object(Game, "current_game", GamesManager, self._objects)
        
        result = self._current_game.configure_game()
        if not result:
            analytics = self._objects.get_object("analytics")
            if analytics:
                analytics.update_user_metrics("new game")
        
        self._games.append(self._current_game)
        
        return result
    
    def add_guess_to_current_game(self):
        outcome = self._current_game.add_guess()
        return outcome
    
    def end_current_game(self, outcome):
        self._current_game.summarize_game(outcome)
    
    def update_aggregate_feedback(self, game_feedback):
        self._aggregate_feedback = pd.concat([self._aggregate_feedback, game_feedback], ignore_index=True)
    
    def get_aggregate_feedback(self):
        return self._aggregate_feedback.copy()
    
    def reset_current_game(self):
        self._data.reset()
        self._current_game.clear_text_variables()
        self._current_game = None
    
    def get_current_game_outcome(self):
        return self._current_game.get_outcome()
    
    def get_game_count(self, games_with_outcome=True):
        if games_with_outcome:
            return len([game for game in self._games if game.get_outcome() in ["win", "lose"]])
        return len(self._games)