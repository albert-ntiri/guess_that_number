import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict, ObjectManagerFake, GameSettings
from main.tests.test_data import data_copy, errors
from main.game.game_initializers import *



### Object Manager Setup

objects_fake_global_easy = objects_fake_global_dict["easy"]
objects_fake_global_medium = objects_fake_global_dict["medium"]
objects_fake_global_hard = objects_fake_global_dict["hard"]


### ValidSelection Tests

@pytest.fixture
def valid_selection_copy():
    return ValidSelection(objects_fake_global_easy)


# Test process_game_entry method
def test_process_game_entry_db(valid_selection_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM session;", _db_path=test_db_path)
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    valid_selection_copy.process_game_entry()
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, '1', '10', 0)] == db_entry

def test_process_game_entry_hints_more_than_two_hints(valid_selection_copy):
    valid_selection_copy.process_game_entry()
    assert len(valid_selection_copy._hints._hint_pool) > 2

def test_process_game_entry_hints_relevant_hints_matches_hint_pool(valid_selection_copy):
    valid_selection_copy.process_game_entry()
    assert valid_selection_copy._hints._relevant_hints == valid_selection_copy._hints._hint_pool

def test_process_game_entry_too_many_arguments_raises_error(valid_selection_copy):
    with pytest.raises(TypeError):
        valid_selection_copy.process_game_entry("extra")



#### InvalidSelection Tests

@pytest.fixture
def invalid_selection_copy(errors):
    invalid_error = errors.get_error_obj("invalid")
    return InvalidSelection(objects_fake_global_easy, invalid_error, ("1.5", "9.8"))


# Test _display_error_message method
def test_display_error_message(invalid_selection_copy):
    invalid_selection_copy._display_error_message()
    expected_error_message = "Both values must be integers."
    assert expected_error_message == invalid_selection_copy._text_display._variables.get_variable_text("range_error_msg")

def test_display_error_message_too_many_arguments_raises_error(invalid_selection_copy):
    with pytest.raises(TypeError):
        invalid_selection_copy._display_error_message("extra")


# Test _update_db method
def test_update_db(invalid_selection_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    invalid_selection_copy._update_db()
    game_table_query = "SELECT session_id, error, error_type_id FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3)] == db_entry

def test_update_db_too_many_arguments_raises_error(invalid_selection_copy):
    with pytest.raises(TypeError):
        invalid_selection_copy._update_db("extra")
    

# Test process_error method
def test_process_error_display(invalid_selection_copy):
    invalid_selection_copy.process_error()
    expected_error_message = "Both values must be integers."
    assert expected_error_message == invalid_selection_copy._text_display._variables.get_variable_text("range_error_msg")

def test_process_error_db(invalid_selection_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    invalid_selection_copy.process_error()
    game_table_query = "SELECT session_id, error, error_type_id FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3)] == db_entry

def test_process_error_too_many_arguments_raises_error(invalid_selection_copy):
    with pytest.raises(TypeError):
        invalid_selection_copy.process_error("extra")



#### GameInitializer Tests
    
@pytest.fixture
def game_initializer_copy():
    return GameInitializer(objects_fake_global_easy)
    
@pytest.fixture
def game_initializer_copy_medium():
    return GameInitializer(objects_fake_global_medium)
    
@pytest.fixture
def game_initializer_copy_hard():
    return GameInitializer(objects_fake_global_hard)


# Test initialize_game method
def test_initialize_game_custom_valid_db(game_initializer_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM session;", _db_path=test_db_path)
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "1")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "5")
    
    game_initializer_copy.initialize_game()
    
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 4, '1', '5', 0)] == db_entry

def test_initialize_game_custom_valid_hints_more_than_two_hints(game_initializer_copy):
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "1")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "5")
    
    game_initializer_copy.initialize_game()
    
    hints = game_initializer_copy._objects.get_object("hints")
    assert len(hints._hint_pool) > 2

def test_initialize_game_custom_valid_hints_relevant_hints_matches_hint_pool(game_initializer_copy):
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "1")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "5")
    
    game_initializer_copy.initialize_game()
    
    hints = game_initializer_copy._objects.get_object("hints")
    assert hints._relevant_hints == hints._hint_pool

def test_initialize_game_custom_error_comparison_display(game_initializer_copy):
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "5")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "1")
    
    game_initializer_copy.initialize_game()
    
    expected_error_message = "High value must be greater than low value."
    assert expected_error_message == game_initializer_copy._text_display._variables.get_variable_text("range_error_msg")

def test_initialize_game_custom_error_comparison_db(game_initializer_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "5")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "1")
    
    game_initializer_copy.initialize_game()
    
    game_table_query = "SELECT session_id, error, error_type_id FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1)] == db_entry

def test_initialize_game_custom_error_invalid_display(game_initializer_copy):
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "5")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy.initialize_game()
    
    expected_error_message = "Both values must be integers."
    assert expected_error_message == game_initializer_copy._text_display._variables.get_variable_text("range_error_msg")

def test_initialize_game_custom_error_invalid_db(game_initializer_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "5")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy.initialize_game()
    
    game_table_query = "SELECT session_id, error, error_type_id FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3)] == db_entry

def test_initialize_game_easy_db(game_initializer_copy, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM session;", _db_path=test_db_path)
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    level_easy = game_initializer_copy._data.get_sub_data_object("levels", "easy")
    game_initializer_copy._settings._level_obj = level_easy
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy.initialize_game()
    
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, '1', '10', 0)] == db_entry

def test_initialize_game_easy_hints_more_than_two_hints(game_initializer_copy):
    level_easy = game_initializer_copy._data.get_sub_data_object("levels", "easy")
    game_initializer_copy._settings._level_obj = level_easy
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy.initialize_game()
    
    hints = game_initializer_copy._objects.get_object("hints")
    assert len(hints._hint_pool) > 2

def test_initialize_game_easy_hints_relevant_hints_matches_hint_pool(game_initializer_copy):
    level_easy = game_initializer_copy._data.get_sub_data_object("levels", "easy")
    game_initializer_copy._settings._level_obj = level_easy
    game_initializer_copy._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy.initialize_game()
    
    hints = game_initializer_copy._objects.get_object("hints")
    assert hints._relevant_hints == hints._hint_pool

def test_initialize_game_medium_db(game_initializer_copy_medium, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM session;", _db_path=test_db_path)
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    level_medium = game_initializer_copy_medium._data.get_sub_data_object("levels", "medium")
    game_initializer_copy_medium._settings._level_obj = level_medium
    game_initializer_copy_medium._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy_medium._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy_medium.initialize_game()
    
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 2, '1', '100', 0)] == db_entry

def test_initialize_game_medium_hints_more_than_two_hints(game_initializer_copy_medium):
    level_medium = game_initializer_copy_medium._data.get_sub_data_object("levels", "medium")
    game_initializer_copy_medium._settings._level_obj = level_medium
    game_initializer_copy_medium._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy_medium._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy_medium.initialize_game()
    
    hints = game_initializer_copy_medium._objects.get_object("hints")
    assert len(hints._hint_pool) > 2

def test_initialize_game_medium_hints_relevant_hints_matches_hint_pool(game_initializer_copy_medium):
    level_medium = game_initializer_copy_medium._data.get_sub_data_object("levels", "medium")
    game_initializer_copy_medium._settings._level_obj = level_medium
    game_initializer_copy_medium._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy_medium._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy_medium.initialize_game()
    
    hints = game_initializer_copy_medium._objects.get_object("hints")
    assert hints._relevant_hints == hints._hint_pool

def test_initialize_game_hard_db(game_initializer_copy_hard, sqlite_db_fake, test_db_path):
    sqlite_db_fake.run_query("DELETE FROM session;", _db_path=test_db_path)
    sqlite_db_fake.run_query("DELETE FROM game;", _db_path=test_db_path)
    level_hard = game_initializer_copy_hard._data.get_sub_data_object("levels", "hard")
    game_initializer_copy_hard._settings._level_obj = level_hard
    game_initializer_copy_hard._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy_hard._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy_hard.initialize_game()
    
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 3, '1', '1000', 0)] == db_entry

def test_initialize_game_hard_hints_more_than_two_hints(game_initializer_copy_hard):
    level_hard = game_initializer_copy_hard._data.get_sub_data_object("levels", "hard")
    game_initializer_copy_hard._settings._level_obj = level_hard
    game_initializer_copy_hard._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy_hard._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy_hard.initialize_game()
    
    hints = game_initializer_copy_hard._objects.get_object("hints")
    assert len(hints._hint_pool) > 2

def test_initialize_game_hard_hints_relevant_hints_matches_hint_pool(game_initializer_copy_hard):
    level_hard = game_initializer_copy_hard._data.get_sub_data_object("levels", "hard")
    game_initializer_copy_hard._settings._level_obj = level_hard
    game_initializer_copy_hard._text_display._variables.display_variable_text("low_range", "")
    game_initializer_copy_hard._text_display._variables.display_variable_text("high_range", "")
    
    game_initializer_copy_hard.initialize_game()
    
    hints = game_initializer_copy_hard._objects.get_object("hints")
    assert hints._relevant_hints == hints._hint_pool

def test_initialize_game_too_many_arguments_raises_error(game_initializer_copy):
    with pytest.raises(TypeError):
        game_initializer_copy.initialize_game("extra")



numbers = objects_fake_global_easy.get_object("numbers")
data = objects_fake_global_easy.get_object("data")
level_easy = data.get_sub_data_object("levels", "easy")
settings = objects_fake_global_easy.create_object(GameSettings, "settings", ObjectManagerFake, numbers, level_easy)
settings.set_game_settings("", "")


