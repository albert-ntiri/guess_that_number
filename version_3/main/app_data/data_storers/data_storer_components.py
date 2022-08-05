"""
The data_storer_components.py module is part of the data_storers package.  It consists of base classes
for the different types of data storers.  None of the classes in this module are meant to be instantiated
directly.

Classes:
    DataStorer
    ErrorStorer
    GameComponentStorer
    StorageManager
"""


from resources.infrastructure.iterable_log_entries import DBRecordLogEntry



class DataStorer:
    """
    The DataStorer class defines a template for updating the database with information from a game.  It is
    not meant to be instantiated.  Instead, its subclasses, in most cases multiple levels down, are instantiated
    to update a table in the database based on a specific situation.  The update_db_table method is used to
    run the query.  The _set_parameters method is used to customize the variables needed for the query.
    """
    
    _update_query = ""
    
    def __init__(self, session):
        self._session = session
        self._db = self._session.get_database()
        self._session_id = self._session.session_id
        self._parameters = {"session_id": int(self._session_id)}
    
    def update_db_table(self):
        pass
    
    def _set_parameters(self):
        pass
    
    def get_parameters(self):
        return self._parameters



class ErrorStorer:
    """
    The ErrorStorer class is an interface for storing error messages in the database.  It has a method that
    adds an error type id and error indicator and adds them to an existing list of parameters.
    """
    
    def add_error_info(self, parameters, error_type):
        error_type_id_query = self._session.build_query("id", "error_type", "code", f"'{error_type}'")
        error_type_id = self._db.run_query(error_type_id_query, fetch='one', _db_path=self._session._db_path)[0]
        
        parameters.update({
            'error': 1, 
            'error_type_id': int(error_type_id)
        })
        
        return parameters



class GameComponentStorer(DataStorer):
    """
    The GameComponentStorer class inherits from DataStorer.  It is for entries that add new information about
    a game.  It updates the parameters attribute with the game_id.
    """
    
    def __init__(self, session):
        super().__init__(session)
        self._game_id = self._session.current_game_id
        
        self._parameters.update({
            "game_id": int(self._game_id),
        })
    
    def update_db_table(self):
        pass
    
    def _set_parameters(self):
        pass



class StorageManager:
    """
    The StorageManager class is the base class for the manager classes for each type of database update.
    Its main method, update_database is used to delegate the specific implementation of the update to the
    appropriate data storer object.
    """
    
    def __init__(self, session, objects):
        self._objects = objects
        self._session = session
        self._logs = self._objects.get_object("logs")
        
        self._record_type = ""
    
    def update_database(self, db_update_params):
        pass
    
    def _process_update(self, db_update_obj, entry_type="Entered"):
        """This method standardizes database updates of all types by running the specific data storer object's
        update_db_table method and then logging the entry in the database log."""
        
        db_update_obj.update_db_table()
        if self._logs:
            db_record_log_entry = DBRecordLogEntry(self._logs, self._record_type, entry_type, db_update_obj.get_parameters())
            db_record_log_entry.add_log_entry("database")