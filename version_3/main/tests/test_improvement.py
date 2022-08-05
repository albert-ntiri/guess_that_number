import pytest
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.tests.tests_setup import objects_fake_global_dict
from main.game.improvement import *
from main.resources.infrastructure.data import FeedbackHintType
import pandas as pd



### Object Manager Setup

objects_fake_global = objects_fake_global_dict["game_level"]



### Improvement Tests

@pytest.fixture
def improvement_copy():
    games = objects_fake_global.get_object("games")
    games.add_game()
    games._current_game._outcome = "lose"
    feedback_df = games._current_game._feedback.get_feedback_df()
    feedback_df.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    feedback_df.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    feedback_df.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    feedback_df.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    feedback_df.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    
    data = objects_fake_global.get_object("data")
    hints_obj = data.get_data_object("hint_types")
    yield Improvement(objects_fake_global, hints_obj)
    
    games._games = []
    feedback_df = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])

@pytest.fixture
def improvement_copy_multiple_games():
    games = objects_fake_global.get_object("games")
    for i in range(2):
        games.add_game()
        games._current_game._outcome = "lose"
    feedback_df = games._current_game._feedback.get_feedback_df()
    feedback_df.loc[1] = ["multiple", "Nice try!  Hint: 2 is a multiple.", "3", "bad"]
    feedback_df.loc[2] = ["multiple", "Nice try!  Hint: 3 is a multiple.", "5", "bad"]
    feedback_df.loc[3] = ["perfect_cube", "Nice try!  Hint: It is a perfect cube.", "4", "bad"]
    feedback_df.loc[4] = ["even_odd", "Nice try!  Hint: It is an odd number.", "3", "good"]
    feedback_df.loc[5] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "6", "bad"]
    games._aggregate_feedback = feedback_df.copy()
    games._aggregate_feedback.loc[6] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "8", "bad"]
    games._aggregate_feedback.loc[7] = ["perfect_square", "Nice try!  Hint: It is a perfect square.", "2", "bad"]
    
    data = objects_fake_global.get_object("data")
    hints_obj = data.get_data_object("hint_types")
    yield Improvement(objects_fake_global, hints_obj)
    
    games._games = []
    feedback_df = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])


# Test _get_feedback_component method
def test_get_feedback_component_general(improvement_copy):
    expected_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    assert expected_feedback == improvement_copy._get_feedback_component("general", "multiples")

def test_get_feedback_component_example(improvement_copy):
    expected_feedback = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    assert expected_feedback == improvement_copy._get_feedback_component("example", "3", "Nice try!  Hint: 2 is a multiple.")

def test_get_feedback_component_description(improvement_copy):
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    expected_feedback = f"Remember:\n{imp_area_desc}"
    assert expected_feedback == improvement_copy._get_feedback_component("description", imp_area_desc)

def test_get_feedback_component_no_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_feedback_component()


# Test _get_example_feedback method
def test_get_example_feedback_one_ex(improvement_copy):
    expected_feedback = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    assert expected_feedback == improvement_copy._get_example_feedback([["3", "Nice try!  Hint: 2 is a multiple."]])

def test_get_example_feedback_multiple_examples(improvement_copy):
    examples = [["3", "Nice try!  Hint: 2 is a multiple."], ["5", "Nice try!  Hint: 2 is a multiple."]]
    expected_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    expected_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    expected_feedback = expected_feedback1 + "\n" + expected_feedback2
    assert expected_feedback == improvement_copy._get_example_feedback(examples)

def test_get_example_feedback_no_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_example_feedback()

def test_get_example_feedback_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_example_feedback("", "extra")


# Test _get_ranked_improvement_areas method
def test_get_ranked_improvement_areas_current(improvement_copy):
    expected_list = ["multiple", "perfect_square"]
    assert expected_list == improvement_copy._get_ranked_improvement_areas()

def test_get_ranked_improvement_areas_aggregate(improvement_copy_multiple_games):
    expected_list = ["perfect_square", "multiple"]
    assert expected_list == improvement_copy_multiple_games._get_ranked_improvement_areas(current=False)

def test_get_ranked_improvement_areas_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_ranked_improvement_areas(current=False, extra="no")


# Test _get_top_improvement_area method
def test_get_top_improvement_area_one_game(improvement_copy):
    assert "multiple" == improvement_copy._get_top_improvement_area()

def test_get_top_improvement_area_multiple_games(improvement_copy_multiple_games):
    assert "perfect_square" == improvement_copy_multiple_games._get_top_improvement_area()

def test_get_top_improvement_area_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_top_improvement_area("extra")


# Test get_improvement_area_id method
def test_get_improvement_area_id_one_game(improvement_copy):
    assert 2 == improvement_copy.get_improvement_area_id()

def test_get_improvement_area_id_multiple_games(improvement_copy_multiple_games):
    assert 5 == improvement_copy_multiple_games.get_improvement_area_id()

def test_get_improvement_area_id_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy.get_improvement_area_id("extra")


# Test _get_imp_area_display_name method
def test_get_imp_area_display_name_one_game(improvement_copy):
    assert "multiples" == improvement_copy._get_imp_area_display_name()

def test_get_imp_area_display_name_multiple_games(improvement_copy_multiple_games):
    assert "perfect squares" == improvement_copy_multiple_games._get_imp_area_display_name()

def test_get_imp_area_display_name_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_imp_area_display_name("extra")


# Test _get_examples method
def test_get_examples_one_game(improvement_copy):
    expected_examples = [["3", "Nice try!  Hint: 2 is a multiple."], ["5", "Nice try!  Hint: 3 is a multiple."]]
    assert expected_examples == improvement_copy._get_examples()

def test_get_examples_multiple_games(improvement_copy_multiple_games):
    expected_examples = [["6", "Nice try!  Hint: It is a perfect square."]]
    assert expected_examples == improvement_copy_multiple_games._get_examples()

def test_get_examples_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_examples("extra")


# Test _get_all_feedback_parts method
def test_get_all_feedback_parts_one_game(improvement_copy):
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    feedback_parts = (general_feedback, example_feedback, description_feedback)
    
    assert feedback_parts == improvement_copy._get_all_feedback_parts()

def test_get_all_feedback_parts_multiple_games(improvement_copy_multiple_games):
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: perfect squares."
    
    example_feedback = 'Your guess, 6, did not match the hint: "Nice try!  Hint: It is a perfect square."'
    
    imp_area_desc = "Perfect Square: Any number that is the square of a rational number. For example, 0, 1, 4, 9, 16, 25, etc. are all perfect squares. So are and ."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    feedback_parts = (general_feedback, example_feedback, description_feedback)
    
    assert feedback_parts == improvement_copy_multiple_games._get_all_feedback_parts()

def test_get_all_feedback_parts_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy._get_all_feedback_parts("extra")


# Test get_feedback method
def test_get_feedback_one_game(improvement_copy):
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: multiples."
    
    example_feedback1 = 'Your guess, 3, did not match the hint: "Nice try!  Hint: 2 is a multiple."'
    example_feedback2 = 'Your guess, 5, did not match the hint: "Nice try!  Hint: 3 is a multiple."'
    example_feedback = example_feedback1 + "\n" + example_feedback2
    
    imp_area_desc = "Multiple: The\xa0result\xa0of\xa0multiplying a number by an integer (not by a fraction)."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    assert expected_feedback == improvement_copy.get_feedback()

def test_get_feedback_multiple_games(improvement_copy_multiple_games):
    general_feedback = "Feedback:\nSome of your guesses did not match the hints.  For example: perfect squares."
    
    example_feedback = 'Your guess, 6, did not match the hint: "Nice try!  Hint: It is a perfect square."'
    
    imp_area_desc = "Perfect Square: Any number that is the square of a rational number. For example, 0, 1, 4, 9, 16, 25, etc. are all perfect squares. So are and ."
    description_feedback = f"Remember:\n{imp_area_desc}"
    
    expected_feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
    
    assert expected_feedback == improvement_copy_multiple_games.get_feedback()

def test_get_feedback_too_many_arguments_raises_error(improvement_copy):
    with pytest.raises(TypeError):
        improvement_copy.get_feedback("extra")



