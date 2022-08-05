import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.game.game_summarizers import *



### GameSummarizer Tests

@pytest.fixture
def game_summarizer_copy_win():
    return GameSummarizer(objects_fake_global_dict["easy"], "win")

@pytest.fixture
def game_summarizer_copy_lose():
    return GameSummarizer(objects_fake_global_dict["easy"], "lose")

@pytest.fixture
def game_summarizer_copy_quit():
    return GameSummarizer(objects_fake_global_dict["easy"], "quit")


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
def end_game_manager_copy_win():
    return EndGameManager(objects_fake_global_dict["easy"], "win")

class WinGameSummarizerStub(WinGameSummarizer):
    def _get_game_feedback(self):
        return "good"

@pytest.fixture
def win_game_summarizer_copy(end_game_manager_copy_win):
    stats = end_game_manager_copy_win._objects.get_object("stats")
    stats._score.value = 80
    return WinGameSummarizerStub(end_game_manager_copy_win._objects, "win")


# Test _get_score method
def test_get_score_outcome_obj(win_game_summarizer_copy):
    assert win_game_summarizer_copy._outcome_obj.score == win_game_summarizer_copy._get_score()

def test_get_score_return_value(win_game_summarizer_copy):
    assert 80 == win_game_summarizer_copy._get_score()

def test_get_score_too_many_arguments_raises_error(win_game_summarizer_copy):
    with pytest.raises(TypeError):
        win_game_summarizer_copy._get_score("extra")


# Test run_game_summary method
def test_run_game_summary_win_db(win_game_summarizer_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = win_game_summarizer_copy._objects.get_object("settings")
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    win_game_summarizer_copy._session.update_database("game", start_game_params)
    
    win_game_summarizer_copy.run_game_summary()
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 1, 80, 0)] == db_entry

def test_run_game_summary_win_message(win_game_summarizer_copy):
    win_game_summarizer_copy.run_game_summary()
    expected_text = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 80\n\n\nThanks for playing! Please come back soon."
    assert expected_text == win_game_summarizer_copy._text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_win_too_many_arguments_raises_error(win_game_summarizer_copy):
    with pytest.raises(TypeError):
        win_game_summarizer_copy.run_game_summary("extra")



### LoseGameSummarizer Tests

class LoseGameSummarizerStub(LoseGameSummarizer):
    def _get_game_feedback(self):
        return "bad"

@pytest.fixture
def lose_game_summarizer_copy():
    return LoseGameSummarizerStub(objects_fake_global_dict["easy"], "lose")


# Test run_game_summary method
def test_run_game_summary_lose_db(lose_game_summarizer_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = lose_game_summarizer_copy._objects.get_object("settings")
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    lose_game_summarizer_copy._session.update_database("game", start_game_params)
    
    lose_game_summarizer_copy.run_game_summary()
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, score, play_again FROM outcome;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, None, 0)] == db_entry

def test_run_game_summary_lose_message(lose_game_summarizer_copy):
    lose_game_summarizer_copy.run_game_summary()
    expected_text = "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon."
    assert expected_text == lose_game_summarizer_copy._text_display._variables.get_variable_text("last_msg")

def test_run_game_summary_lose_too_many_arguments_raises_error(lose_game_summarizer_copy):
    with pytest.raises(TypeError):
        lose_game_summarizer_copy.run_game_summary("extra")



### QuitGameSummarizer Tests

@pytest.fixture
def quit_game_summarizer_copy():
    return QuitGameSummarizer(objects_fake_global_dict["easy"], "quit")


# Test run_game_summary method
def test_run_game_summary_quit_db(quit_game_summarizer_copy, sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    settings = quit_game_summarizer_copy._objects.get_object("settings")
    start_game_params = {"settings": settings, "error": False, "error_type": None}
    quit_game_summarizer_copy._session.update_database("game", start_game_params)
    
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
def end_game_manager_copy_lose():
    return EndGameManager(objects_fake_global_dict["easy"], "lose")

@pytest.fixture
def end_game_manager_copy_quit():
    return EndGameManager(objects_fake_global_dict["easy"], "quit")


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



