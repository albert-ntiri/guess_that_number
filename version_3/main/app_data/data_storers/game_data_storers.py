"""
The game_data_storers.py module is part of the data_storers package.  It consists of classes for storing
data at the start of a game, based on user entries for the level of difficulty or the custom range.

Classes:
    GameDataStorer
    GameEntry
    GameErrorEntry
    GameStorageManager
"""


from app_data.data_storers.data_storer_components import DataStorer, ErrorStorer, StorageManager



class GameDataStorer(DataStorer):
    """
    The GameDataStorer class inherits from DataStorer.  It is for entries into the game table in the database.
    It does not add any new functionality; it is there for organizational purposes.
    """
    
    def update_db_table(self):
        pass
    
    def _set_parameters(self):
        pass



class GameEntry(GameDataStorer):
    """
    The GameEntry class inherits from GameDataStorer.  It implements the updates for new games started without
    errors.
    """
    
    _update_query = """
        INSERT INTO game(session_id, level_of_difficulty_type_id, range_low, range_high, winning_number, time, error) 
        VALUES (:session_id, :level_of_difficulty_type_id, :range_low, :range_high, :winning_number, 
                datetime('now', 'localtime'), :error);
        """
    
    def __init__(self, session, settings):
        super().__init__(session)
        self._settings = settings
        self._level_id = self._settings.get_setting("level of difficulty id")
        self._range_low, self._range_high = self._settings.get_setting("number range")
        self._winning_number = self._settings.get_setting("winning number")
    
    def update_db_table(self):
        self._set_parameters()
        self._db.run_query(GameEntry._update_query, self._parameters, _db_path=self._session._db_path)
    
    def _set_parameters(self):
        self._parameters.update({
            "level_of_difficulty_type_id": int(self._level_id),
            "range_low": int(self._range_low),
            "range_high": int(self._range_high),
            "winning_number": int(self._winning_number),
            "error": 0
        })



class GameErrorEntry(GameDataStorer, ErrorStorer):
    """
    The GameErrorEntry class inherits from GameDataStorer and ErrorStorer.  It implements the updates for errors
    when inputting a custom range.
    """
    
    _update_query = """
        INSERT INTO game(session_id, time, error, error_type_id)
        VALUES (:session_id, datetime('now', 'localtime'), :error, :error_type_id);
        """
    
    def __init__(self, session, error_type):
        super().__init__(session)
        self._error_type = error_type
    
    def update_db_table(self):
        self._set_parameters()
        self._parameters = self.add_error_info(self._parameters, self._error_type)
        self._db.run_query(GameErrorEntry._update_query, self._parameters, _db_path=self._session._db_path)



class GameStorageManager(StorageManager):
    """
    The GameStorageManager class is the manager class for database updates when a game is initiated.  It
    inherits from StorageManager.
    """
    
    def __init__(self, session, objects):
        super().__init__(session, objects)
        self._record_type = "Game"
    
    def update_database(self, db_update_params):
        if db_update_params["error"]:
            game_entry_obj = GameErrorEntry(self._session, db_update_params["error_type"])
        else:
            game_entry_obj = GameEntry(self._session, db_update_params["settings"])
        
        self._process_update(game_entry_obj)