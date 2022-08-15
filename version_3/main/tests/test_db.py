import pytest
import os, subprocess as sp
from main.tests.tests_setup import objects_fake_global_dict
from main.app_data.db import *



### Object Manager Setup

objects_fake_global_easy = objects_fake_global_dict["easy"]
numbers = objects_fake_global_easy.get_object("numbers")
data = objects_fake_global_easy.get_object("data")



### SqliteDBConnector Tests

@pytest.fixture
def test_db_path():
    return "tests/sqlite_guess_that_number.db"

@pytest.fixture
def sqlite_db_fake():
    existing_db = sp.getoutput("IF EXIST tests/sqlite_guess_that_number.db ECHO 1")
    if existing_db:
        os.system('cmd /c "del tests/sqlite_guess_that_number.db"')
    db = SqliteDBConnector()
    return db


# Test run_query method
@pytest.fixture
def test_query():
    query = """
            SELECT one AS number FROM new
            UNION
            SELECT two AS number FROM new
            UNION
            SELECT three AS number FROM new
            ;
            """
    return query


def test_db(sqlite_db_fake):
    assert True == isinstance(sqlite_db_fake, SqliteDBConnector)

def test_run_query_correct_db_location(sqlite_db_fake, test_db_path):
    tests_dir = os.path.dirname(os.path.abspath("tests"))
    db_path_test = os.path.join(tests_dir, test_db_path)
    main_dir = os.path.dirname(os.path.abspath("guess_that_number.py"))
    db_path_main = os.path.join(main_dir, test_db_path)
    assert db_path_test == db_path_main

def test_run_query_simple(sqlite_db_fake, test_db_path):
    assert [(1, 2, 3)] == sqlite_db_fake.run_query("SELECT 1, 2, 3;", fetch="all", _db_path=test_db_path)

def test_run_query_multiline_fetch_all(sqlite_db_fake, test_db_path, test_query):
    sqlite_db_fake.run_query("DROP TABLE IF EXISTS new;", _db_path=test_db_path)
    sqlite_db_fake.run_query("CREATE TABLE IF NOT EXISTS new AS SELECT 1 one, 2 two, 3 three;", _db_path=test_db_path)
    assert [(1,), (2,), (3,)] == sqlite_db_fake.run_query(test_query, fetch="all", _db_path=test_db_path)

def test_run_query_multiline_fetch_one(sqlite_db_fake, test_db_path, test_query):
    sqlite_db_fake.run_query("DROP TABLE IF EXISTS new;", _db_path=test_db_path)
    sqlite_db_fake.run_query("CREATE TABLE IF NOT EXISTS new AS SELECT 1 one, 2 two, 3 three;", _db_path=test_db_path)
    assert (1,) == sqlite_db_fake.run_query(test_query, fetch="one", _db_path=test_db_path)

def test_run_query_multiline_fetch_none(sqlite_db_fake, test_db_path, test_query):
    sqlite_db_fake.run_query("DROP TABLE IF EXISTS new;", _db_path=test_db_path)
    sqlite_db_fake.run_query("CREATE TABLE IF NOT EXISTS new AS SELECT 1 one, 2 two, 3 three;", _db_path=test_db_path)
    assert None == sqlite_db_fake.run_query(test_query, fetch=None, _db_path=test_db_path)

@pytest.fixture
def create_parameter_table_query():
    query = """
            CREATE TABLE IF NOT EXISTS params AS
            SELECT 1 AS id, 'one' AS name
            UNION
            SELECT 2 AS id, 'two' AS name
            UNION
            SELECT 3 AS id, 'three' AS name
            ;
            """
    return query

def test_run_query_parameters(sqlite_db_fake, test_db_path, create_parameter_table_query):
    sqlite_db_fake.run_query("DROP TABLE IF EXISTS params;", _db_path=test_db_path)
    sqlite_db_fake.run_query(create_parameter_table_query, _db_path=test_db_path)
    insert_query = "INSERT INTO params(id, name) VALUES(:id, :name);"
    parameters = {"id": 4, "name": "four"}
    sqlite_db_fake.run_query(insert_query, parameters=parameters, _db_path=test_db_path)
    assert ("four",) == sqlite_db_fake.run_query("SELECT name FROM params WHERE id = 4;", fetch="one", _db_path=test_db_path)

def test_run_query_include_cols(sqlite_db_fake, test_db_path, create_parameter_table_query):
    sqlite_db_fake.run_query("DROP TABLE IF EXISTS params;", _db_path=test_db_path)
    sqlite_db_fake.run_query(create_parameter_table_query, _db_path=test_db_path)
    result = sqlite_db_fake.run_query("SELECT name FROM params WHERE id = 3", fetch="all", include_cols=True, _db_path=test_db_path)
    assert ([("three",)], ("name",)) == result

def test_run_query_no_arguments_raises_error(sqlite_db_fake):
    with pytest.raises(TypeError):
        sqlite_db_fake.run_query()

def test_run_query_too_many_arguments_raises_error(sqlite_db_fake, test_db_path):
    with pytest.raises(TypeError):
        sqlite_db_fake.run_query("SELECT 1;", parameters=None, fetch=None, include_cols=False, _db_path=test_db_path, extra="no")



### DBManager Tests

@pytest.fixture
def db_manager_fake():
    return DBManager(numbers, data)


# Test get_database method
def test_get_database(db_manager_fake):
    db = db_manager_fake.get_database()
    assert True == isinstance(db, DBConnector)

def test_get_database_too_many_arguments_raises_error(db_manager_fake):
    with pytest.raises(TypeError):
        db_manager_fake.get_database("extra")



### Test database build

db_tables = [row[0] for row in create_table_queries]


# Create DB
def test_database_build_table_list(sqlite_db_fake, test_db_path):
    for table in db_tables + ["new", "params"]:
        sqlite_db_fake.run_query(f"DROP TABLE IF EXISTS {table};", _db_path=test_db_path)
    for table, query in create_table_queries:
        sqlite_db_fake.run_query(query, _db_path=test_db_path)
    query = "SELECT * FROM sqlite_master WHERE type = 'table';"
    result = sqlite_db_fake.run_query(query, fetch="all", _db_path=test_db_path)
    tables = [row[1] for row in result]
    assert db_tables == tables


# Populate Types
db_error_types = [(1, 'range_entry', 'comparison', 'comparison'),
               (2, 'range_entry', 'missing', 'missing'),
               (3, 'range_entry', 'invalid', 'invalid'),
               (4, 'guess_entry', 'non_integer', 'non_integer'),
               (5, 'guess_entry', 'out_of_range', 'out_of_range')]

db_hint_types = [(1, 'factor', 'Factor: Any integer which divides evenly into a given integer. For example, 8 is a factor of 24.\nDivisible: When dividing by a certain number gives a whole number answer.'),
                 (2, 'multiple', 'Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction).'),
                 (3, 'prime', 'Prime: A positive integer which has only 1 and the number itself as factors. For example, 2, 3, 5, 7, 11, 13, etc. are all primes. By convention, the number 1 is not prime.'),
                 (4, 'even_odd', 'Even: An integer that is a multiple of 2. The even numbers are { . . . , –4, –2, 0, 2, 4, 6, . . . }.\nOdd: An integer that is not a multiple of 2. The odd numbers are { . . . , –3, –1, 1, 3, 5, . . . }.'),
                 (5, 'perfect_square', 'Perfect Square: Any number that is the square of a rational number. For example, 0, 1, 4, 9, 16, 25, etc. are all perfect squares. So are and .'),
                 (6, 'perfect_cube', 'perfect_cube'),
                 (7, 'digit_sum', 'Digit: Any of the symbols 0, 1, 2, 3, 4, 5, 6, 7, 8, and 9 used to write numbers. For example, the digits in the number 361 are 3, 6, and 1.\nSum: The result of adding a set of numbers or algebraic expressions.'),
                 (8, 'digit_length', 'Digit: Any of the symbols 0, 1, 2, 3, 4, 5, 6, 7, 8, and 9 used to write numbers. For example, the digits in the number 361 are 3, 6, and 1.'),
                 (9, 'greater_less', 'greater_less')]

db_level_of_difficulty_types = [(1, 'easy', 'easy'),
                                (2, 'medium', 'medium'),
                                (3, 'hard', 'hard'),
                                (4, 'custom', 'custom')]

db_outcome_types = [(1, 'win', 'win'),
                    (2, 'lose', 'lose'),
                    (3, 'quit', 'quit')]


def test_database_build_types_errors(sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query(f"DELETE FROM error_type;", _db_path=test_db_path)
    error_types = data.get_type_list("errors")
    
    for index, category, value in error_types:
        query = "INSERT INTO error_type VALUES (:id, :category, :code, :description);"
        parameters = {"id": index, "category": category, "code": value, "description": value}
        sqlite_db_fake.run_query(query, parameters, _db_path=test_db_path)
    
    check_query = "SELECT * FROM error_type;"
    result = sqlite_db_fake.run_query(check_query, fetch="all", _db_path=test_db_path)
    assert db_error_types == result

def test_database_build_types_hints(sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query(f"DELETE FROM hint_type;", _db_path=test_db_path)
    hint_types = data.get_type_list("hints")
    
    for index, value, description in hint_types:
        query = f"INSERT INTO hint_type VALUES (:id, :code, :description);"
        parameters = {"id": index, "code": value, "description": description}
        sqlite_db_fake.run_query(query, parameters, _db_path=test_db_path)
    
    check_query = "SELECT * FROM hint_type;"
    result = sqlite_db_fake.run_query(check_query, fetch="all", _db_path=test_db_path)
    assert db_hint_types == result

def test_database_build_types_levels_outcomes(sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query(f"DELETE FROM level_of_difficulty_type;", _db_path=test_db_path)
    sqlite_db_fake.run_query(f"DELETE FROM outcome_type;", _db_path=test_db_path)
    levels_of_difficulty = data.get_type_list("levels")
    outcomes = data.get_type_list("outcomes")
    
    type_tables = [("level_of_difficulty", levels_of_difficulty), ("outcome", outcomes)]
    
    for table_name, values_list in type_tables:
        for index, value in values_list:
            query = f"INSERT INTO {table_name}_type VALUES (:id, :code, :description);"
            parameters = {"id": index, "code": value, "description": value}
            sqlite_db_fake.run_query(query, parameters, _db_path=test_db_path)
    
    levels_check_query = "SELECT * FROM level_of_difficulty_type;"
    levels_result = sqlite_db_fake.run_query(levels_check_query, fetch="all", _db_path=test_db_path)
    outcomes_check_query = "SELECT * FROM outcome_type;"
    outcomes_result = sqlite_db_fake.run_query(outcomes_check_query, fetch="all", _db_path=test_db_path)
    assert db_level_of_difficulty_types + db_outcome_types == levels_result + outcomes_result


# Populate Hints
hint_check = [(1, 1, 1, 'Nice try!  Hint: It has 1 factor(s).'),
              (2, 4, 1, 'Nice try!  Hint: It is an odd number.'),
              (3, 5, 1, 'Nice try!  Hint: It is a perfect square.'),
              (4, 6, 1, 'Nice try!  Hint: It is a perfect cube.'),
              (5, 2, 2, 'Nice try!  Hint: 2 is a multiple.'),
              (6, 2, 2, 'Nice try!  Hint: 4 is a multiple.'),
              (7, 2, 2, 'Nice try!  Hint: 6 is a multiple.'),
              (8, 2, 2, 'Nice try!  Hint: 8 is a multiple.'),
              (9, 2, 2, 'Nice try!  Hint: 10 is a multiple.'),
              (10, 3, 2, 'Nice try!  Hint: It is a prime number.'),
              (11, 4, 2, 'Nice try!  Hint: It is an even number.'),
              (12, 2, 3, 'Nice try!  Hint: 3 is a multiple.'),
              (13, 2, 3, 'Nice try!  Hint: 6 is a multiple.'),
              (14, 2, 3, 'Nice try!  Hint: 9 is a multiple.'),
              (15, 2, 3, 'Nice try!  Hint: 12 is a multiple.'),
              (16, 2, 3, 'Nice try!  Hint: 15 is a multiple.'),
              (17, 3, 3, 'Nice try!  Hint: It is a prime number.'),
              (18, 4, 3, 'Nice try!  Hint: It is an odd number.'),
              (19, 1, 4, 'Nice try!  Hint: It is divisible by 2.'),
              (20, 1, 4, 'Nice try!  Hint: It has 3 factor(s).'),
              (21, 2, 4, 'Nice try!  Hint: 4 is a multiple.'),
              (22, 2, 4, 'Nice try!  Hint: 8 is a multiple.'),
              (23, 2, 4, 'Nice try!  Hint: 12 is a multiple.'),
              (24, 2, 4, 'Nice try!  Hint: 16 is a multiple.'),
              (25, 2, 4, 'Nice try!  Hint: 20 is a multiple.'),
              (26, 3, 4, 'Nice try!  Hint: It has 1 prime factor(s).'),
              (27, 4, 4, 'Nice try!  Hint: It is an even number.'),
              (28, 5, 4, 'Nice try!  Hint: It is a perfect square.'),
              (29, 2, 5, 'Nice try!  Hint: 5 is a multiple.'),
              (30, 2, 5, 'Nice try!  Hint: 10 is a multiple.'),
              (31, 2, 5, 'Nice try!  Hint: 15 is a multiple.'),
              (32, 2, 5, 'Nice try!  Hint: 20 is a multiple.'),
              (33, 2, 5, 'Nice try!  Hint: 25 is a multiple.'),
              (34, 3, 5, 'Nice try!  Hint: It is a prime number.'),
              (35, 4, 5, 'Nice try!  Hint: It is an odd number.')]

def test_database_build_hints(sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query(f"DELETE FROM hint;", _db_path=test_db_path)
    for i in range(1, 6):
        concept_manager = ConceptManager(i, numbers, None, data)
        hints = concept_manager.generate_hints(check_db=False, filter_results=False)
        for hint in hints:
            hint_obj = data.get_hint_obj_from_hint(hint)
            hint_type_id = hint_obj.get_id()
            populate_hints_query = "INSERT INTO hint(hint_type_id, number, hint) VALUES (:hint_type_id, :number, :hint);"
            parameters = {'hint_type_id': int(hint_type_id), 'number': int(i), 'hint': hint}
            sqlite_db_fake.run_query(populate_hints_query, parameters, _db_path=test_db_path)
    
    query = "SELECT * FROM hint;"
    result = sqlite_db_fake.run_query(query, fetch="all", _db_path=test_db_path)
    assert hint_check == result


