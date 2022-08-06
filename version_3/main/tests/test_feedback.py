import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.game.feedback import *



### Object Manager Setup

objects_fake_global = objects_fake_global_dict["game_level"]



### GuessFeedback Tests

@pytest.fixture
def guess_feedback_copy_one_hint(sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = objects_fake_global.get_object("games")
    games.add_game()
    games._current_game._outcome = "lose"
    
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
    games = objects_fake_global.get_object("games")
    games.add_game()
    games._current_game._outcome = "lose"
    
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

@pytest.fixture
def game_feedback_copy(sqlite_db_fake, test_db_path):
    for table in ["game", "outcome"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = objects_fake_global.get_object("games")
    games.add_game()
    games._current_game._outcome = "lose"
    data = objects_fake_global.get_object("data")
    outcome_obj = data.get_sub_data_object("outcomes", "lose")
    db_update_params_new = {"entry_type": "New", "outcome_obj": outcome_obj}
    session = objects_fake_global.get_object("session")
    session.update_database("outcome", db_update_params_new)
    
    feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
    game_feedback = GameFeedback(objects_fake_global, feedback, None)
    
    yield game_feedback
    
    game_feedback._feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])


# Test _record_game_feedback method
def test_record_game_feedback(game_feedback_copy, sqlite_db_fake, test_db_path):
    game_feedback_copy._feedback_type = "improvement"
    game_feedback_copy._record_game_feedback(improvement_area_id=2)
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_record_game_feedback_too_many_arguments_raises_error(game_feedback_copy):
    with pytest.raises(TypeError):
        game_feedback_copy._record_game_feedback(improvement_area_id=2, recommendation_type=None, extra="no")


# Test _process_feedback method
def test_process_feedback_message(game_feedback_copy):
    feedback_mgr = game_feedback_copy._objects.create_object(FeedbackManager, "feedback", GameFeedback, game_feedback_copy._objects)
    feedback_mgr._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    feedback_mgr._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    feedback_mgr._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    feedback_mgr._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    feedback_mgr._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    
    game_feedback_copy._process_feedback()
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    
    assert expected_feedback == game_feedback_copy._text_display._variables.get_variable_text("feedback_text")

def test_process_feedback_db(game_feedback_copy, sqlite_db_fake, test_db_path):
    feedback_mgr = game_feedback_copy._objects.create_object(FeedbackManager, "feedback", GameFeedback, game_feedback_copy._objects)
    feedback_mgr._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    feedback_mgr._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    feedback_mgr._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    feedback_mgr._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    feedback_mgr._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    
    game_feedback_copy._process_feedback()
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_process_feedback_too_many_arguments_raises_error(game_feedback_copy):
    with pytest.raises(TypeError):
        game_feedback_copy._process_feedback("extra")


# Test get_feedback method
def test_get_feedback_improvement_message(game_feedback_copy):
    feedback_mgr = game_feedback_copy._objects.create_object(FeedbackManager, "feedback", GameFeedback, game_feedback_copy._objects)
    game_feedback_copy._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    game_feedback_copy._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    game_feedback_copy._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    game_feedback_copy._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    game_feedback_copy._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    game_feedback_copy._feedback = feedback_mgr._feedback
    
    game_feedback_copy.get_feedback()
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    
    assert expected_feedback == game_feedback_copy._text_display._variables.get_variable_text("feedback_text")

def test_get_feedback_improvement_db(game_feedback_copy, sqlite_db_fake, test_db_path):
    feedback_mgr = game_feedback_copy._objects.create_object(FeedbackManager, "feedback", GameFeedback, game_feedback_copy._objects)
    feedback_mgr._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    feedback_mgr._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    feedback_mgr._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    feedback_mgr._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    feedback_mgr._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    game_feedback_copy._feedback = feedback_mgr._feedback
    
    game_feedback_copy.get_feedback()
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_get_feedback_too_many_arguments_raises_error(game_feedback_copy):
    with pytest.raises(TypeError):
        game_feedback_copy.get_feedback("extra")



### FeedbackManager Tests

@pytest.fixture
def feedback_manager_copy(sqlite_db_fake, test_db_path):
    for table in ["game", "guess"]:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    games = objects_fake_global.get_object("games")
    games.add_game()
    games._current_game._outcome = "lose"
    feedback_manager = objects_fake_global.create_object(FeedbackManager, "feedback", FeedbackManager, objects_fake_global)
    
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


# Test get_game_feedback method
def test_get_game_feedback_improvement_message(feedback_manager_copy):
    feedback_manager_copy._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    feedback_manager_copy._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    feedback_manager_copy._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    feedback_manager_copy._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    feedback_manager_copy._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    
    feedback_manager_copy.get_game_feedback(None)
    
    
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    text_display = feedback_manager_copy._objects.get_object("text_display")
    
    assert expected_feedback == text_display._variables.get_variable_text("feedback_text")

def test_get_game_feedback_improvement_db(feedback_manager_copy, sqlite_db_fake, test_db_path):
    feedback_manager_copy._feedback.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    feedback_manager_copy._feedback.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    feedback_manager_copy._feedback.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    feedback_manager_copy._feedback.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    feedback_manager_copy._feedback.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    
    feedback_manager_copy.get_game_feedback(None)
    
    outcome_table_query = "SELECT game_id, session_id, outcome_type_id, feedback_type, improvement_area_id FROM outcome WHERE outcome_id = 1;"
    db_entry = sqlite_db_fake.run_query(outcome_table_query, fetch="all", _db_path=test_db_path)
    assert [(1, 1, 2, "improvement", 2)] == db_entry

def test_get_game_feedback_no_arguments_raises_error(feedback_manager_copy):
    with pytest.raises(TypeError):
        feedback_manager_copy.get_game_feedback()

def test_get_game_feedback_too_many_arguments_raises_error(feedback_manager_copy):
    with pytest.raises(TypeError):
        feedback_manager_copy.get_game_feedback(None, "extra")


# Test get_feedback_df method
def test_get_feedback_df(feedback_manager_copy):
    feedback_df = feedback_manager_copy.get_feedback_df()
    assert True == isinstance(feedback_df, pd.DataFrame)

def test_get_feedback_df_too_many_arguments_raises_error(feedback_manager_copy):
    with pytest.raises(TypeError):
        feedback_manager_copy.get_feedback_df("extra")



