import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict, GameSettings, ObjectManagerFake
from main.game.guess import *
from main.tests.test_data_storers import prime_hint



### Guess Tests

@pytest.fixture
def guess_copy():
    guess = Guess(5, objects_fake_global_dict["easy"])
    guess._text_display.clear_all_variables()
    return guess

@pytest.fixture
def guess_copy_medium():
    guess = Guess("5.5", objects_fake_global_dict["medium"])
    guess._text_display.clear_all_variables()
    return guess

@pytest.fixture
def guess_copy_hard():
    guess = Guess(5, objects_fake_global_dict["hard"])
    guess._text_display.clear_all_variables()
    return guess


# Test get_guess method
def test_get_guess(guess_copy):
    assert 5 == guess_copy.get_guess()

def test_get_guess_too_many_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy.get_guess("extra")


# Test _update_status method
def test_update_status_initial(guess_copy):
    assert "" == guess_copy._text_display.get_text("status_text")

def test_update_status_easy(guess_copy):
    guess_copy._stats._guesses_remaining.value = guess_copy._stats._guesses_remaining._set_default_value()
    guess_copy._update_status()
    assert f"Guesses Remaining: 10" == guess_copy._text_display.get_text("status_text")

def test_update_status_medium(guess_copy_medium):
    guess_copy_medium._stats._guesses_remaining.value = guess_copy_medium._stats._guesses_remaining._set_default_value()
    guess_copy_medium._update_status()
    assert f"Guesses Remaining: 5" == guess_copy_medium._text_display.get_text("status_text")

def test_update_status_hard(guess_copy_hard):
    guess_copy_hard._stats._guesses_remaining.value = guess_copy_hard._stats._guesses_remaining._set_default_value()
    guess_copy_hard._update_status()
    assert f"Guesses Remaining: 4" == guess_copy_hard._text_display.get_text("status_text")

def test_update_status_too_many_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy._update_status("extra")


# Test _update_screen_text method
def test_update_screen_text_easy_status(guess_copy):
    guess_copy._stats._guesses_remaining.value = guess_copy._stats._guesses_remaining._set_default_value()
    guess_copy._update_screen_text("Hint Text")
    assert f"Guesses Remaining: 10" == guess_copy._text_display.get_text("status_text")

def test_update_screen_text_easy_hint(guess_copy):
    guess_copy._stats._guesses_remaining.value = guess_copy._stats._guesses_remaining._set_default_value()
    guess_copy._update_screen_text("Hint Text")
    assert "Hint Text" == guess_copy._text_display.get_text("hint_text")

def test_update_screen_text_no_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy._update_screen_text()

def test_update_screen_text_too_many_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy._update_screen_text("Hint Text", "extra")


# Test _update_db method
def test_update_db_hint(guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    guess_copy._session.update_database("game", db_update_params)
    guess_copy._update_db(prime_hint, feedback="good")
    guess_table_query = "SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 1, "5", "good", 0)] == db_entry

def test_update_db_error(guess_copy_medium, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = guess_copy_medium._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    guess_copy_medium._session.update_database("game", db_update_params)
    guess_copy_medium._update_db("Please enter an integer.", error=True, error_type="non_integer")
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "5.5", 1, 4)] == db_entry

def test_update_db_no_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy._update_db()

def test_update_db_too_many_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy._update_db("Message", feedback="good", error=False, error_type=None, extra="no")


# Test _update_game_state method
def test_update_game_state_hint_db(guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    guess_copy._session.update_database("game", db_update_params)
    guess_copy._update_game_state(prime_hint, feedback="good")
    guess_table_query = "SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 1, "5", "good", 0)] == db_entry

def test_update_game_state_hint_screen_text_status(guess_copy):
    guess_copy._stats._score.value = guess_copy._stats._score._set_default_value()
    guess_copy._stats._guesses_remaining.value = guess_copy._stats._guesses_remaining._set_default_value()
    guess_copy._update_game_state(prime_hint, feedback="good")
    assert f"Guesses Remaining: 9" == guess_copy._text_display.get_text("status_text")

def test_update_game_state_hint_screen_text_hint(guess_copy):
    guess_copy._update_game_state(prime_hint, feedback="good")
    assert prime_hint == guess_copy._text_display.get_text("hint_text")

def test_update_game_state_hint_stats_score(guess_copy):
    guess_copy._stats._score.value = guess_copy._stats._score._set_default_value()
    guess_copy._stats._guesses_remaining.value = guess_copy._stats._guesses_remaining._set_default_value()
    guess_copy._update_game_state(prime_hint, feedback="good")
    assert 90 == guess_copy._stats.get_value("score")

def test_update_game_state_hint_stats_guesses_remaining(guess_copy):
    guess_copy._stats._score.value = guess_copy._stats._score._set_default_value()
    guess_copy._stats._guesses_remaining.value = guess_copy._stats._guesses_remaining._set_default_value()
    guess_copy._update_game_state(prime_hint, feedback="good")
    assert 9 == guess_copy._stats.get_value("guesses remaining")

def test_update_game_state_error_db(guess_copy_medium, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = guess_copy_medium._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    guess_copy_medium._session.update_database("game", db_update_params)
    guess_copy_medium._update_game_state("Please enter an integer.", error=True, error_type="non_integer")
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "5.5", 1, 4)] == db_entry

def test_update_game_state_error_screen_text_status(guess_copy_medium):
    guess_copy_medium._stats._score.value = guess_copy_medium._stats._score._set_default_value()
    guess_copy_medium._stats._guesses_remaining.value = guess_copy_medium._stats._guesses_remaining._set_default_value()
    guess_copy_medium._update_game_state("Please enter an integer.", error=True, error_type="non_integer")
    assert f"Guesses Remaining: 4" == guess_copy_medium._text_display.get_text("status_text")

def test_update_game_state_error_screen_text_hint(guess_copy_medium):
    guess_copy_medium._update_game_state("Please enter an integer.", error=True, error_type="non_integer")
    assert "Please enter an integer." == guess_copy_medium._text_display.get_text("hint_text")

def test_update_game_state_error_stats_score(guess_copy_medium):
    guess_copy_medium._stats._score.value = guess_copy_medium._stats._score._set_default_value()
    guess_copy_medium._stats._guesses_remaining.value = guess_copy_medium._stats._guesses_remaining._set_default_value()
    guess_copy_medium._update_game_state("Please enter an integer.", error=True, error_type="non_integer")
    assert 80 == guess_copy_medium._stats.get_value("score")

def test_update_game_state_error_stats_guesses_remaining(guess_copy_medium):
    guess_copy_medium._stats._score.value = guess_copy_medium._stats._score._set_default_value()
    guess_copy_medium._stats._guesses_remaining.value = guess_copy_medium._stats._guesses_remaining._set_default_value()
    guess_copy_medium._update_game_state("Please enter an integer.", error=True, error_type="non_integer")
    assert 4 == guess_copy_medium._stats.get_value("guesses remaining")

def test_update_game_state_no_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy._update_db()

def test_update_game_state_too_many_arguments_raises_error(guess_copy):
    with pytest.raises(TypeError):
        guess_copy._update_db("Message", feedback="good", error=False, error_type=None, extra="no")



### InvalidGuess Tests

@pytest.fixture
def guess_manager_copy():
    return GuessManager(objects_fake_global_dict["easy"])

@pytest.fixture
def invalid_guess_copy_non_integer(guess_manager_copy):
    error_obj = guess_manager_copy._data.get_sub_data_object("errors", "non_integer")
    return InvalidGuess('5.5', objects_fake_global_dict["easy"], error_obj)

@pytest.fixture
def invalid_guess_copy_out_of_range(guess_manager_copy):
    error_obj = guess_manager_copy._data.get_sub_data_object("errors", "out_of_range")
    return InvalidGuess('15', objects_fake_global_dict["easy"], error_obj)


# Test process_guess method
def test_process_guess_invalid_non_integer_db(invalid_guess_copy_non_integer, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = invalid_guess_copy_non_integer._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    invalid_guess_copy_non_integer._session.update_database("game", db_update_params)
    invalid_guess_copy_non_integer.process_guess()
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "5.5", 1, 4)] == db_entry

def test_process_guess_invalid_non_integer_screen_text_status(invalid_guess_copy_non_integer):
    invalid_guess_copy_non_integer._stats._score.value = invalid_guess_copy_non_integer._stats._score._set_default_value()
    invalid_guess_copy_non_integer._stats._guesses_remaining.value = invalid_guess_copy_non_integer._stats._guesses_remaining._set_default_value()
    invalid_guess_copy_non_integer.process_guess()
    assert f"Guesses Remaining: 9" == invalid_guess_copy_non_integer._text_display.get_text("status_text")

def test_process_guess_invalid_non_integer_screen_text_hint(invalid_guess_copy_non_integer):
    invalid_guess_copy_non_integer.process_guess()
    assert "Please enter an integer." == invalid_guess_copy_non_integer._text_display.get_text("hint_text")

def test_process_guess_invalid_non_integer_stats_score(invalid_guess_copy_non_integer):
    invalid_guess_copy_non_integer._stats._score.value = invalid_guess_copy_non_integer._stats._score._set_default_value()
    invalid_guess_copy_non_integer._stats._guesses_remaining.value = invalid_guess_copy_non_integer._stats._guesses_remaining._set_default_value()
    invalid_guess_copy_non_integer.process_guess()
    assert 90 == invalid_guess_copy_non_integer._stats.get_value("score")

def test_process_guess_invalid_non_integer_stats_guesses_remaining(invalid_guess_copy_non_integer):
    invalid_guess_copy_non_integer._stats._score.value = invalid_guess_copy_non_integer._stats._score._set_default_value()
    invalid_guess_copy_non_integer._stats._guesses_remaining.value = invalid_guess_copy_non_integer._stats._guesses_remaining._set_default_value()
    invalid_guess_copy_non_integer.process_guess()
    assert 9 == invalid_guess_copy_non_integer._stats.get_value("guesses remaining")

def test_process_guess_invalid_out_of_range_db(invalid_guess_copy_out_of_range, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = invalid_guess_copy_out_of_range._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    invalid_guess_copy_out_of_range._session.update_database("game", db_update_params)
    invalid_guess_copy_out_of_range.process_guess()
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "15", 1, 5)] == db_entry

def test_process_guess_invalid_out_of_range_screen_text_status(invalid_guess_copy_out_of_range):
    invalid_guess_copy_out_of_range._stats._score.value = invalid_guess_copy_out_of_range._stats._score._set_default_value()
    invalid_guess_copy_out_of_range._stats._guesses_remaining.value = invalid_guess_copy_out_of_range._stats._guesses_remaining._set_default_value()
    invalid_guess_copy_out_of_range.process_guess()
    assert f"Guesses Remaining: 9" == invalid_guess_copy_out_of_range._text_display.get_text("status_text")

def test_process_guess_invalid_out_of_range_screen_text_hint(invalid_guess_copy_out_of_range):
    invalid_guess_copy_out_of_range.process_guess()
    assert "Your guess is out of range. Please try again." == invalid_guess_copy_out_of_range._text_display.get_text("hint_text")

def test_process_guess_invalid_out_of_range_stats_score(invalid_guess_copy_out_of_range):
    invalid_guess_copy_out_of_range._stats._score.value = invalid_guess_copy_out_of_range._stats._score._set_default_value()
    invalid_guess_copy_out_of_range._stats._guesses_remaining.value = invalid_guess_copy_out_of_range._stats._guesses_remaining._set_default_value()
    invalid_guess_copy_out_of_range.process_guess()
    assert 90 == invalid_guess_copy_out_of_range._stats.get_value("score")

def test_process_guess_invalid_out_of_range_stats_guesses_remaining(invalid_guess_copy_out_of_range):
    invalid_guess_copy_out_of_range._stats._score.value = invalid_guess_copy_out_of_range._stats._score._set_default_value()
    invalid_guess_copy_out_of_range._stats._guesses_remaining.value = invalid_guess_copy_out_of_range._stats._guesses_remaining._set_default_value()
    invalid_guess_copy_out_of_range.process_guess()
    assert 9 == invalid_guess_copy_out_of_range._stats.get_value("guesses remaining")

def test_process_guess_invalid_too_many_arguments_raises_error(invalid_guess_copy_non_integer):
    with pytest.raises(TypeError):
        invalid_guess_copy_non_integer.process_guess("extra")



### CorrectGuess Tests

@pytest.fixture
def correct_guess_copy(guess_manager_copy):
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    return CorrectGuess(int(winning_number), guess_manager_copy._objects)


# Test process_guess method
def test_process_guess_correct_db(correct_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = correct_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    correct_guess_copy._session.update_database("game", db_update_params)
    correct_guess_copy.process_guess()
    guess_table_query = "SELECT game_id, session_id, guess, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    winning_number = settings.get_setting("winning number")
    assert [(1, 1, str(winning_number), 0)] == db_entry

def test_process_guess_correct_return_value(correct_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = correct_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    correct_guess_copy._session.update_database("game", db_update_params)
    assert "win" == correct_guess_copy.process_guess()

def test_process_guess_correct_too_many_arguments_raises_error(correct_guess_copy):
    with pytest.raises(TypeError):
        correct_guess_copy.process_guess("extra")



### IncorrectGuess Tests

@pytest.fixture
def incorrect_guess_copy(guess_manager_copy):
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess = 3 if int(winning_number) != 3 else 5
    return IncorrectGuess(guess, guess_manager_copy._objects)

incorrect_guess_hints = [prime_hint]


# Test process_guess method
def test_process_guess_incorrect_no_more_guesses_db(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    incorrect_guess_copy._stats._guesses_remaining.value = 1
    
    incorrect_guess_copy.process_guess()
    
    guess_table_query = "SELECT game_id, session_id, guess, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    winning_number = settings.get_setting("winning number")
    guess = 3 if int(winning_number) != 3 else 5
    assert [(1, 1, str(guess), 0)] == db_entry

def test_process_guess_incorrect_no_more_guesses_return_value(incorrect_guess_copy):
    incorrect_guess_copy._stats._guesses_remaining.value = 1
    assert "lose" == incorrect_guess_copy.process_guess()

def test_process_guess_incorrect_no_more_hints_db(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = []
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    guess_table_query = """SELECT game_id, session_id, hint_type_id, hint_number, guess, feedback, error
                           FROM guess
                           ORDER BY guess_id DESC
                           LIMIT 1;"""
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    winning_number = settings.get_setting("winning number")
    guess = 3 if int(winning_number) != 3 else 5
    assert [(1, 1, 9, 2, str(guess), None, 0)] == db_entry

def test_process_guess_incorrect_no_more_hints_screen_text_status(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = []
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    assert f"Guesses Remaining: 1" == incorrect_guess_copy._text_display.get_text("status_text")

def test_process_guess_incorrect_no_more_hints_screen_text_hint(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = []
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    greater_less_hints = ["Nice try!  Higher.", "Nice try!  Lower."]
    assert incorrect_guess_copy._text_display.get_text("hint_text") in greater_less_hints

def test_process_guess_incorrect_no_more_hints_stats_score(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = []
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    assert 10 == incorrect_guess_copy._stats.get_value("score")

def test_process_guess_incorrect_no_more_hints_stats_guesses_remaining(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = []
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    assert 1 == incorrect_guess_copy._stats.get_value("guesses remaining")

def test_process_guess_incorrect_hints_remaining_db(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = incorrect_guess_hints.copy()
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    guess_table_query = """SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error
                           FROM guess
                           ORDER BY guess_id DESC
                           LIMIT 1;"""
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    winning_number = settings.get_setting("winning number")
    guess = 3 if int(winning_number) != 3 else 5
    assert [(1, 1, 3, prime_hint, 2, str(guess), "good", 0)] == db_entry

def test_process_guess_incorrect_hints_remaining_screen_text_status(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = incorrect_guess_hints.copy()
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    assert f"Guesses Remaining: 1" == incorrect_guess_copy._text_display.get_text("status_text")

def test_process_guess_incorrect_hints_remaining_screen_text_hint(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = incorrect_guess_hints.copy()
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    assert prime_hint == incorrect_guess_copy._text_display.get_text("hint_text")

def test_process_guess_incorrect_hints_remaining_stats_score(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = incorrect_guess_hints.copy()
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    assert 10 == incorrect_guess_copy._stats.get_value("score")

def test_process_guess_incorrect_hints_remaining_stats_guesses_remaining(incorrect_guess_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = incorrect_guess_copy._objects.get_object("settings")
    db_update_params = {"settings": settings, "error": False, "error_type": None}
    incorrect_guess_copy._session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    incorrect_guess_copy._stats._score.value = 20
    incorrect_guess_copy._stats._guesses_remaining.value = 2
    incorrect_guess_copy._hints._relevant_hints = []
    incorrect_guess_copy._hints._redundant_hints = incorrect_guess_hints.copy()
    incorrect_guess_copy._hints._hint_pool = incorrect_guess_copy._hints._relevant_hints + incorrect_guess_copy._hints._redundant_hints
    
    incorrect_guess_copy.process_guess()
    
    assert 1 == incorrect_guess_copy._stats.get_value("guesses remaining")

def test_process_guess_incorrect_too_many_arguments_raises_error(incorrect_guess_copy):
    with pytest.raises(TypeError):
        incorrect_guess_copy.process_guess("extra")



### GuessManager Tests


# Test _get_guess_obj method
def test_get_guess_obj_invalid(guess_manager_copy):
    guess_obj = guess_manager_copy._get_guess_obj("5.5")
    assert True == isinstance(guess_obj, InvalidGuess)

def test_get_guess_obj_correct(guess_manager_copy):
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess_obj = guess_manager_copy._get_guess_obj(str(winning_number))
    assert True == isinstance(guess_obj, CorrectGuess)

def test_get_guess_obj_incorrect(guess_manager_copy):
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess = str(int(winning_number) + 1) if int(winning_number) != 10 else "1"
    guess_obj = guess_manager_copy._get_guess_obj(guess)
    assert True == isinstance(guess_obj, IncorrectGuess)

def test_get_guess_obj_no_arguments_raises_error(guess_manager_copy):
    with pytest.raises(TypeError):
        guess_manager_copy._get_guess_obj()

def test_get_guess_obj_too_many_arguments_raises_error(guess_manager_copy):
    with pytest.raises(TypeError):
        guess_manager_copy._get_guess_obj("1", "extra")


# Test process_guess method
def test_process_guess_manager_invalid_non_integer_db(guess_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = guess_manager_copy._objects.get_object("session")
    db_update_params = {"settings": guess_manager_copy._settings, "error": False, "error_type": None}
    session.update_database("game", db_update_params)
    guess_manager_copy.process_guess("5.5")
    guess_table_query = "SELECT game_id, session_id, guess, error, error_type_id FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, "5.5", 1, 4)] == db_entry

def test_process_guess_manager_correct_db(guess_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = guess_manager_copy._objects.get_object("session")
    db_update_params = {"settings": guess_manager_copy._settings, "error": False, "error_type": None}
    session.update_database("game", db_update_params)
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess_manager_copy.process_guess(str(winning_number))
    guess_table_query = "SELECT game_id, session_id, guess, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, str(winning_number), 0)] == db_entry

def test_process_guess_manager_correct_return_value(guess_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = guess_manager_copy._objects.get_object("session")
    db_update_params = {"settings": guess_manager_copy._settings, "error": False, "error_type": None}
    session.update_database("game", db_update_params)
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    assert "win" == guess_manager_copy.process_guess(str(winning_number))

def test_process_guess_manager_incorrect_no_more_guesses_db(guess_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = guess_manager_copy._objects.get_object("session")
    db_update_params = {"settings": guess_manager_copy._settings, "error": False, "error_type": None}
    session.update_database("game", db_update_params)
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess = "3" if int(winning_number) != 3 else "5"
    stats = guess_manager_copy._objects.get_object("stats")
    stats._guesses_remaining.value = 1
    
    guess_manager_copy.process_guess(guess)
    
    guess_table_query = "SELECT game_id, session_id, guess, error FROM guess;"
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, guess, 0)] == db_entry

def test_process_guess_manager_incorrect_no_more_guesses_return_value(guess_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = guess_manager_copy._objects.get_object("session")
    db_update_params = {"settings": guess_manager_copy._settings, "error": False, "error_type": None}
    session.update_database("game", db_update_params)
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess = "3" if int(winning_number) != 3 else "5"
    stats = guess_manager_copy._objects.get_object("stats")
    stats._guesses_remaining.value = 1
    
    assert "lose" == guess_manager_copy.process_guess(guess)

def test_process_guess_manager_incorrect_no_more_hints_db(guess_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = guess_manager_copy._objects.get_object("session")
    db_update_params = {"settings": guess_manager_copy._settings, "error": False, "error_type": None}
    session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    stats = guess_manager_copy._objects.get_object("stats")
    stats._score.value = 20
    stats._guesses_remaining.value = 2
    guess_manager_copy._hints._relevant_hints = []
    guess_manager_copy._hints._redundant_hints = []
    guess_manager_copy._hints._hint_pool = guess_manager_copy._hints._relevant_hints + guess_manager_copy._hints._redundant_hints
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess = "3" if int(winning_number) != 3 else "5"
    
    guess_manager_copy.process_guess(guess)
    
    guess_table_query = """SELECT game_id, session_id, hint_type_id, hint_number, guess, feedback, error
                           FROM guess
                           ORDER BY guess_id DESC
                           LIMIT 1;"""
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 9, 2, guess, None, 0)] == db_entry

def test_process_guess_manager_incorrect_hints_remaining_db(guess_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = guess_manager_copy._objects.get_object("session")
    db_update_params = {"settings": guess_manager_copy._settings, "error": False, "error_type": None}
    session.update_database("game", db_update_params)
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    stats = guess_manager_copy._objects.get_object("stats")
    stats._score.value = 20
    stats._guesses_remaining.value = 2
    guess_manager_copy._hints._relevant_hints = []
    guess_manager_copy._hints._redundant_hints = incorrect_guess_hints.copy()
    guess_manager_copy._hints._hint_pool = guess_manager_copy._hints._relevant_hints + guess_manager_copy._hints._redundant_hints
    winning_number = guess_manager_copy._settings.get_setting("winning number")
    guess = "3" if int(winning_number) != 3 else "5"
    
    guess_manager_copy.process_guess(guess)
    
    guess_table_query = """SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error
                           FROM guess
                           ORDER BY guess_id DESC
                           LIMIT 1;"""
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 2, guess, "good", 0)] == db_entry

def test_get_guess_obj_no_arguments_raises_error(guess_manager_copy):
    with pytest.raises(TypeError):
        guess_manager_copy.process_guess()

def test_get_guess_obj_too_many_arguments_raises_error(guess_manager_copy):
    with pytest.raises(TypeError):
        guess_manager_copy.process_guess("1", "extra")



