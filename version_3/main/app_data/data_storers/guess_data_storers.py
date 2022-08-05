"""
The guess_data_storers.py module is part of the data_storers package.  It consists of classes for storing
data after each guess, based on the guess, winning number, and hint.

Classes:
    GuessDataStorer
    GuessEntry
    GuessHintEntry
    GuessNoHintEntry
    GuessErrorEntry
    GuessStorageManager
"""


from app_data.data_storers.data_storer_components import GameComponentStorer, ErrorStorer, StorageManager



class GuessDataStorer(GameComponentStorer):
    """
    The GuessDataStorer class inherits from GameComponentStorer.  It is for entries into the guess table in
    the database.  It updates the parameters attribute with the guess.
    """
    
    def __init__(self, session, guess):
        super().__init__(session)
        
        self._parameters.update({
            "guess": guess
        })
    
    def update_db_table(self):
        pass
    
    def _set_parameters(self):
        pass



class GuessEntry(GuessDataStorer):
    """
    The GuessEntry class inherits from GuessDataStorer.  It is for new guesses entered without errors.  It
    updates the parameters attribute with the feedback and error values.
    """
    
    def __init__(self, session, guess, feedback):
        super().__init__(session, guess)
        
        self._parameters.update({
            'feedback': feedback,
            'error': 0
        })
    
    def update_db_table(self):
        pass
    
    def _set_parameters(self):
        pass



class GuessHintEntry(GuessEntry):
    """
    The GuessHintEntry class inherits from GuessEntry.  It implements the updates for new guesses entered
    with a hint.
    """
    
    _update_query = """
        INSERT INTO guess(game_id, session_id, hint_type_id, hint, hint_number, time, guess, feedback, error) 
        VALUES (:game_id, :session_id, :hint_type_id, :hint, :hint_number, datetime('now', 'localtime'), :guess, 
                :feedback, :error);
        """
    
    def __init__(self, session, guess, feedback, hint, hint_types_obj):
        super().__init__(session, guess, feedback)
        self._hint = hint
        self._hint_types_obj = hint_types_obj
        
    def update_db_table(self):
        self._set_parameters()
        self._db.run_query(GuessHintEntry._update_query, self._parameters, _db_path=self._session._db_path)
    
    def _set_parameters(self):
        hint_number = self._session.get_total_hints_given()
        hint_number = 1 if not hint_number else hint_number[0] + 1
        
        hint_obj = self._hint_types_obj.get_hint_obj_from_hint(self._hint)
        hint_type_id = hint_obj.get_id()
        
        hint = self._hint if self._hint else None
        
        self._parameters.update({
            'hint_type_id': int(hint_type_id),
            'hint': hint,
            'hint_number': int(hint_number),
        })



class GuessNoHintEntry(GuessEntry):
    """
    The GuessNoHintEntry class inherits from GuessEntry.  It implements the updates for new guesses entered
    without a hint.
    """
    
    _update_query = """
        INSERT INTO guess(game_id, session_id, time, guess, feedback, error)
        VALUES (:game_id, :session_id, datetime('now', 'localtime'), :guess, :feedback, :error);
        """
    
    def __init__(self, session, guess, feedback):
        super().__init__(session, guess, feedback)
    
    def update_db_table(self):
        self._db.run_query(GuessNoHintEntry._update_query, self._parameters, _db_path=self._session._db_path)



class GuessErrorEntry(GuessDataStorer, ErrorStorer):
    """
    The GuessErrorEntry class inherits from GuessDataStorer and ErrorStorer.  It implements the updates for
    errors when inputting a guess.
    """
    
    _update_query = """
        INSERT INTO guess(game_id, session_id, time, guess, error, error_type_id)
        VALUES (:game_id, :session_id, datetime('now', 'localtime'), :guess, :error, :error_type_id);
        """
    
    def __init__(self, session, guess, error_type):
        super().__init__(session, guess)
        self._error_type = error_type
    
    def update_db_table(self):
        self._set_parameters()
        self._parameters = self.add_error_info(self._parameters, self._error_type)
        self._db.run_query(GuessErrorEntry._update_query, self._parameters, _db_path=self._session._db_path)



class GuessStorageManager(StorageManager):
    """
    The GuessStorageManager class is the manager class for database updates when a guess is entered.  It
    inherits from StorageManager.
    """
    
    def __init__(self, session, objects):
        super().__init__(session, objects)
        self._record_type = "Guess"
    
    def update_database(self, db_update_params):
        """This method adds a record to the guess table in the database when a new guess is entered by 
        the user.  If there is no hint, it omits those columns.  If error is True, it adds the error_type_id 
        corresponding to the error_type that is passed in and leaves the hint information blank."""
        
        if db_update_params["error"]:
            guess_entry_obj = GuessErrorEntry(self._session, db_update_params["guess"], db_update_params["error_type"])
        elif not db_update_params["hint"]:
            guess_entry_obj = GuessNoHintEntry(self._session, db_update_params["guess"], db_update_params["feedback"])
        else:
            data = self._objects.get_object("data")
            hints_obj = data.get_data_object("hint_types")
            guess_entry_obj = GuessHintEntry(self._session, db_update_params["guess"], db_update_params["feedback"],
                                             db_update_params["hint"], hints_obj)
        
        self._process_update(guess_entry_obj)