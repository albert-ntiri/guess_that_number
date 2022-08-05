import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.game.game import *
from main.tests.test_guess import incorrect_guess_hints, prime_hint
from main.tests.test_text_displayers import variable_values



### Game Tests

@pytest.fixture
def game_fake():
    game = Game(objects_fake_global_dict["easy"])
    return game


# Test _display_initial_status method
def test_display_initial_status_guess_prompt(game_fake):
    game_fake._settings.set_game_settings("", "")
    game_fake._stats.update_game_stats()
    game_fake._display_initial_status()
    assert "Guess a number between 1 and 10." == game_fake._text_display._variables.get_variable_text("guess_prompt_text")

def test_display_initial_status_status(game_fake):
    game_fake._settings.set_game_settings("", "")
    game_fake._stats.update_game_stats()
    game_fake._display_initial_status()
    assert "Guesses Remaining: 10" == game_fake._text_display._variables.get_variable_text("status_text")

def test_display_initial_status_too_many_arguments_raises_error(game_fake):
    with pytest.raises(TypeError):
        game_fake._display_initial_status("extra")


# Test configure_game method
def test_configure_game_guess_prompt(game_fake):
    game_fake.configure_game()
    assert "Guess a number between 1 and 10." == game_fake._text_display._variables.get_variable_text("guess_prompt_text")

def test_configure_game_status(game_fake):
    game_fake.configure_game()
    assert "Guesses Remaining: 10" == game_fake._text_display._variables.get_variable_text("status_text")

def test_configure_game_db(game_fake, sqlite_db_fake, test_db_path):
    for table in ["session", "game"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    
    game_fake.configure_game()
    
    game_table_query = "SELECT session_id, level_of_difficulty_type_id, range_low, range_high, error FROM game;"
    db_entry = sqlite_db_fake.run_query(game_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, '1', '10', 0)] == db_entry

def test_configure_game_too_many_arguments_raises_error(game_fake):
    with pytest.raises(TypeError):
        game_fake.configure_game("extra")


# Test add_guess method
def test_add_guess_incorrect_hints_remaining_db(game_fake, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    game_fake.configure_game()
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    game_fake._stats._score.value = 20
    game_fake._stats._guesses_remaining.value = 2
    game_fake._hints._relevant_hints = []
    game_fake._hints._redundant_hints = incorrect_guess_hints.copy()
    game_fake._hints._hint_pool = game_fake._hints._relevant_hints + game_fake._hints._redundant_hints
    winning_number = game_fake._settings.get_setting("winning number")
    guess = "3" if int(winning_number) != 3 else "5"
    game_fake._text_display.display_text("dynamic", "guess", guess)
    
    game_fake.add_guess()
    
    guess_table_query = """SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error
                           FROM guess
                           ORDER BY guess_id DESC
                           LIMIT 1;"""
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 2, guess, "good", 0)] == db_entry

def test_add_guess_too_many_arguments_raises_error(game_fake):
    with pytest.raises(TypeError):
        game_fake.add_guess("extra")


# Test summarize_game method


# Test get_outcome method
def test_get_outcome(game_fake):
    game_fake._outcome = "win"
    assert "win" == game_fake.get_outcome()

def test_get_outcome_too_many_arguments_raises_error(game_fake):
    with pytest.raises(TypeError):
        game_fake.get_outcome("extra")


# Test clear_text_variables method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_clear_text_variables(game_fake, variable_name, text):
    game_fake._text_display._variables.display_variable_text(variable_name, text)
    game_fake.clear_text_variables()
    variable = game_fake._text_display._variables._get_kivy_variable(variable_name)
    assert "" == variable.text

def test_clear_text_variables_too_many_arguments_raises_error(game_fake):
    with pytest.raises(TypeError):
        game_fake.clear_text_variables("extra")



