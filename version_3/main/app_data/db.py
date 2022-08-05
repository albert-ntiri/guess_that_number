"""
The db.py module is part of the app_data package.  It consists of 2 sets of classes: 1 for establishing a
database connection and 1 for building the database for the app.

Classes:
    DBConnector
    SqliteDBConnector
    PostgreSqlDBConnector
    
    DBScriptor
    CreateDBScriptor
    PopulateTypesDBScriptor
    PopulateHintsDBScriptor
    
    DBManager
"""


import os.path
import pandas as pd

from resources.infrastructure.log_entries import DBConnectorLogEntry, DBScriptorLogEntry, DBTableLogEntry, HintsPopulatedLogEntry
from resources.infrastructure.iterable_log_entries import DBCreatedLogEntry, DBQueryLogEntry
from resources.variables.create_db_queries import create_table_queries
from concepts.concept_manager import ConceptManager

import sqlite3
# import psycopg2   # PostgreSQL



class DBConnector:
    """
    The DBConnector class is a base class for establishing a connection to a database and executing queries.
    Its subclasses implement the database connection based on the source of the database.  It defines one
    method to run a query that it defers to its subclasses to implement.
    """
    
    _main_directory = os.path.dirname(os.path.abspath('guess_that_number.py'))
    _name = ''
    _db_name = ''
    _db_absolute_path = ''
    
    def run_query(self):
        pass



class SqliteDBConnector(DBConnector):
    """
    The SqliteDBConnector class implements the connection to a SQLite database.  It inherits from DBConnector.
    """
    
    _name = 'Sqlite'
    _db_name = 'sqlite_guess_that_number.db'
    _db_absolute_path = os.path.join(DBConnector._main_directory, _db_name)
    
    def run_query(self, query, parameters=None, fetch=None, include_cols=False, _db_path=None):
        """This method creates a database connection and runs a query.  If fetch_result is true, it
        returns the result."""
        
        db_path = _db_path if _db_path else SqliteDBConnector._db_absolute_path
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        if parameters:
            if fetch == 'all':
                result = c.execute(query, parameters).fetchall()
            elif fetch == 'one':
                result = c.execute(query, parameters).fetchone()
            else:
                c.execute(query, parameters)
                result = None
        else:
            if fetch == 'all':
                result = c.execute(query).fetchall()
            elif fetch == 'one':
                result = c.execute(query).fetchone()
            else:
                c.execute(query)
                result = None
        
        if include_cols:
            cols = tuple([x[0] for x in c.description])
        
        conn.commit()
        conn.close()
        
        if include_cols:
            return result, cols
        return result



class PostgreSqlDBConnector(DBConnector):
    """
    The PostgreSqlDBConnector class implements the connection to a PostgreSQL database.  It inherits from
    DBConnector.
    """
    
    _name = 'PostgreSql'
    _db_name = 'postgresql_guess_that_number.db'
    _db_absolute_path = os.path.join(DBConnector._main_directory, _db_name)
    
    def run_query(self):
        pass



class DBScriptor:
    """
    The DBScriptor class is a base class for running scripts from the database.  It contains a DBConnector
    object that it uses to connect to the database and run queries.  Its execute script method defines the
    set of queries to be run in the script.  It is deferred to its subclasses to implement.
    """
    
    _name = ""
    
    def __init__(self, db_manager, logs):
        self._db_manager = db_manager
        self._db = self._db_manager.get_database()
        self._logs = logs
    
    def execute_script(self):
        pass
    
    def log_result(self, query, result_name):
        results, cols = self._db.run_query(query, fetch="all", include_cols=True)
        results_df = pd.DataFrame(results, columns=cols)
        db_query_log_entry = DBQueryLogEntry(self._logs, result_name, results_df)
        db_query_log_entry.add_log_entry("database")



class CreateDBScriptor(DBScriptor):
    """
    The CreateDBScriptor class implements the script to create the database and all of its tables.
    It inherits from DBScriptor.
    """
    
    _name = "Create Database Scriptor"
    
    def execute_script(self):
        for table, query in create_table_queries:
            self._db.run_query(query)
            if self._logs:
                self._db_manager.log_update(DBTableLogEntry, table, "created")
        if self._logs:
            self.log_result()
    
    def log_result(self):
        tables = self._db.run_query("SELECT * FROM sqlite_master WHERE type = 'table';", fetch="all")
        db_query_log_entry = DBCreatedLogEntry(self._logs, tables)
        db_query_log_entry.add_log_entry("database")



class PopulateTypesDBScriptor(DBScriptor):
    """
    The PopulateTypesDBScriptor class implements the script to populate the type tables in the database.
    It inherits from DBScriptor.  It gets its values from the DataManager class.
    """
    
    _name = "Populate Types Database Scriptor"
    
    def __init__(self, db_manager, log_manager, data_obj):
        super().__init__(db_manager, log_manager)
        self._data = data_obj
    
    def execute_script(self):
        levels_of_difficulty = self._data.get_type_list("levels")
        hint_types = self._data.get_type_list("hints")
        outcomes = self._data.get_type_list("outcomes")
        error_types = self._data.get_type_list("errors")
        
        type_tables = [("level_of_difficulty", levels_of_difficulty), ("outcome", outcomes)]
        
        for table_name, values_list in type_tables:
            for index, value in values_list:
                query = f"INSERT INTO {table_name}_type VALUES (:id, :code, :description);"
                parameters = {"id": index, "code": value, "description": value}
                self._db.run_query(query, parameters)
            if self._logs:
                self._db_manager.log_update(DBTableLogEntry, table_name, "populated")
                self.log_result(f"SELECT * FROM {table_name}_type;", f"{table_name.replace('_', ' ').title()} Types")
        
        for index, value, description in hint_types:
            query = f"INSERT INTO hint_type VALUES (:id, :code, :description);"
            parameters = {"id": index, "code": value, "description": description}
            self._db.run_query(query, parameters)
        if self._logs:
            self._db_manager.log_update(DBTableLogEntry, "hint", "populated")
            self.log_result("SELECT * FROM hint_type;", "Hint Types")
        
        for index, category, value in error_types:
            query = "INSERT INTO error_type VALUES (:id, :category, :code, :description);"
            parameters = {"id": index, "category": category, "code": value, "description": value}
            self._db.run_query(query, parameters)
        if self._logs:
            self._db_manager.log_update(DBTableLogEntry, "error_type", "populated")
            self.log_result("SELECT * FROM error_type;", "Error Types")



class PopulateHintsDBScriptor(DBScriptor):
    """
    The PopulateHintsDBScriptor class implements the script to populate the hint table in the database
    with a set of hints for the numbers 1 up to the value of the _hints_stored attribute.  This improves
    the app's performance by not requiring it to generate hints every game for the most common numbers.
    It inherits from DBScriptor.
    """
    
    _name = "Populate Hints Database Scriptor"
    _hints_stored = 100
    
    def __init__(self, db_manager, log_manager, data_obj, numbers):
        super().__init__(db_manager, log_manager)
        self._data = data_obj
        self._numbers = numbers
    
    def execute_script(self):
        self._populate_hints()
        if self._logs:
            self._db_manager.log_update(HintsPopulatedLogEntry, PopulateHintsDBScriptor._hints_stored)
            self.log_result("SELECT * FROM hint WHERE number IN (1,2,3,4,5) ORDER BY number;", "Hints")
    
    def _populate_hints(self):
        for i in range(1, PopulateHintsDBScriptor._hints_stored + 1):
            concept_manager = ConceptManager(i, self._numbers, self._db, self._data)
            hints = concept_manager.generate_hints(check_db=False, filter_results=False)
            for hint in hints:
                hint_obj = self._data.get_hint_obj_from_hint(hint)
                hint_type_id = hint_obj.get_id()
                populate_hints_query = "INSERT INTO hint(hint_type_id, number, hint) VALUES (:hint_type_id, :number, :hint);"
                parameters = {'hint_type_id': int(hint_type_id), 'number': int(i), 'hint': hint}
                self._db.run_query(populate_hints_query, parameters)



class DBManager:
    """
    The DBManager class manages the database.  It determines which connector to use and instantiates that object, which it
    then uses to instantiate each DBScriptor subclass and execute their scripts to create and load the database.
    """
    
    def __init__(self, numbers, data_obj, logs=None):
        self._logs = logs
        
        if os.path.exists(PostgreSqlDBConnector._db_name):
            self._db = self._get_db_connector(PostgreSqlDBConnector)
        else:
            self._db = self._get_db_connector(SqliteDBConnector)
        
        self._numbers = numbers
        self._data = data_obj
        
        self._create_db = CreateDBScriptor(self, self._logs)
        self._populate_db = PopulateTypesDBScriptor(self, self._logs, self._data)
        self._populate_hints = PopulateHintsDBScriptor(self, self._logs, self._data, self._numbers)
        
        if not os.path.exists(self._db._db_name):
            self._build_db()
    
    def get_database(self):
        return self._db
    
    def _get_db_connector(self, connector_class):
        db_connector = connector_class()
        if self._logs:
            self.log_update(DBConnectorLogEntry, connector_class._name)
        return db_connector
    
    def _build_db(self):
        for scriptor in [self._create_db, self._populate_db, self._populate_hints]:
            scriptor.execute_script()
            if self._logs:
                self.log_update(DBScriptorLogEntry, scriptor._name)
    
    def log_update(self, log_entry_class, *args):
        log_entry = log_entry_class(self._logs, *args)
        log_entry.add_log_entry("database")
    
    def log_query_result(self, query, result_name):
        self._populate_hints.log_result(query, result_name)