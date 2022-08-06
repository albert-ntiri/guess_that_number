import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.app_data.data_storers.session import *
from main.app_data.db import DBConnector
from resources.variables.create_db_queries import non_type_tables
from main.tests.test_data_storers import prime_hint



### Object Manager Setup

objects_fake_global = objects_fake_global_dict["easy"]
settings = objects_fake_global.get_object("settings")


@pytest.fixture
def session_fake(sqlite_db_fake, test_db_path):
    session = objects_fake_global.get_object("session")
    yield session
    for table in non_type_tables:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)



### Session Tests


# Test add_session_record_to_db method
def test_add_session_record_to_db(session_fake, sqlite_db_fake, test_db_path):
    session_count = sqlite_db_fake.run_query("SELECT COUNT(*) FROM session;", fetch="one", _db_path=test_db_path)[0]
    session_fake.add_session_record_to_db()
    assert session_count + 1 == sqlite_db_fake.run_query("SELECT COUNT(*) FROM session;", fetch="one", _db_path=test_db_path)[0]

def test_add_session_record_to_db_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.add_session_record_to_db("extra")


# Test _get_session_id method
def test_get_session_id(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM session;", _db_path=test_db_path)
    session_fake.add_session_record_to_db()
    assert 1 == session_fake._get_session_id()

def test_get_session_id_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake._get_session_id("extra")


# Test get_database method
def test_get_database(session_fake):
    db = session_fake.get_database()
    assert True == isinstance(db, DBConnector)

def test_get_database_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.get_database("extra")


# Test _get_game_id method
def test_get_game_id_correct_value(session_fake, sqlite_db_fake, test_db_path):
    insert_query = f"""INSERT INTO game(session_id, error) VALUES(1, 0);"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    assert 1 == session_fake._get_game_id()

def test_get_game_id_added_to_list(session_fake, sqlite_db_fake, test_db_path):
    insert_query = f"""INSERT INTO game(session_id, error) VALUES(1, 0);"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    game_id = session_fake._get_game_id()
    assert game_id == session_fake._game_ids[-1]

def test_get_game_id_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake._get_game_id("extra")


# Test update_database method
def test_update_database_game_no_error(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", db_update_params)
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, '1', '10', 0)] == db_entry

def test_update_database_game_error(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    db_update_params = {"settings": None, "error": True, "error_type": "invalid"}
    session_fake.update_database("game", db_update_params)
    game_table_query = "SELECT session_id, error, error_type_id FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3)] == db_entry

def test_update_database_guess_hint(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", start_game_params)
    db_update_params = {"guess": "6", "hint": prime_hint, "feedback": "good", "error": False, "error_type": None}
    session_fake.update_database("guess", db_update_params)
    guess_table_query = "SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 1, "6", "good", 0)] == db_entry

def test_update_database_guess_no_hint(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", start_game_params)
    db_update_params = {"guess": "6", "hint": None, "feedback": None, "error": False, "error_type": None}
    session_fake.update_database("guess", db_update_params)
    guess_table_query = "SELECT game_id, session_id, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "6", None, 0)] == db_entry

def test_update_database_guess_error(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", start_game_params)
    db_update_params = {"guess": "5.5", "hint": "Please enter an integer.", "feedback": None, "error": True,
                        "error_type": "non_integer"}
    session_fake.update_database("guess", db_update_params)
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "5.5", 1, 4)] == db_entry

def test_update_database_outcome_new_score(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", start_game_params)
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "win")
    outcome_obj.score = 80
    db_update_params = {"entry_type": "New", "outcome_obj": outcome_obj}
    session_fake.update_database("outcome", db_update_params)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 80, 0)] == db_entry

def test_update_database_outcome_new_no_score(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", start_game_params)
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params = {"entry_type": "New", "outcome_obj": outcome_obj}
    session_fake.update_database("outcome", db_update_params)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, None, 0)] == db_entry

def test_update_database_outcome_update_play_again(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", start_game_params)
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params_new = {"entry_type": "New", "outcome_obj": outcome_obj}
    session_fake.update_database("outcome", db_update_params_new)
    db_update_params_update = {"entry_type": "Updated", "update_type": "play_again"}
    session_fake.update_database("outcome", db_update_params_update)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, play_again FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, 1)] == db_entry

def test_update_database_outcome_update_feedback_improvement(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    session_fake.update_database("game", start_game_params)
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params_new = {"entry_type": "New", "outcome_obj": outcome_obj}
    session_fake.update_database("outcome", db_update_params_new)
    db_update_params_update = {"entry_type": "Updated", "update_type": "feedback", "feedback_type": "improvement",
                               "improvement_area_id": 2, "recommendation_type": None}
    session_fake.update_database("outcome", db_update_params_update)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_update_database_no_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.update_database()

def test_update_database_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.update_database("game", {"error": True}, "extra")


# Test get_total_hints_given method
@pytest.mark.parametrize("n", [1, 2, 3])
def test_get_total_hints_given(session_fake, sqlite_db_fake, test_db_path, n):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    for i in range(n):
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint) VALUES(1, 1, 'hint {i}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    
    assert (n,) == session_fake.get_total_hints_given()

def test_get_total_hints_given_no_hints(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    insert_query = f"""INSERT INTO guess(game_id, session_id) VALUES(1, 1);"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    
    assert (0,) == session_fake.get_total_hints_given()

def test_get_total_hints_given_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.get_total_hints_given("extra")


# Test get_last_hint method
@pytest.mark.parametrize("n", [1, 2, 3])
def test_get_last_hint(session_fake, sqlite_db_fake, test_db_path, n):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    for i in range(n):
        multiple_value = (i + 1) * 2
        multiple_hint = f"Nice try!  Hint: {multiple_value} is a multiple."
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                           VALUES(1, 1, 2, '{multiple_hint}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    
    last_hint_multiple = 2 * n
    assert ("multiple", f"Nice try!  Hint: {last_hint_multiple} is a multiple.") == session_fake.get_last_hint()

def test_get_last_hint_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.get_last_hint("extra")


# Test build_query method
def test_build_query_no_optional_args(session_fake):
    expected_result = "SELECT session_id FROM session"
    assert expected_result == session_fake.build_query("session_id", "session")

def test_build_query_no_optional_args(session_fake):
    expected_result = "SELECT session_id FROM game WHERE game_id = 1"
    assert expected_result == session_fake.build_query("session_id", "game", filter_col="game_id", filter_val="1")

def test_build_query_no_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.build_query()

def test_build_query_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.build_query("session_id", "game", filter_col="game_id", filter_val=1, extra="no")


# Test get_session_count method
def test_get_session_count_zero(session_fake, sqlite_db_fake, test_db_path):
    assert 0 == session_fake.get_session_count()

def test_get_session_count_one(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("INSERT INTO session(time) VALUES (datetime('now', 'localtime'));", _db_path=test_db_path)
    assert 1 == session_fake.get_session_count()

def test_get_session_count_two(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("INSERT INTO session(time) VALUES (datetime('now', 'localtime'));", _db_path=test_db_path)
    sqlite_db_fake.run_query("INSERT INTO session(time) VALUES (datetime('now', 'localtime'));", _db_path=test_db_path)
    assert 2 == session_fake.get_session_count()

def test_get_session_count_too_many_arguments_raises_error(session_fake):
    with pytest.raises(TypeError):
        session_fake.get_session_count("extra")



