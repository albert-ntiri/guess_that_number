"""
The hint_manager.py module is part of the game package.  It is for accessing hints for a particular game,
selecting hints as the game goes on, and updating the list of available hints left.  It is the bridge
between the ConceptManager and the rest of the Game components.

Classes:
    HintManager
"""


from concepts.concept_manager import ConceptManager



class HintManager:
    """
    The HintManager class manages and controls access to the hints for a game.
    
    Attributes:
        _hint_pool: A list of all possible hints for a game, based on the winning number.
        _relevant_hints: A subset of the hint_pool list that provides new information about the winning number.
        _redundant_hints: A subset of the hint_pool list that does not provide new information about the winning number.
        _hints_given: A list of hints that have been shown to the user during a game.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._numbers = self._objects.get_object("numbers")
        self._session = self._objects.get_object("session")
        self._data = self._objects.get_object("data")
        self._settings = self._objects.get_object("settings")
        
        self._hint_pool = []
        self._relevant_hints = []
        self._redundant_hints = []
        self._hints_given = []
    
    def get_hint_list(self, _db=True):
        game_concepts = self.get_concepts(self._settings.get_setting("winning number"), store_object=True, _db=_db)
        self._hint_pool = game_concepts.generate_hints(check_db=_db, _db_path=self._session._db_path)
        self._relevant_hints = list(self._hint_pool)
    
    def get_concepts(self, number, store_object=False, _db=True):
        db = self._session.get_database() if _db else None
        
        create_object_args = (number, self._numbers, db, self._data)
        if store_object:
            concepts = self._objects.create_object(ConceptManager, "game_concepts", HintManager, *create_object_args)
        else:
            concepts = ConceptManager(*create_object_args)
        
        return concepts
    
    def get_new_hint(self, guess_concepts, guess, _check_db=True):
        if self.get_hint_count("pool") > 0:
            self._get_relevant_hints(guess_concepts, _check_db=_check_db)
            hint = self._select_hint()
            self._hints_given.append(hint)
        else:
            hint = guess_concepts.check_greater_or_less(guess, self._settings.get_setting("winning number"))
        
        return hint
    
    def get_hint_count(self, hint_list_name):
        hint_list = self.get_hints(hint_list_name)
        return len(hint_list)
    
    def get_hints(self, hint_list_name):
        hint_lists = {
            "pool": self._hint_pool,
            "relevant": self._relevant_hints,
            "redundant": self._redundant_hints,
            "given": self._hints_given
            }
        
        if hint_list_name in hint_lists:
            return hint_lists[hint_list_name].copy()
    
    def _get_relevant_hints(self, guess_concepts, _check_db=True):
        guess_hints = guess_concepts.generate_hints(check_db=_check_db, filter_results=False, _db_path=self._session._db_path)
        self._redundant_hints = self._redundant_hints + list(set(self._hint_pool).intersection(set(guess_hints)))
        self._relevant_hints = [hint for hint in self._relevant_hints if hint not in self._redundant_hints]
    
    def _select_hint(self):
        try:
            hint = self._get_hint_from_list(self._relevant_hints)
        except ValueError:
            hint = self._get_hint_from_list(self._redundant_hints)
        
        self._update_hint_pool()
        
        return hint
    
    def _get_hint_from_list(self, hint_list):
        hint_index = self._numbers.get_random_numbers((0, len(hint_list)), n=1)
        hint = hint_list.pop(hint_index)
        return hint
    
    def _update_hint_pool(self):
        self._hint_pool = self._relevant_hints + self._redundant_hints