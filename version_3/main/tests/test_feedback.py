import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.game.feedback import *



### Object Manager Setup

objects_fake_global = objects_fake_global_dict["easy"]



### GuessFeedback Tests

@pytest.fixture
def guess_feedback_copy_one_hint(sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = objects_fake_global.get_object("session")
    settings = objects_fake_global.get_object("settings")
    session.update_database("game", {"settings": settings, "error": False, "error_type": None})
    
    for i in range(2, 3):
        multiple_hint = f"Nice try!  Hint: {i} is a multiple."
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                           VALUES(1, 1, 2, '{multiple_hint}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
    guess_feedback = GuessFeedback(objects_fake_global, feedback, 2)
    
    yield guess_feedback
    
    guess_feedback._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])

@pytest.fixture
def guess_feedback_copy_two_hints(sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = objects_fake_global.get_object("session")
    settings = objects_fake_global.get_object("settings")
    session.update_database("game", {"settings": settings, "error": False, "error_type": None})
    
    for i in range(2, 4):
        multiple_hint = f"Nice try!  Hint: {i} is a multiple."
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                           VALUES(1, 1, 2, '{multiple_hint}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
    guess_feedback = GuessFeedback(objects_fake_global, feedback, 2)
    
    yield guess_feedback
    
    guess_feedback._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])


# Test _generate_guess_feedback method
def test_generate_guess_feedback_good_one_hint(guess_feedback_copy_one_hint):
    hints = guess_feedback_copy_one_hint._objects.get_object("hints")
    guess_concepts = hints.get_concepts(guess_feedback_copy_one_hint._guess)
    assert (1, "good") == guess_feedback_copy_one_hint._generate_guess_feedback(guess_concepts)

def test_generate_guess_feedback_bad_two_hints(guess_feedback_copy_two_hints):
    guess_feedback_copy_two_hints._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    hints = guess_feedback_copy_two_hints._objects.get_object("hints")
    guess_concepts = hints.get_concepts(guess_feedback_copy_two_hints._guess)
    assert (2, "bad") == guess_feedback_copy_two_hints._generate_guess_feedback(guess_concepts)

def test_generate_guess_feedback_no_arguments_raises_error(guess_feedback_copy_one_hint):
    with pytest.raises(TypeError):
        guess_feedback_copy_one_hint._generate_guess_feedback()

def test_generate_guess_feedback_too_many_arguments_raises_error(guess_feedback_copy_one_hint):
    with pytest.raises(TypeError):
        guess_feedback_copy_one_hint._generate_guess_feedback("", "extra")


# Test _record_guess_feedback method
def test_record_guess_feedback_good_one_hint(guess_feedback_copy_one_hint):
    guess_feedback_copy_one_hint._record_guess_feedback(1, "good")
    expected_feedback_entry = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    assert expected_feedback_entry == list(guess_feedback_copy_one_hint._feedback.iloc[-1, :])

def test_record_guess_feedback_bad_two_hints(guess_feedback_copy_two_hints):
    guess_feedback_copy_two_hints._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    guess_feedback_copy_two_hints._record_guess_feedback(2, "bad")
    expected_feedback_entry = ["multiple", "Nice try!  Hint: 3 is a multiple.", 2, "bad"]
    assert expected_feedback_entry == list(guess_feedback_copy_two_hints._feedback.iloc[-1, :])

def test_record_guess_feedback_no_arguments_raises_error(guess_feedback_copy_one_hint):
    with pytest.raises(TypeError):
        guess_feedback_copy_one_hint._record_guess_feedback()

def test_record_guess_feedback_too_many_arguments_raises_error(guess_feedback_copy_one_hint):
    with pytest.raises(TypeError):
        guess_feedback_copy_one_hint._record_guess_feedback(1, "good", "extra")


# Test get_feedback method
def test_get_feedback_guess_good_one_hint_correct_return_value(guess_feedback_copy_one_hint):
    hints = guess_feedback_copy_one_hint._objects.get_object("hints")
    guess_concepts = hints.get_concepts(guess_feedback_copy_one_hint._guess)
    feedback = guess_feedback_copy_one_hint.get_feedback(guess_concepts)
    assert "good" == feedback

def test_get_feedback_guess_good_one_hint_df_updated(guess_feedback_copy_one_hint):
    hints = guess_feedback_copy_one_hint._objects.get_object("hints")
    guess_concepts = hints.get_concepts(guess_feedback_copy_one_hint._guess)
    guess_feedback_copy_one_hint.get_feedback(guess_concepts)
    expected_feedback_entry = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    assert expected_feedback_entry == list(guess_feedback_copy_one_hint._feedback.iloc[-1, :])

def test_get_feedback_guess_bad_two_hints_correct_return_value(guess_feedback_copy_two_hints):
    hints = guess_feedback_copy_two_hints._objects.get_object("hints")
    guess_concepts = hints.get_concepts(guess_feedback_copy_two_hints._guess)
    guess_feedback_copy_two_hints._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    feedback = guess_feedback_copy_two_hints.get_feedback(guess_concepts)
    assert "bad" == feedback

def test_get_feedback_guess_bad_two_hints_df_updated(guess_feedback_copy_two_hints):
    hints = guess_feedback_copy_two_hints._objects.get_object("hints")
    guess_concepts = hints.get_concepts(guess_feedback_copy_two_hints._guess)
    guess_feedback_copy_two_hints._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    guess_feedback_copy_two_hints.get_feedback(guess_concepts)
    expected_feedback_entry = ["multiple", "Nice try!  Hint: 3 is a multiple.", 2, "bad"]
    assert expected_feedback_entry == list(guess_feedback_copy_two_hints._feedback.iloc[-1, :])

def test_get_feedback_guess_no_arguments_raises_error(guess_feedback_copy_one_hint):
    with pytest.raises(TypeError):
        guess_feedback_copy_one_hint.get_feedback()

def test_get_feedback_guess_too_many_arguments_raises_error(guess_feedback_copy_one_hint):
    with pytest.raises(TypeError):
        guess_feedback_copy_one_hint.get_feedback("", "extra")



### GameFeedback Tests


# Test _record_game_feedback method


# Test _process_feedback method


# Test get_feedback method



### FeedbackManager Tests

@pytest.fixture
def feedback_manager_copy(sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    session = objects_fake_global.get_object("session")
    settings = objects_fake_global.get_object("settings")
    session.update_database("game", {"settings": settings, "error": False, "error_type": None})
    feedback_manager = FeedbackManager(objects_fake_global)
    
    yield feedback_manager
    
    feedback_manager._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])


# Test get_guess_feedback method
def test_get_guess_feedback_no_previous_hints(feedback_manager_copy):
    hints = feedback_manager_copy._objects.get_object("hints")
    guess_concepts = hints.get_concepts(2)
    feedback = feedback_manager_copy.get_guess_feedback(2, guess_concepts)
    assert None == feedback

def test_get_guess_feedback_good_one_hint_correct_return_value(feedback_manager_copy, sqlite_db_fake, test_db_path):
    for i in range(2, 3):
        multiple_hint = f"Nice try!  Hint: {i} is a multiple."
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                           VALUES(1, 1, 2, '{multiple_hint}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    
    hints = feedback_manager_copy._objects.get_object("hints")
    guess_concepts = hints.get_concepts(2)
    feedback = feedback_manager_copy.get_guess_feedback(2, guess_concepts)
    assert "good" == feedback

def test_get_guess_feedback_good_one_hint_df_updated(feedback_manager_copy, sqlite_db_fake, test_db_path):
    for i in range(2, 3):
        multiple_hint = f"Nice try!  Hint: {i} is a multiple."
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                           VALUES(1, 1, 2, '{multiple_hint}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    
    hints = feedback_manager_copy._objects.get_object("hints")
    guess_concepts = hints.get_concepts(2)
    feedback_manager_copy.get_guess_feedback(2, guess_concepts)
    expected_feedback_entry = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    assert expected_feedback_entry == list(feedback_manager_copy._feedback.iloc[-1, :])

def test_get_guess_feedback_bad_two_hints_correct_return_value(feedback_manager_copy, sqlite_db_fake, test_db_path):
    for i in range(2, 4):
        multiple_hint = f"Nice try!  Hint: {i} is a multiple."
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                           VALUES(1, 1, 2, '{multiple_hint}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    
    hints = feedback_manager_copy._objects.get_object("hints")
    guess_concepts = hints.get_concepts(2)
    feedback = feedback_manager_copy.get_guess_feedback(2, guess_concepts)
    assert "bad" == feedback

def test_get_feedback_bad_two_hints_df_updated(feedback_manager_copy, sqlite_db_fake, test_db_path):
    for i in range(2, 4):
        multiple_hint = f"Nice try!  Hint: {i} is a multiple."
        insert_query = f"""INSERT INTO guess(game_id, session_id, hint_type_id, hint)
                           VALUES(1, 1, 2, '{multiple_hint}');"""
        sqlite_db_fake.run_query(insert_query, _db_path=test_db_path)
    
    hints = feedback_manager_copy._objects.get_object("hints")
    guess_concepts = hints.get_concepts(2)
    feedback_manager_copy._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", 2, "good"]
    feedback_manager_copy.get_guess_feedback(2, guess_concepts)
    expected_feedback_entry = ["multiple", "Nice try!  Hint: 3 is a multiple.", 2, "bad"]
    assert expected_feedback_entry == list(feedback_manager_copy._feedback.iloc[-1, :])

def test_get_guess_feedback_no_arguments_raises_error(feedback_manager_copy):
    with pytest.raises(TypeError):
        feedback_manager_copy.get_guess_feedback()

def test_get_guess_feedback_too_many_arguments_raises_error(feedback_manager_copy):
    with pytest.raises(TypeError):
        feedback_manager_copy.get_guess_feedback(2, "", "extra")


# Test get_feedback_df method
def test_get_feedback_df(feedback_manager_copy):
    feedback_df = feedback_manager_copy.get_feedback_df()
    assert True == isinstance(feedback_df, pd.DataFrame)

def test_get_feedback_df_too_many_arguments_raises_error(feedback_manager_copy):
    with pytest.raises(TypeError):
        feedback_manager_copy.get_feedback_df("extra")



