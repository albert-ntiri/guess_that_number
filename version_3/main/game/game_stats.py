"""
The game_stats.py module is part of the game package.  It is for calculating and providing access to
data points related to the state of a game, specifically, the current score and the number of guesses
remaining.

Classes:
    Stat
    GameStat
    GameScore
    GuessesRemaining
    GameStatsManager
"""


from resources.infrastructure.subsystem import BaseClass, Manager



class Stat(BaseClass):
    """
    The Stat class is the base class for data points for a game.  It is not meant to be instantiated
    directly.  It has 2 types of subclasses: 1 for game stats and 1 for user metrics.  The game stats
    classes are part of this module, while the user metrics classes are part of the analytics.py module.
    """
    
    def __init__(self, objects):
        super().__init__()
        self._objects = objects
        
        self._name = ""
        self._value = 0
        
        self._obj_id_method = self.get_name
        self._standardized_method = self.update_stat
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value
    
    def update_stat(self):
        new_value = self._get_new_value() if self._value else self._set_default_value()
        self.value = new_value
    
    def _get_new_value(self):
        pass
    
    def _set_default_value(self):
        pass
    
    def get_name(self):
        return self._name



class GameStat(Stat):
    """
    The GameStat class is the base class for game-related data points.  It inherits from Stat.  It is
    not meant to be instantiated directly.
    """
    
    default_score = 100
    
    def __init__(self, objects):
        super().__init__(objects)
        self._settings = self._objects.get_object("settings")
        self._penalty = 0
    
    def _set_default_value(self):
        self._penalty = self._settings.get_setting("penalty")



class GameScore(GameStat):
    """
    The GameScore class holds and updates the score of a game as it played.  It inherits from GameStat.
    """
    
    def __init__(self, objects):
        super().__init__(objects)
        self._name = "score"
    
    def _get_new_value(self):
        return self._value - self._penalty
    
    def _set_default_value(self):
        super()._set_default_value()
        return GameStat.default_score



class GuessesRemaining(GameStat):
    """
    The GuessesRemaining class holds and updates the number of guesses a user has left in a game.  It
    inherits from GameStat.
    """
    
    def __init__(self, objects):
        super().__init__(objects)
        self._name = "guesses remaining"
    
    def _get_new_value(self):
        return self._value - 1
    
    def _set_default_value(self):
        super()._set_default_value()
        return int(GameStat.default_score / self._penalty)



class GameStatsManager(Manager):
    """
    The GameStatsManager class manages the updates to the GameStat subclasses and provides a way for
    other objects to access the current value of game stats.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._score = GameScore(self._objects)
        self._guesses_remaining = GuessesRemaining(self._objects)
        self._stats_dict = {
            self._score.get_name(): self._score,
            self._guesses_remaining.get_name(): self._guesses_remaining
        }
        super().__init__(GameStat)
    
    def update_game_stats(self):
        self.run_all_subclass_methods()
    
    def get_value(self, stat_name):
        stat_obj = self._stats_dict[stat_name]
        return stat_obj.value