"""
The game.py module is part of the game package.  It is for high-level management of all components of a
single game.

Classes:
    Game
"""


from game.game_settings import GameSettings
from game.game_stats import GameStatsManager
from game.hint_manager import HintManager
from game.guess import GuessManager
from game.feedback import FeedbackManager
from game.game_initializers import GameInitializer
from game.game_summarizers import EndGameManager

from resources.infrastructure.log_entries import NewGameLogEntry
from resources.infrastructure.iterable_log_entries import NewHintsLogEntry



class Game:
    """
    The Game class creates and manages the objects responsible for different components of a game.  Some of
    these objects are stored as attributes.  Others, such as GameInitializer and EndGameManager, are
    instantiated only when needed.
    
    Attributes:
        _settings: An object of the GameSettings class.
        _stats: An object of the GameStatsManager class.
        _hints: An object of the HintManager class.
        _guesses: An object of the GuessManager class.
        _feedback: An object of the FeedbackManager class.
        
        _outcome: Whether the user won, lost, or quit the game.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._text_display = self._objects.get_object("text_display")
        self._numbers = self._objects.get_object("numbers")
        self._level_obj = self._objects.get_object("level_obj")
        self._logs = self._objects.get_object("logs")
        
        self._settings = self._objects.create_object(GameSettings, "settings", Game, self._numbers, self._level_obj)
        self._stats = self._objects.create_object(GameStatsManager, "stats", Game, self._objects)
        self._hints = self._objects.create_object(HintManager, "hints", Game, self._objects)
        self._guesses = self._objects.create_object(GuessManager, "guesses", Game, self._objects)
        self._feedback = self._objects.create_object(FeedbackManager, "feedback", Game, self._objects)
        
        self._outcome = ""
    
    def configure_game(self):
        game_initializer = GameInitializer(self._objects)
        
        result = game_initializer.initialize_game()
        if result:
            return result
        
        self._stats.update_game_stats()
        self._display_initial_status()
        
        if self._logs:
            new_game_log_entry = NewGameLogEntry(self._logs, self._settings)
            new_game_log_entry.log_all()
            
            new_hints_log_entry = NewHintsLogEntry(self._logs, self._hints.get_hints("pool"))
            new_hints_log_entry.add_log_entry("hints")
    
    def add_guess(self):
        guess = self._text_display.get_text("guess")
        outcome = self._guesses.process_guess(guess)
        
        if outcome:
            return outcome
    
    def summarize_game(self, outcome):
        self._outcome = outcome
        end_game_manager = EndGameManager(self._objects, outcome)
        end_game_manager.run_game_summary()
    
    def clear_text_variables(self):
        self._text_display.clear_all_variables()
    
    def get_outcome(self):
        return self._outcome
    
    def _display_initial_status(self):
        guess_range_low, guess_range_high = self._settings.get_setting("number range")
        self._text_display.display_text("text", "guess_prompt_text", "guess_prompt", guess_range_low, guess_range_high)
        
        guesses_remaining = self._stats.get_value("guesses remaining")
        self._text_display.display_text("text", "status_text", "status", guesses_remaining)