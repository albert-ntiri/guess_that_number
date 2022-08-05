"""
The guess.py module is part of the game package.  It is for taking in guesses, evaluating them, and
updating the game accordingly.  Those updates include the score, the number of guesses remaining, the
hint displayed on the screen, and whether the game is still active or complete.

Classes:
    Guess
    InvalidGuess
    ValidGuess
    CorrectGuess
    IncorrectGuess
    GuessManager
"""


from resources.infrastructure.log_entries import NewGuessLogEntry
from resources.infrastructure.iterable_log_entries import RemainingHintsLogEntry



class Guess:
    """
    The Guess class is the base class for guesses in a game.  Its main method, process_guess, is implemented by
    its subclasses based on whether the guess is invalid, correct, or incorrect, as well as the current status
    of the game.  It is not meant to be instantiated directly.
    """
    
    def __init__(self, guess, objects):
        self._objects = objects
        self._session = self._objects.get_object("session")
        self._stats = self._objects.get_object("stats")
        self._text_display = self._objects.get_object("text_display")
        
        self._guess = guess
    
    def process_guess(self):
        pass
    
    def _update_game_state(self, message, feedback=None, error=False, error_type=None):
        self._stats.update_game_stats()
        self._update_db(message, feedback, error, error_type)
        self._update_screen_text(message)
    
    def _update_screen_text(self, message):
        self._text_display.display_text("dynamic", "hint_text", message)
        self._update_status()
    
    def _update_db(self, message, feedback=None, error=False, error_type=None):
        db_update_params = {"guess": self._guess, "hint": message, "feedback": feedback, "error_type": error_type}
        if error:
            db_update_params["error"] = True
        else:
            db_update_params["error"] = False
        
        self._session.update_database("guess", db_update_params)
    
    def _update_status(self):
        """This method calculates the number of guesses the user has left and displays it on the game page."""
        
        guesses_remaining = self._stats.get_value("guesses remaining")
        self._text_display.display_text("text", "status_text", "status", guesses_remaining)
    
    def get_guess(self):
        return self._guess



class InvalidGuess(Guess):
    """
    The InvalidGuess class is for guesses that are not integers or are outside of the specified range for the
    game.  It inherits from Guess.
    """
    
    def __init__(self, guess, objects, error_obj):
        super().__init__(guess, objects)
        self._error_obj = error_obj
        self._error_type = self._error_obj.get_name()
        self._error_message = self._error_obj.get_message()
    
    def process_guess(self):
        self._update_game_state(self._error_message, error=True, error_type=self._error_type)



class ValidGuess(Guess):
    """
    The ValidGuess class is the base class for guesses that are integers within the specified range.  It inherits
    from Guess.  It is not meant to be instantiated directly.
    """
    
    def process_guess(self):
        pass



class CorrectGuess(ValidGuess):
    """
    The CorrectGuess class is for guesses that match the winning number.  It inherits from ValidGuess.
    """
    
    def process_guess(self):
        db_update_params = {"guess": self._guess, "hint": None, "feedback": None, "error": False, "error_type": None}
        self._session.update_database("guess", db_update_params)
        return "win"



class IncorrectGuess(ValidGuess):
    """
    The IncorrectGuess class is for guesses that do not match the winning number.  It inherits from ValidGuess.
    """
    
    def __init__(self, guess, objects):
        super().__init__(guess, objects)
        self._hints = self._objects.get_object("hints")
        self._analytics = self._objects.get_object("analytics")
        self._feedback = self._objects.get_object("feedback")
    
    def process_guess(self):
        guess_concepts = self._hints.get_concepts(self._guess)
        if self._hints.get_hint_count("pool") > 0 and self._stats.get_value("guesses remaining") > 1:
            self._update_metrics()
            hint = self._hints.get_new_hint(guess_concepts, self._guess)
            feedback_ind = self._feedback.get_guess_feedback(self._guess, guess_concepts)
            self._update_game_state(hint, feedback_ind)
        elif self._stats.get_value("guesses remaining") > 1:
            self._update_metrics()
            hint = self._hints.get_new_hint(guess_concepts, self._guess)
            self._update_game_state(hint)
        else:
            db_update_params = {"guess": self._guess, "hint": None, "feedback": None, "error": False, "error_type": None}
            self._session.update_database("guess", db_update_params)
            return "lose"
    
    def _update_metrics(self):
        if self._analytics:
            self._analytics.update_user_metrics("new guess")



class GuessManager:
    """
    The GuessManager class determines the appropriate Guess subclass to instantiate based on guess that is
    passed in and delegates the processing of the guess to that subclass.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._settings = self._objects.get_object("settings")
        self._hints = self._objects.get_object("hints")
        self._numbers = self._objects.get_object("numbers")
        self._data = self._objects.get_object("data")
        self._text_display = self._objects.get_object("text_display")
        self._logs = self._objects.get_object("logs")
        
        self.guesses = []
    
    def process_guess(self, guess):
        guess_obj = self._get_guess_obj(guess)
        outcome = guess_obj.process_guess()
        self.guesses.append(guess_obj)
        
        if self._logs:
            self._log_guess(guess_obj, outcome)
        
        return outcome
    
    def _get_guess_obj(self, guess):
        error_type = self._numbers.validate_user_entry("guess", guess, self._settings.get_setting("number range"))
        if error_type:
            guess_error_obj = self._data.get_sub_data_object("errors", error_type)
            guess_obj = self._objects.create_object(InvalidGuess, "guess_obj", GuessManager, guess, self._objects,
                                                    guess_error_obj)
        else:
            guess = int(guess)
            if guess == self._settings.get_setting("winning number"):
                guess_obj = self._objects.create_object(CorrectGuess, "guess_obj", GuessManager, guess, self._objects)
            else:
                guess_obj = self._objects.create_object(IncorrectGuess, "guess_obj", GuessManager, guess, self._objects)
        
        return guess_obj
    
    def _log_guess(self, guess_obj, outcome):
        message_type = "error" if isinstance(guess_obj, InvalidGuess) else "" if outcome else "hint"
        message = self._text_display.get_text("hint_text") if message_type else ""
        
        new_guess_log_entry = NewGuessLogEntry(self._logs, len(self.guesses), guess_obj.get_guess(), message, message_type)
        new_guess_log_entry.add_log_entry("main")
        
        remaining_hints_log_entry = RemainingHintsLogEntry(self._logs, new_guess_log_entry, self._hints.get_hints("relevant"),
                                                           self._hints.get_hints("redundant"), self._hints.get_hints("pool"))
        remaining_hints_log_entry.add_log_entry("hints")