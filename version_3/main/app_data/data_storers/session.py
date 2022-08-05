"""
The session.py module is part of the data_storers package.  It is for collecting and storing data for all
of the user's activity on the app.  It enters this information into the database.  It serves as the bridge
between the specific data storers and the rest of the app.

Classes:
    Session
"""


from app_data.data_storers.game_data_storers import GameStorageManager
from app_data.data_storers.guess_data_storers import GuessStorageManager
from app_data.data_storers.outcome_data_storers import OutcomeStorageManager
from resources.infrastructure.log_entries import NewSessionLogEntry
from resources.infrastructure.iterable_log_entries import DBRecordLogEntry



class Session:
    """
    The Session class captures information about a live session of a user, including information about the 
    games played, guesses, hints, and outcome.  It also contains helper methods to query the database for
    specific information as needed.
    """
    
    def __init__(self, objects, _db_path=None):
        """The constructor method for this class takes in a game object and saves it as an attribute.  It 
        also creates a session, adds it to the session table in the database, saves the session_id as an 
        attribute and instantiates an AppData object."""
        
        self._objects = objects
        self._db_manager = self._objects.get_object("db_manager")
        self._db = self.get_database()
        self._logs = self._objects.get_object("logs")
        self._db_path = _db_path
        self._data_storers = {
            "Game": GameStorageManager(self, self._objects),
            "Guess": GuessStorageManager(self, self._objects),
            "Outcome": OutcomeStorageManager(self, self._objects)
            }
        
        self.add_session_record_to_db()
        self.session_id = self._get_session_id()
        
        self._game_ids = []
        self._current_game_id = None
    
    @property
    def current_game_id(self):
        return self._current_game_id
    
    @current_game_id.setter
    def current_game_id(self, new_value):
        self._current_game_id = new_value
    
    def add_session_record_to_db(self):
        """This method adds a new record to the session table in the database when the app is opened."""
        
        query = "INSERT INTO session(time) VALUES (datetime('now', 'localtime'))"
        self._db.run_query(query, _db_path=self._db_path)
    
    def update_database(self, update_type, update_db_params):
        """This method delegates database updates to the appropriate data storers based on the type of
        update: a new game initiated, a new guess entered, or a game concluding."""
        
        data_storer = self._data_storers[update_type.title()]
        data_storer.update_database(update_db_params)
        
        if update_type == "game":
            self.current_game_id = self._get_game_id()
    
    def get_database(self):
        return self._db_manager.get_database()
    
    def get_total_hints_given(self):
        """This method returns the number of hints that were given for the most recent game of a session."""
        
        query = """SELECT COUNT(hint) 
                   FROM guess 
                   WHERE game_id = """ + str(self.current_game_id) + """ 
                       AND hint IS NOT NULL"""
        
        total_hints_given = self._db.run_query(query, fetch='one', _db_path=self._db_path)
        
        return total_hints_given
    
    def get_last_hint(self):
        """This method returns the last hint and hint type that was given for the most recent game of a 
        session."""
        
        query = """SELECT t.code, g.hint 
                   FROM guess g
                       JOIN hint_type t ON g.hint_type_id = t.id
                   WHERE g.game_id = """ + str(self.current_game_id) + """ 
                   ORDER BY g.guess_id DESC LIMIT 1"""
        
        hint_type, hint = self._db.run_query(query, fetch='one', _db_path=self._db_path)
        
        return hint_type, hint
    
    def get_session_count(self):
        """This method returns the number of rows in the session table."""
        
        query = self.build_query("COUNT(*)", "session")
        session_count = self._db.run_query(query, fetch='one', _db_path=self._db_path)[0]
        
        return int(session_count)
    
    def _get_session_id(self):
        """This method returns the most recent session_id from the session table."""
        
        query = "SELECT id FROM session ORDER BY time DESC LIMIT 1"
        session_id = self._db.run_query(query, fetch='one', _db_path=self._db_path)[0]
        
        if self._logs:
            session_log_entry = NewSessionLogEntry(self._logs, session_id)
            session_log_entry.add_log_entry("database")
        
        return session_id
    
    def _get_game_id(self):
        game_id_query = """SELECT game_id FROM game WHERE session_id = """ + str(self.session_id) + """ 
                           ORDER BY time DESC LIMIT 1"""
        game_id = self._db.run_query(game_id_query, fetch='one', _db_path=self._db_path)[0]
        self._game_ids.append(game_id)
        
        return game_id
    
    # def _process_update(self, db_update_obj, record_type, entry_type):
    #     db_update_obj.update_db_table()
    #     if self._logs:
    #         db_record_log_entry = DBRecordLogEntry(self._logs, record_type, entry_type, db_update_obj.get_parameters())
    #         db_record_log_entry.add_log_entry("database")
    
    @staticmethod
    def build_query(target_col, table, filter_col=None, filter_val=None):
        query = "SELECT " + target_col + " FROM " + table
        if filter_col and filter_val:
            query = query + " WHERE " + filter_col + " = " + filter_val
        return query