import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.game.game_summarizers import *
import pandas as pd



### Object Manager Setup

objects_fake_global_easy = objects_fake_global_dict["easy"]
objects_fake_global_game_level = objects_fake_global_dict["game_level"]



### GameSummarizer Tests

@pytest.fixture
def game_summarizer_copy_win():
    return GameSummarizer(objects_fake_global_easy, "win")

@pytest.fixture
def game_summarizer_copy_lose():
    return GameSummarizer(objects_fake_global_easy, "lose")

@pytest.fixture
def game_summarizer_copy_quit():
    return GameSummarizer(objects_fake_global_easy, "quit")


# Test _get_outcome_object method
def test_get_outcome_object_win(game_summarizer_copy_win):
    outcome_obj = game_summarizer_copy_win._get_outcome_object("win")
    assert 1 == outcome_obj.get_id()

def test_get_outcome_object_lose(game_summarizer_copy_win):
    outcome_obj = game_summarizer_copy_win._get_outcome_object("lose")
    assert 2 == outcome_obj.get_id()

def test_get_outcome_object_quit(game_summarizer_copy_win):
    outcome_obj = game_summarizer_copy_win._get_outcome_object("quit")
    assert 3 == outcome_obj.get_id()

def test_get_outcome_object_no_arguments_raises_error(game_summarizer_copy_win):
    with pytest.raises(TypeError):
        game_summarizer_copy_win._get_outcome_object()

def test_get_outcome_object_too_many_arguments_raises_error(game_summarizer_copy_win):
    with pytest.raises(TypeError):
        game_summarizer_copy_win._get_outcome_object("win", "extra")


# Test _update_database method
def test_update_database_score(game_summarizer_copy_win, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = game_summarizer_copy_win._objects.get_object("settings")
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    game_summarizer_copy_win._session.update_database("game", start_game_params)
    data = game_summarizer_copy_win._objects.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "win")
    outcome_obj.score = 80
    
    game_summarizer_copy_win._update_database()
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 80, 0)] == db_entry

def test_update_database_no_score(game_summarizer_copy_lose, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = game_summarizer_copy_lose._objects.get_object("settings")
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    game_summarizer_copy_lose._session.update_database("game", start_game_params)
    
    game_summarizer_copy_lose._update_database()
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, None, 0)] == db_entry

def test_update_database_too_many_arguments_raises_error(game_summarizer_copy_win):
    with pytest.raises(TypeError):
        game_summarizer_copy_win._update_database("extra")


# Test _get_end_game_message method
def test_get_end_game_message_win(game_summarizer_copy_win):
    game_summarizer_copy_win._get_end_game_message()
    expected_text = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 80\n\n\nThanks for playing! Please come back soon."
    assert expected_text == game_summarizer_copy_win._text_display._variables.get_variable_text("last_msg")

def test_get_end_game_message_lose(game_summarizer_copy_lose):
    game_summarizer_copy_lose._get_end_game_message()
    expected_text = "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon."
    assert expected_text == game_summarizer_copy_lose._text_display._variables.get_variable_text("last_msg")

def test_get_end_game_message_quit(game_summarizer_copy_quit):
    game_summarizer_copy_quit._get_end_game_message()
    expected_text = "Thanks for playing! Please come back soon."
    assert expected_text == game_summarizer_copy_quit._text_display._variables.get_variable_text("last_msg")

def test_get_end_game_message_too_many_arguments_raises_error(game_summarizer_copy_win):
    with pytest.raises(TypeError):
        game_summarizer_copy_win._get_end_game_message("extra")



### WinGameSummarizer Tests

@pytest.fixture
def end_game_manager_copy_win(sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = objects_fake_global_game_level.get_object("games")
    games.add_game()
    games._current_game._stats._score.value = 80
    games._current_game._feedback._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    games._current_game._feedback._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    games._current_game._feedback._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    games._current_game._feedback._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    games._current_game._feedback._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    yield EndGameManager(objects_fake_global_game_level, "win")
    games._games = []
    games._current_game._feedback._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
    games._aggregate_feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])

@pytest.fixture
def win_game_summarizer_copy(end_game_manager_copy_win):
    yield WinGameSummarizer(end_game_manager_copy_win._objects, "win")
    games = objects_fake_global_game_level.get_object("games")


# Test _get_score method
def test_get_score_outcome_obj(win_game_summarizer_copy):
    assert win_game_summarizer_copy._outcome_obj.score == win_game_summarizer_copy._get_score()

def test_get_score_return_value(win_game_summarizer_copy):
    assert 80 == win_game_summarizer_copy._get_score()

def test_get_score_too_many_arguments_raises_error(win_game_summarizer_copy):
    with pytest.raises(TypeError):
        win_game_summarizer_copy._get_score("extra")


# Test _get_game_feedback method
def test_get_game_feedback_win_improvement_message(win_game_summarizer_copy):
    win_game_summarizer_copy._session.update_database("outcome", {"entry_type": "New",
                                                                  "outcome_obj": win_game_summarizer_copy._outcome_obj})
    
    win_game_summarizer_copy._get_game_feedback()
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    assert expected_feedback == win_game_summarizer_copy._text_display._variables.get_variable_text("feedback_text")

def test_get_game_feedback_win_improvement_db(win_game_summarizer_copy, sqlite_db_fake, test_db_path):
    win_game_summarizer_copy._session.update_database("outcome", {"entry_type": "New",
                                                                  "outcome_obj": win_game_summarizer_copy._outcome_obj})
    
    win_game_summarizer_copy._get_game_feedback()
    
    outcome_table_query = """SELECT outcome_id, game_id, session_id, outcome_type_id, score, feedback_type, improvement_area_id
                             FROM outcome;"""
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 1, 80, "improvement", 2)] == db_entry

def test_get_game_feedback_win_too_many_arguments_raises_error(win_game_summarizer_copy):
    with pytest.raises(TypeError):
        win_game_summarizer_copy._get_game_feedback("extra")


# Test run_game_summary method
def test_run_game_summary_win_improvement_feedback(win_game_summarizer_copy):
    win_game_summarizer_copy.run_game_summary()
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    assert expected_feedback == win_game_summarizer_copy._text_display._variables.get_variable_text("feedback_text")

def test_run_game_summary_win_db(win_game_summarizer_copy, sqlite_db_fake, test_db_path):
    win_game_summarizer_copy.run_game_summary()
    
    outcome_table_query = """SELECT outcome_id, game_id, session_id, outcome_type_id, score, feedback_type, improvement_area_id,
                             play_again FROM outcome;"""
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 1, 80, "improvement", 2, 0)] == db_entry

def test_run_game_summary_win_end_game_message(win_game_summarizer_copy):
    win_game_summarizer_copy.run_game_summary()
    expected_text = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 80\n\n\nThanks for playing! Please come back soon."
    assert expected_text == win_game_summarizer_copy._text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_win_too_many_arguments_raises_error(win_game_summarizer_copy):
    with pytest.raises(TypeError):
        win_game_summarizer_copy.run_game_summary("extra")



### LoseGameSummarizer Tests

@pytest.fixture
def lose_game_summarizer_copy(sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = objects_fake_global_game_level.get_object("games")
    games.add_game()
    games._current_game._feedback._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    games._current_game._feedback._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    games._current_game._feedback._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    games._current_game._feedback._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    games._current_game._feedback._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    yield LoseGameSummarizer(objects_fake_global_game_level, "lose")
    games._games = []
    games._current_game._feedback._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
    games._aggregate_feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])


# Test _get_game_feedback method
def test_get_game_feedback_lose_improvement_message(lose_game_summarizer_copy):
    lose_game_summarizer_copy._session.update_database("outcome", {"entry_type": "New",
                                                                  "outcome_obj": lose_game_summarizer_copy._outcome_obj})
    
    lose_game_summarizer_copy._get_game_feedback()
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    assert expected_feedback == lose_game_summarizer_copy._text_display._variables.get_variable_text("feedback_text")

def test_get_game_feedback_lose_improvement_db(lose_game_summarizer_copy, sqlite_db_fake, test_db_path):
    lose_game_summarizer_copy._session.update_database("outcome", {"entry_type": "New",
                                                                  "outcome_obj": lose_game_summarizer_copy._outcome_obj})
    
    lose_game_summarizer_copy._get_game_feedback()
    
    outcome_table_query = """SELECT outcome_id, game_id, session_id, outcome_type_id, score, feedback_type, improvement_area_id
                             FROM outcome;"""
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 2, None, "improvement", 2)] == db_entry

def test_get_game_feedback_lose_too_many_arguments_raises_error(lose_game_summarizer_copy):
    with pytest.raises(TypeError):
        lose_game_summarizer_copy._get_game_feedback("extra")


# Test run_game_summary method
def test_run_game_summary_lose_feedback(lose_game_summarizer_copy):
    lose_game_summarizer_copy.run_game_summary()
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    assert expected_feedback == lose_game_summarizer_copy._text_display._variables.get_variable_text("feedback_text")

def test_run_game_summary_lose_db(lose_game_summarizer_copy, sqlite_db_fake, test_db_path):
    lose_game_summarizer_copy.run_game_summary()
    
    outcome_table_query = """SELECT outcome_id, game_id, session_id, outcome_type_id, score, feedback_type, improvement_area_id,
                             play_again FROM outcome;"""
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 2, None, "improvement", 2, 0)] == db_entry

def test_run_game_summary_lose_end_game_message(lose_game_summarizer_copy):
    lose_game_summarizer_copy.run_game_summary()
    expected_text = "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon."
    assert expected_text == lose_game_summarizer_copy._text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_lose_too_many_arguments_raises_error(lose_game_summarizer_copy):
    with pytest.raises(TypeError):
        lose_game_summarizer_copy.run_game_summary("extra")



### QuitGameSummarizer Tests

@pytest.fixture
def quit_game_summarizer_copy():
    games = objects_fake_global_game_level.get_object("games")
    games.add_game()
    return QuitGameSummarizer(objects_fake_global_game_level, "quit")
    games._games = []
    games._current_game._feedback._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])


# Test run_game_summary method
def test_run_game_summary_quit_db(quit_game_summarizer_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = quit_game_summarizer_copy._objects.get_object("games")
    games.add_game()
    
    quit_game_summarizer_copy.run_game_summary()
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 3, None, 0)] == db_entry

def test_run_game_summary_quit_message(quit_game_summarizer_copy):
    quit_game_summarizer_copy.run_game_summary()
    expected_text = "Thanks for playing! Please come back soon."
    assert expected_text == quit_game_summarizer_copy._text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_quit_too_many_arguments_raises_error(quit_game_summarizer_copy):
    with pytest.raises(TypeError):
        quit_game_summarizer_copy.run_game_summary("extra")



### EndGameManager Tests

@pytest.fixture
def end_game_manager_copy_lose(sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = objects_fake_global_game_level.get_object("games")
    games.add_game()
    yield EndGameManager(objects_fake_global_game_level, "lose")
    games._games = []

@pytest.fixture
def end_game_manager_copy_quit(sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = objects_fake_global_game_level.get_object("games")
    games.add_game()
    yield EndGameManager(objects_fake_global_game_level, "quit")
    games._games = []


# Test _get_game_summarizer method
def test_get_game_summarizer_win(end_game_manager_copy_win):
    game_summarizer = end_game_manager_copy_win._get_game_summarizer()
    assert True == isinstance(game_summarizer, WinGameSummarizer)

def test_get_game_summarizer_lose(end_game_manager_copy_lose):
    game_summarizer = end_game_manager_copy_lose._get_game_summarizer()
    assert True == isinstance(game_summarizer, LoseGameSummarizer)

def test_get_game_summarizer_quit(end_game_manager_copy_quit):
    game_summarizer = end_game_manager_copy_quit._get_game_summarizer()
    assert True == isinstance(game_summarizer, QuitGameSummarizer)

def test_get_game_summarizer_too_many_arguments_raises_error(end_game_manager_copy_win):
    with pytest.raises(TypeError):
        end_game_manager_copy_win.run_game_summary("extra")


# Test run_game_summary method
def test_run_game_summary_mgr_improvement_feedback(end_game_manager_copy_win):
    end_game_manager_copy_win.run_game_summary()
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    text_display = end_game_manager_copy_win._objects.get_object("text_display")
    
    assert expected_feedback == text_display._variables.get_variable_text("feedback_text")

def test_run_game_summary_mgr_win_db(end_game_manager_copy_win, sqlite_db_fake, test_db_path):
    end_game_manager_copy_win.run_game_summary()
    
    outcome_table_query = """SELECT outcome_id, game_id, session_id, outcome_type_id, score, feedback_type, improvement_area_id,
                             play_again FROM outcome;"""
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 1, 80, "improvement", 2, 0)] == db_entry

def test_run_game_summary_mgr_win_end_game_message(end_game_manager_copy_win):
    end_game_manager_copy_win.run_game_summary()
    
    text_display = end_game_manager_copy_win._objects.get_object("text_display")
    expected_text = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 80\n\n\nThanks for playing! Please come back soon."
    assert expected_text == text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_mgr_lose_db(end_game_manager_copy_lose, sqlite_db_fake, test_db_path):
    end_game_manager_copy_lose.run_game_summary()
    
    outcome_table_query = """SELECT outcome_id, game_id, session_id, outcome_type_id, score, feedback_type, improvement_area_id,
                             play_again FROM outcome;"""
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 2, None, None, None, 0)] == db_entry

def test_run_game_summary_mgr_lose_end_game_message(end_game_manager_copy_lose):
    end_game_manager_copy_lose.run_game_summary()
    
    text_display = end_game_manager_copy_lose._objects.get_object("text_display")
    expected_text = "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon."
    assert expected_text == text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_mgr_quit_db(end_game_manager_copy_quit, sqlite_db_fake, test_db_path):
    end_game_manager_copy_quit.run_game_summary()
    
    outcome_table_query = """SELECT outcome_id, game_id, session_id, outcome_type_id, score, feedback_type, improvement_area_id,
                             play_again FROM outcome;"""
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 3, None, None, None, 0)] == db_entry

def test_run_game_summary_mgr_quit_message(end_game_manager_copy_quit):
    end_game_manager_copy_quit.run_game_summary()
    
    text_display = end_game_manager_copy_quit._objects.get_object("text_display")
    expected_text = "Thanks for playing! Please come back soon."
    assert expected_text == text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_mgr_too_many_arguments_raises_error(end_game_manager_copy_win):
    with pytest.raises(TypeError):
        end_game_manager_copy_win.run_game_summary("extra")



