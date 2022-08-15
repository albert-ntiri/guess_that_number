import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.app_data.data_storers.data_storer_components import *
from main.app_data.data_storers.game_data_storers import *
from main.app_data.data_storers.guess_data_storers import *
from main.app_data.data_storers.outcome_data_storers import *



### Object Manager Setup

objects_fake_global_easy = objects_fake_global_dict["easy"]
settings = objects_fake_global_easy.get_object("settings")


@pytest.fixture
def session_fake(sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM session;", _db_path=test_db_path)
    session = objects_fake_global_easy.get_object("session")
    return session



### DataStorer Tests

@pytest.fixture
def data_storer_fake(session_fake):
    return DataStorer(session_fake)


# Test get_parameters method
def test_get_parameters(data_storer_fake):
    assert {"session_id": 1} == data_storer_fake.get_parameters()

def test_get_parameters_too_many_arguments_raises_error(data_storer_fake):
    with pytest.raises(TypeError):
        data_storer_fake.get_parameters("extra")



### ErrorStorer Tests

class ErrorStorerFake(DataStorer, ErrorStorer):
    def __init__(self, session):
        super().__init__(session)
    

@pytest.fixture
def error_storer_fake(session_fake):
    return ErrorStorerFake(session_fake)


# Test add_error_info method
@pytest.mark.parametrize("parameters, error_type, error_type_id",
                         [({"session_id": 1}, "comparison", 1),
                          ({"session_id": 1}, "missing", 2),
                          ({"session_id": 1}, "invalid", 3),
                          ({"session_id": 1}, "non_integer", 4),
                          ({"session_id": 1}, "out_of_range", 5)
                          ])
def test_add_error_info(error_storer_fake, parameters, error_type, error_type_id):
    expected_parameters = {"session_id": 1, "error": 1, "error_type_id": error_type_id}
    actual_parameters = error_storer_fake.add_error_info(parameters, error_type)
    assert expected_parameters == actual_parameters

def test_add_error_info_no_arguments_raises_error(error_storer_fake):
    with pytest.raises(TypeError):
        error_storer_fake.add_error_info()

def test_add_error_info_too_many_arguments_raises_error(error_storer_fake):
    with pytest.raises(TypeError):
        error_storer_fake.add_error_info({"session_id": 1}, "comparison", "extra")



### StorageManager Tests

class DataStorerChildStub(DataStorer):
    def __init__(self, session):
        super().__init__(session)
    
    def update_db_table(self):
        return 3

class StorageManagerFake(StorageManager):
    def _process_update(self, db_update_obj):
        return db_update_obj.update_db_table()


@pytest.fixture
def db_update_object(session_fake):
    return DataStorerChildStub(session_fake)

@pytest.fixture
def storage_manager_fake(session_fake):
    return StorageManagerFake(session_fake, objects_fake_global_easy)


# Test _process_update method
def test_process_update(storage_manager_fake, db_update_object):
    assert 3 == storage_manager_fake._process_update(db_update_object)



### GameEntry Tests

@pytest.fixture
def game_entry_copy(session_fake):
    game_entry = GameEntry(session_fake, settings)
    yield game_entry
    game_entry._parameters.clear()


# Test _set_parameters method
@pytest.mark.parametrize("parameter, value",
                         [("level_of_difficulty_type_id", 1),
                          ("range_low", 1),
                          ("range_high", 10),
                          ("error", 0)
                          ])
def test_set_parameters_game_entry(game_entry_copy, parameter, value):
    game_entry_copy._set_parameters()
    assert value == game_entry_copy._parameters[parameter]

def test_set_parameters_game_entry_winning_number(game_entry_copy):
    game_entry_copy._set_parameters()
    assert game_entry_copy._parameters["winning_number"] in range(1, 11)

def test_set_parameters_game_entry_length(game_entry_copy):
    game_entry_copy._set_parameters()
    assert 6 == len(game_entry_copy._parameters)

def test_set_parameters_game_entry_too_many_arguments_raises_error(game_entry_copy):
    with pytest.raises(TypeError):
        game_entry_copy._set_parameters("extra")


# Test update_db_table method
def test_update_db_table_game_entry(game_entry_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    game_entry_copy.update_db_table()
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, '1', '10', 0)] == db_entry

def test_update_db_table_game_entry_too_many_arguments_raises_error(game_entry_copy):
    with pytest.raises(TypeError):
        game_entry_copy.update_db_table("extra")



### GameErrorEntry Tests

@pytest.fixture
def game_error_entry_copy(session_fake):
    game_error_entry = GameErrorEntry(session_fake, "invalid")
    yield game_error_entry
    game_error_entry._parameters.clear()


# Test update_db_table method
def test_update_db_table_game_error_entry(game_error_entry_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    game_error_entry_copy.update_db_table()
    game_table_query = "SELECT session_id, error, error_type_id FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3)] == db_entry

def test_update_db_table_game_error_entry_too_many_arguments_raises_error(game_error_entry_copy):
    with pytest.raises(TypeError):
        game_error_entry_copy.update_db_table("extra")



### GameStorageManager Tests

@pytest.fixture
def game_storage_manager_copy(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    return GameStorageManager(session_fake, objects_fake_global_easy)


# Test update_database method
def test_update_database_game_no_error(game_storage_manager_copy, sqlite_db_fake, test_db_path):
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    game_storage_manager_copy.update_database(db_update_params)
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, '1', '10', 0)] == db_entry

def test_update_database_game_error(game_storage_manager_copy, sqlite_db_fake, test_db_path):
    db_update_params = {"settings": None, "error": True, "error_type": "invalid"}
    game_storage_manager_copy.update_database(db_update_params)
    game_table_query = "SELECT session_id, error, error_type_id FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3)] == db_entry

def test_update_database_game_no_arguments_raises_error(game_storage_manager_copy):
    with pytest.raises(TypeError):
        game_storage_manager_copy.update_database()

def test_update_database_game_too_many_arguments_raises_error(game_storage_manager_copy):
    with pytest.raises(TypeError):
        game_storage_manager_copy.update_database({"settings": None, "error": True, "error_type": "invalid"}, "extra")



### GuessHintEntry Tests

prime_hint = "Nice try!  Hint: It is a prime number."

@pytest.fixture
def guess_hint_entry_copy(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    data = session_fake._objects.get_object("data")
    hints_obj = data.get_data_object("hint_types")
    guess_hint_entry = GuessHintEntry(session_fake, "6", "good", prime_hint, hints_obj)
    yield guess_hint_entry
    guess_hint_entry._parameters.clear()


# Test _set_parameters method
@pytest.mark.parametrize("parameter, value",
                         [("guess", "6"),
                          ("feedback", "good"),
                          ("error", 0),
                          ("hint_type_id", 3),
                          ("hint", prime_hint),
                          ("hint_number", 1)
                          ])
def test_set_parameters_guess_hint_entry(guess_hint_entry_copy, parameter, value):
    guess_hint_entry_copy._set_parameters()
    assert value == guess_hint_entry_copy._parameters[parameter]

def test_set_parameters_guess_hint_entry_length(guess_hint_entry_copy):
    guess_hint_entry_copy._set_parameters()
    assert 8 == len(guess_hint_entry_copy._parameters)

def test_set_parameters_guess_hint_entry_too_many_arguments_raises_error(guess_hint_entry_copy):
    with pytest.raises(TypeError):
        guess_hint_entry_copy._set_parameters("extra")


# Test update_db_table method
def test_update_db_table_guess_hint_entry(guess_hint_entry_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM guess;", _db_path=test_db_path)
    guess_hint_entry_copy.update_db_table()
    guess_table_query = "SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 1, "6", "good", 0)] == db_entry

def test_update_db_table_guess_hint_entry_too_many_arguments_raises_error(guess_hint_entry_copy):
    with pytest.raises(TypeError):
        guess_hint_entry_copy.update_db_table("extra")



### GuessNoHintEntry Tests

@pytest.fixture
def guess_no_hint_entry_copy(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    guess_no_hint_entry = GuessNoHintEntry(session_fake, "6", None)
    yield guess_no_hint_entry
    guess_no_hint_entry._parameters.clear()


# Test update_db_table method
def test_update_db_table_guess_no_hint_entry(guess_no_hint_entry_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM guess;", _db_path=test_db_path)
    guess_no_hint_entry_copy.update_db_table()
    guess_table_query = "SELECT game_id, session_id, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "6", None, 0)] == db_entry

def test_update_db_table_guess_no_hint_entry_too_many_arguments_raises_error(guess_no_hint_entry_copy):
    with pytest.raises(TypeError):
        guess_no_hint_entry_copy.update_db_table("extra")



### GuessErrorEntry Tests

@pytest.fixture
def guess_error_entry_copy(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    guess_error_entry = GuessErrorEntry(session_fake, "5.5", "non_integer")
    yield guess_error_entry
    guess_error_entry._parameters.clear()


# Test update_db_table method
def test_update_db_table_guess_error_entry(guess_error_entry_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM guess;", _db_path=test_db_path)
    guess_error_entry_copy.update_db_table()
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "5.5", 1, 4)] == db_entry

def test_update_db_table_guess_error_entry_too_many_arguments_raises_error(guess_error_entry_copy):
    with pytest.raises(TypeError):
        guess_error_entry_copy.update_db_table("extra")



### GuessStorageManager Tests

@pytest.fixture
def guess_storage_manager_copy(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    return GuessStorageManager(session_fake, objects_fake_global_easy)


# Test update_database method
def test_update_database_guess_hint(guess_storage_manager_copy, sqlite_db_fake, test_db_path):
    db_update_params = {"guess": "6", "hint": prime_hint, "feedback": "good", "error": False, "error_type": None}
    guess_storage_manager_copy.update_database(db_update_params)
    guess_table_query = "SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 1, "6", "good", 0)] == db_entry

def test_update_database_guess_no_hint(guess_storage_manager_copy, sqlite_db_fake, test_db_path):
    db_update_params = {"guess": "6", "hint": None, "feedback": None, "error": False, "error_type": None}
    guess_storage_manager_copy.update_database(db_update_params)
    guess_table_query = "SELECT game_id, session_id, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "6", None, 0)] == db_entry

def test_update_database_guess_error(guess_storage_manager_copy, sqlite_db_fake, test_db_path):
    db_update_params = {"guess": "5.5", "hint": "Please enter an integer.", "feedback": None, "error": True,
                        "error_type": "non_integer"}
    guess_storage_manager_copy.update_database(db_update_params)
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "5.5", 1, 4)] == db_entry

def test_update_database_guess_no_arguments_raises_error(guess_storage_manager_copy):
    with pytest.raises(TypeError):
        guess_storage_manager_copy.update_database()

def test_update_database_guess_too_many_arguments_raises_error(guess_storage_manager_copy):
    with pytest.raises(TypeError):
        guess_storage_manager_copy.update_database({"settings": None, "error": True, "error_type": "invalid"}, "extra")



### OutcomeEntry Tests

@pytest.fixture
def outcome_entry_copy_score(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "win")
    outcome_obj.score = 80
    outcome_entry = OutcomeEntry(session_fake, outcome_obj)
    yield outcome_entry
    outcome_entry._parameters.clear()

@pytest.fixture
def outcome_entry_copy_no_score(session_fake, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    outcome_entry = OutcomeEntry(session_fake, outcome_obj)
    yield outcome_entry
    outcome_entry._parameters.clear()


# Test _set_parameters method
@pytest.mark.parametrize("parameter, value",
                         [("outcome_type_id", 1),
                          ("play_again", 0),
                          ("score", 80)
                          ])
def test_set_parameters_outcome_entry_score(outcome_entry_copy_score, parameter, value):
    outcome_entry_copy_score._set_parameters()
    assert value == outcome_entry_copy_score._parameters[parameter]

@pytest.mark.parametrize("parameter, value",
                         [("outcome_type_id", 2),
                          ("play_again", 0)
                          ])
def test_set_parameters_outcome_entry_no_score(outcome_entry_copy_no_score, parameter, value):
    outcome_entry_copy_no_score._set_parameters()
    assert value == outcome_entry_copy_no_score._parameters[parameter]

def test_set_parameters_outcome_entry_too_many_arguments_raises_error(outcome_entry_copy_score):
    with pytest.raises(TypeError):
        outcome_entry_copy_score._set_parameters("extra")


# Test update_db_table method
def test_update_db_table_outcome_entry_score(outcome_entry_copy_score, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM outcome;", _db_path=test_db_path)
    outcome_entry_copy_score.update_db_table()
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 80, 0)] == db_entry

def test_update_db_table_outcome_entry_no_score(outcome_entry_copy_no_score, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM outcome;", _db_path=test_db_path)
    outcome_entry_copy_no_score.update_db_table()
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, None, 0)] == db_entry

def test_update_db_table_outcome_entry_too_many_arguments_raises_error(outcome_entry_copy_score):
    with pytest.raises(TypeError):
        outcome_entry_copy_score.update_db_table("extra")



### PlayAgainUpdate Tests

@pytest.fixture
def play_again_update_copy(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    outcome_query = "INSERT INTO outcome(game_id, session_id, outcome_type_id, play_again) VALUES (1, 1, 2, 0);"
    sqlite_db_fake.run_query(outcome_query, _db_path=test_db_path)
    play_again_update = PlayAgainUpdate(session_fake)
    yield play_again_update
    play_again_update._parameters.clear()


# Test update_db_table method
def test_update_db_table_play_again_update(play_again_update_copy, sqlite_db_fake, test_db_path):
    play_again_update_copy.update_db_table()
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, play_again FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, 1)] == db_entry

def test_update_db_table_play_again_update_too_many_arguments_raises_error(play_again_update_copy):
    with pytest.raises(TypeError):
        play_again_update_copy.update_db_table("extra")



### FeedbackUpdate Tests

@pytest.fixture
def feedback_update_copy_improvement(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session_fake.update_database("game", {"settings": settings, "error": False, "error_type": None})
    data = session_fake._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    outcome_query = "INSERT INTO outcome(game_id, session_id, outcome_type_id, play_again) VALUES (1, 1, 2, 0);"
    sqlite_db_fake.run_query(outcome_query, _db_path=test_db_path)
    feedback_update = FeedbackUpdate(session_fake, feedback_type="improvement", improvement_area_id=2)
    yield feedback_update
    feedback_update._parameters.clear()


# Test _set_parameters method
def test_set_parameters_improvement(feedback_update_copy_improvement):
    assert ("improvement_area_id", 2) == feedback_update_copy_improvement._set_parameters()

def test_set_parameters_feedback_update_too_many_arguments_raises_error(feedback_update_copy_improvement):
    with pytest.raises(TypeError):
        feedback_update_copy_improvement._set_parameters("extra")


# Test update_db_table method
def test_update_db_table_feedback_update_improvement(feedback_update_copy_improvement, sqlite_db_fake, test_db_path):
    feedback_update_copy_improvement.update_db_table()
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_update_db_table_feedback_update_too_many_arguments_raises_error(feedback_update_copy_improvement):
    with pytest.raises(TypeError):
        feedback_update_copy_improvement.update_db_table("extra")



### OutcomeStorageManager Tests

@pytest.fixture
def outcome_storage_manager_copy(session_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    return OutcomeStorageManager(session_fake, objects_fake_global_easy)


# Test _add_outcome_record_to_db method
def test_add_outcome_record_to_db_score(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "win")
    outcome_obj.score = 80
    db_update_params = {"outcome_obj": outcome_obj}
    outcome_storage_manager_copy._add_outcome_record_to_db(db_update_params)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 80, 0)] == db_entry

def test_add_outcome_record_to_db_no_score(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params = {"outcome_obj": outcome_obj}
    outcome_storage_manager_copy._add_outcome_record_to_db(db_update_params)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, None, 0)] == db_entry

def test_add_outcome_record_to_db_outcome_no_arguments_raises_error(outcome_storage_manager_copy):
    with pytest.raises(TypeError):
        outcome_storage_manager_copy._add_outcome_record_to_db()

def test_add_outcome_record_to_db_outcome_too_many_arguments_raises_error(outcome_storage_manager_copy):
    with pytest.raises(TypeError):
        outcome_storage_manager_copy._add_outcome_record_to_db({"outcome_obj": None}, "extra")


# Test _update_outcome_record_in_db method
def test_update_outcome_record_in_db_play_again(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params_new = {"outcome_obj": outcome_obj}
    outcome_storage_manager_copy._add_outcome_record_to_db(db_update_params_new)
    db_update_params_update = {"update_type": "play_again"}
    outcome_storage_manager_copy._update_outcome_record_in_db(db_update_params_update)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, play_again FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, 1)] == db_entry

def test_update_outcome_record_in_db_feedback_improvement(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params_new = {"outcome_obj": outcome_obj}
    outcome_storage_manager_copy._add_outcome_record_to_db(db_update_params_new)
    db_update_params_update = {"update_type": "feedback", "feedback_type": "improvement", "improvement_area_id": 2,
                               "recommendation_type": None}
    outcome_storage_manager_copy._update_outcome_record_in_db(db_update_params_update)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_add_outcome_record_to_db_outcome_no_arguments_raises_error(outcome_storage_manager_copy):
    with pytest.raises(TypeError):
        outcome_storage_manager_copy._update_outcome_record_in_db()

def test_add_outcome_record_to_db_outcome_too_many_arguments_raises_error(outcome_storage_manager_copy):
    with pytest.raises(TypeError):
        outcome_storage_manager_copy._update_outcome_record_in_db({"update_type": "play_again"}, "extra")


# Test update_database method
def test_update_database_outcome_new_score(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "win")
    outcome_obj.score = 80
    db_update_params = {"entry_type": "New", "outcome_obj": outcome_obj}
    outcome_storage_manager_copy.update_database(db_update_params)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 80, 0)] == db_entry

def test_update_database_outcome_new_no_score(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params = {"entry_type": "New", "outcome_obj": outcome_obj}
    outcome_storage_manager_copy.update_database(db_update_params)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, None, 0)] == db_entry

def test_update_database_outcome_update_play_again(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params_new = {"entry_type": "New", "outcome_obj": outcome_obj}
    outcome_storage_manager_copy.update_database(db_update_params_new)
    db_update_params_update = {"entry_type": "Updated", "update_type": "play_again"}
    outcome_storage_manager_copy.update_database(db_update_params_update)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, play_again FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, 1)] == db_entry

def test_update_database_outcome_update_feedback_improvement(outcome_storage_manager_copy, sqlite_db_fake, test_db_path):
    data = outcome_storage_manager_copy._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params_new = {"entry_type": "New", "outcome_obj": outcome_obj}
    outcome_storage_manager_copy.update_database(db_update_params_new)
    db_update_params_update = {"entry_type": "Updated", "update_type": "feedback", "feedback_type": "improvement",
                               "improvement_area_id": 2, "recommendation_type": None}
    outcome_storage_manager_copy.update_database(db_update_params_update)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_update_database_outcome_no_arguments_raises_error(outcome_storage_manager_copy):
    with pytest.raises(TypeError):
        outcome_storage_manager_copy.update_database()

def test_update_database_outcome_too_many_arguments_raises_error(outcome_storage_manager_copy):
    with pytest.raises(TypeError):
        outcome_storage_manager_copy.update_database({"entry_type": "Updated", "update_type": "play_again"}, "extra")



