"""
The game_settings.py module is part of the game package.  It is for setting the parameters for the
game, including the winning number, the level of difficulty, the number range, and the penalty.

Classes:
    GameSettings
"""


from resources.infrastructure.data import CustomLevel



class GameSettings:
    """
    The GameSettings class stores and provides access to information specific to a game.
    
    Attributes:
        _active: A boolean value indicating whether the game is currently being played.
        _winning_number: The number the user has to guess to win the game.
        _level_object: An object of the LevelOfDifficultyTypes class.
        _numbers: An object of the Number class.
        _settings: A dictionary containing values for different settings for the game.
    """
    
    def __init__(self, numbers, level_obj):
        self._active = False
        self._winning_number = 0
        self._level_obj = level_obj
        self._numbers = numbers
        self._settings = {}
    
    def get_setting(self, setting_name):
        return self._settings[setting_name]
    
    def set_game_settings(self, low_range, high_range):
        self._set_active_flag()
        
        result = self._set_range(low_range, high_range)
        if result is not None:
            return result
        
        self._set_winning_number()
    
    def _set_active_flag(self):
        self._active = True
    
    def _set_range(self, low_range, high_range):
        result = self._numbers.validate_user_entry("number range", (low_range, high_range))
        
        if isinstance(result, tuple):
            self._level_obj = CustomLevel(num_range=result)
            self._add_level_to_settings_dict()
        elif result == "comparison" or result == "invalid":
            return result
        else:
            self._add_level_to_settings_dict()
            return
    
    def _set_winning_number(self):
        low_num, high_num = self._level_obj.get_number_range()
        self._winning_number = self._numbers.get_random_numbers((low_num, high_num + 1), n=1)
        self._settings["winning number"] = self._winning_number
    
    def _add_level_to_settings_dict(self):
        self._settings["level of difficulty id"] = self._level_obj.get_id()
        self._settings["level of difficulty name"] = self._level_obj.get_name()
        self._settings["number range"] = self._level_obj.get_number_range()
        self._settings["penalty"] = self._level_obj.get_penalty()
    
    @property
    def active(self):
        return self._active