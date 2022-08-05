"""
The game_initializers.py module is part of the game package.  It is for starting games based on user
inputs.  Those user inputs are the selection of level of difficulty and the custom range, if entered.
A different set of actions are taken based on whether the user inputs pass validation.

Classes:
    GameSelection
    ValidSelection
    InvalidSelection
    GameInitializer
"""


from resources.infrastructure.log_entries import RangeErrorLogEntry



class GameSelection:
    """
    The GameSelection class is the base class for the different game initializers.  It is not meant to be
    instantiated directly.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._session = self._objects.get_object("session")
        self._logs = self._objects.get_object("logs")



class ValidSelection(GameSelection):
    """
    The ValidSelection class is used when user inputs pass validation for a game to be played.  It
    inherits from GameSelection.
    """
    
    def __init__(self, objects):
        super().__init__(objects)
        self._hints = self._objects.get_object("hints")
        self._settings = self._objects.get_object("settings")
    
    def process_game_entry(self):
        self._session.update_database("game", {"settings": self._settings, "error": False, "error_type": None})
        self._hints.get_hint_list()



class InvalidSelection(GameSelection):
    """
    The InvalidSelection class is used when user inputs failed validation, prompting the user to edit
    the selection before a game can be played.  It inherits from GameSelection.
    """
    
    def __init__(self, objects, range_error_obj, user_entry):
        super().__init__(objects)
        self._text_display = self._objects.get_object("text_display")
        self._range_error_obj = range_error_obj
        self._user_entry = user_entry
    
    def process_error(self):
        self._display_error_message()
        self._update_db()
    
    def _display_error_message(self):
        self._text_display.display_text("data", "range_error_msg", self._range_error_obj)
        if self._logs:
            range_error_log_entry = RangeErrorLogEntry(self._logs, self._user_entry, self._range_error_obj.get_message())
            range_error_log_entry.add_log_entry("main")
    
    def _update_db(self):
        self._session.update_database("game", {"settings": None, "error": True, "error_type": self._range_error_obj.get_name()})



class GameInitializer:
    """
    The GameInitializer class is instantiated by a Game object when the user attempts to start a game.  It
    determines the appropriate GameSelection subclass to instantiate based on user inputs.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._data = self._objects.get_object("data")
        self._settings = self._objects.get_object("settings")
        self._text_display = self._objects.get_object("text_display")
    
    def initialize_game(self):
        low_range = self._text_display.get_text("low_range")
        high_range = self._text_display.get_text("high_range")
        
        result = self._settings.set_game_settings(low_range, high_range)
        if result is not None:
            range_error_obj = self._data.get_sub_data_object("errors", result)
            selection = InvalidSelection(self._objects, range_error_obj, (low_range, high_range))
            selection.process_error()
            return "error"
        
        selection = ValidSelection(self._objects)
        selection.process_game_entry()