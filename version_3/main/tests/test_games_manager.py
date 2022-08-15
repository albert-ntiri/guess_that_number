import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.resources.games_manager import *
from main.tests.test_guess import incorrect_guess_hints, prime_hint
from main.tests.test_text_displayers import variable_values
import pandas as pd



### GamesManager Tests

@pytest.fixture
def games_manager_copy():
    objects = objects_fake_global_dict["game_level"]
    games_manager = objects.get_object("games")
    yield games_manager
    games_manager._games = []


# Test add_game method
def test_add_game_current_game_set(games_manager_copy):
    games_manager_copy.add_game()
    assert True == isinstance(games_manager_copy._current_game, Game)

def test_add_game_games_list_updated(games_manager_copy):
    previous_count = len(games_manager_copy._games)
    games_manager_copy.add_game()
    new_count = len(games_manager_copy._games)
    assert new_count == previous_count + 1

def test_add_game_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.add_game("extra")


# Test add_guess_to_current_game method
def test_add_guess_to_current_game_incorrect_hints_remaining_db(games_manager_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games_manager_copy.add_game()
    insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                       VALUES(1, 1, 4, 'Nice try!  Hint: It is an odd number.');"""
    sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    game = games_manager_copy._current_game
    game._stats._score.value = 20
    game._stats._guesses_remaining.value = 2
    game._hints._relevant_hints = []
    game._hints._redundant_hints = incorrect_guess_hints.copy()
    game._hints._hint_pool = game._hints._relevant_hints + game._hints._redundant_hints
    winning_number = game._settings.get_setting("winning number")
    guess = "3" if int(winning_number) != 3 else "5"
    game._text_display.display_text("dynamic", "guess", guess)
    
    games_manager_copy.add_guess_to_current_game()
    
    guess_table_query = """SELECT game_id, session_id, hint_type_id, hint, hint_number, guess, feedback, error
                           FROM guess
                           ORDER BY guess_id DESC
                           LIMIT 1;"""
    db_entry = sqlite_db_fake.run_query(guess_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, prime_hint, 2, guess, "good", 0)] == db_entry

def test_add_guess_to_current_game_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.add_guess_to_current_game("extra")


# Test end_current_game method
def test_summarize_game_win_end_game_message(games_manager_copy):
    games_manager_copy.add_game()
    stats = games_manager_copy._objects.get_object("stats")
    stats._score.value = 80
    
    games_manager_copy.end_current_game("win")
    
    text_display = games_manager_copy._objects.get_object("text_display")
    expected_text = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 80\n\n\nThanks for playing! Please come back soon."
    assert expected_text == text_display._variables.get_variable_text("last_msg")

def test_summarize_game_lose_end_game_message(games_manager_copy):
    games_manager_copy.add_game()
    games_manager_copy.end_current_game("lose")
    
    text_display = games_manager_copy._objects.get_object("text_display")
    expected_text = "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon."
    assert expected_text == text_display._variables.get_variable_text("last_msg")

def test_summarize_game_quit_message(games_manager_copy):
    games_manager_copy.add_game()
    games_manager_copy.end_current_game("quit")
    
    text_display = games_manager_copy._objects.get_object("text_display")
    expected_text = "Thanks for playing! Please come back soon."
    assert expected_text == text_display._variables.get_variable_text("last_msg")

def test_summarize_game_no_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.end_current_game()

def test_summarize_game_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.end_current_game("win", "extra")


# Test update_aggregate_feedback method
def test_update_aggregate_feedback(games_manager_copy):
    game_feedback = pd.DataFrame([["multiple", "hint 1", "4", "bad"]], columns=["hint_type", "hint", "guess", "feedback_ind"])
    previous_length = len(games_manager_copy._aggregate_feedback)
    games_manager_copy.update_aggregate_feedback(game_feedback)
    new_length = len(games_manager_copy._aggregate_feedback)
    assert new_length == previous_length + len(game_feedback)

def test_update_aggregate_feedback_no_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.update_aggregate_feedback()

def test_update_aggregate_feedback_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.update_aggregate_feedback([], "extra")

# Test get_aggregate_feedback method
def test_get_aggregate_feedback(games_manager_copy):
    aggregate_feedback = games_manager_copy._aggregate_feedback.copy()
    assert list(aggregate_feedback) == list(games_manager_copy.get_aggregate_feedback())

def test_get_aggregate_feedback_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.get_aggregate_feedback("extra")


# Test reset_current_game method
def test_reset_current_game_data(games_manager_copy):
    games_manager_copy.add_game()
    data = games_manager_copy._objects.get_object("data")
    data._outcomes._win.score = 75
    games_manager_copy.reset_current_game()
    assert None == data._outcomes._win.score

@pytest.mark.parametrize("variable_name, text", variable_values)
def test_reset_current_game_variables(games_manager_copy, variable_name, text):
    games_manager_copy.add_game()
    games_manager_copy._current_game._text_display._variables.display_variable_text(variable_name, text)
    games_manager_copy.reset_current_game()
    latest_game = games_manager_copy._games[-1]
    variable = latest_game._text_display._variables._get_kivy_variable(variable_name)
    assert "" == variable.text

def test_reset_current_game_cleared(games_manager_copy):
    games_manager_copy.add_game()
    games_manager_copy.reset_current_game()
    assert None == games_manager_copy._current_game

def test_reset_current_game_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.reset_current_game("extra")


# Test get_current_game_outcome method
def test_get_outcome(games_manager_copy):
    games_manager_copy.add_game()
    games_manager_copy._current_game._outcome = "win"
    assert "win" == games_manager_copy.get_current_game_outcome()

def test_get_outcome_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.get_current_game_outcome("extra")


# Test get_game_count method
def test_get_game_count_no_quit(games_manager_copy):
    games_manager_copy.add_game()
    games_manager_copy._current_game._outcome = "win"
    
    assert 1 == games_manager_copy.get_game_count()

def test_get_game_count_quit(games_manager_copy):
    games_manager_copy.add_game()
    games_manager_copy._current_game._outcome = "win"
    games_manager_copy.add_game()
    games_manager_copy._current_game._outcome = "lose"
    games_manager_copy.add_game()
    games_manager_copy._current_game._outcome = "quit"
    
    assert 2 == games_manager_copy.get_game_count()

def test_get_game_count_too_many_arguments_raises_error(games_manager_copy):
    with pytest.raises(TypeError):
        games_manager_copy.get_game_count(True, "extra")



objects = objects_fake_global_dict["game_level"]
text_display = objects.get_object("text_display")
text_display.clear_all_variables()