import pytest
from main.tests.tests_setup import objects_fake_global_dict
from main.resources.infrastructure.data import *

from main.tests.test_concepts import factor_main_hint, factor_factor_hint, factor_digit_hint
from main.tests.test_concepts import multiple_main_hint
from main.tests.test_concepts import prime_main_hint, prime_factor_hint, prime_digit_hint
from main.tests.test_concepts import even_odd_main_hint, even_odd_digit_hint
from main.tests.test_concepts import perfect_square_main_hint, perfect_square_digit_hint
from main.tests.test_concepts import perfect_cube_main_hint, perfect_cube_digit_hint
from main.tests.test_concepts import digit_sum_main_hint
from main.tests.test_concepts import digit_length_main_hint



##### Individual Data Objects


### DataPoint Tests

@pytest.fixture
def data_point_stub():
    return DataPoint("test", 1)


# Test get_name method
def test_get_name(data_point_stub):
    assert "test" == data_point_stub.get_name()

def test_get_name_too_many_arguments_raises_error(data_point_stub):
    with pytest.raises(TypeError):
        data_point_stub.get_name("extra")


# Test get_id method
def test_get_id(data_point_stub):
    assert 1 == data_point_stub.get_id()

def test_get_id_too_many_arguments_raises_error(data_point_stub):
    with pytest.raises(TypeError):
        data_point_stub.get_id("extra")


# Test _get_data_point_info method
def test_get_data_point_info_data_point(data_point_stub):
    assert (1, "test") == data_point_stub._get_data_point_info()

def test_get_data_point_info_data_point_too_many_arguments_raises_error(data_point_stub):
    with pytest.raises(TypeError):
        data_point_stub._get_data_point_info("extra")



### Level Tests

@pytest.fixture
def level_stub():
    return Level("test", 1, (5, 9), 2)


# Test get_number_range method
def test_get_number_range(level_stub):
    assert (5, 9) == level_stub.get_number_range()

def test_get_number_range_too_many_arguments_raises_error(level_stub):
    with pytest.raises(TypeError):
        level_stub.get_number_range("extra")


# Test get_penalty method
def test_get_penalty(level_stub):
    assert 2 == level_stub.get_penalty()

def test_get_penalty_too_many_arguments_raises_error(level_stub):
    with pytest.raises(TypeError):
        level_stub.get_penalty("extra")



### Error Tests

@pytest.fixture
def error_stub():
    error = Error("test", 1, "test error message")
    error._category = "test category"
    return error


# Test get_category method
def test_get_category_error(error_stub):
    assert "test category" == error_stub.get_category()

def test_get_category_error_too_many_arguments_raises_error(error_stub):
    with pytest.raises(TypeError):
        error_stub.get_category("extra")


# Test get_message method
def test_get_message_error(error_stub):
    assert "test error message" == error_stub.get_message()

def test_get_message_error_too_many_arguments_raises_error(error_stub):
    with pytest.raises(TypeError):
        error_stub.get_message("extra")


# Test _get_data_point_info method
def test_get_data_point_info_error(error_stub):
    assert (1, "test category", "test") == error_stub._get_data_point_info()

def test_get_data_point_info_error_too_many_arguments_raises_error(error_stub):
    with pytest.raises(TypeError):
        error_stub._get_data_point_info("extra")



### HintType Tests

@pytest.fixture
def hint_type_stub():
    return HintType("test", 1, "test description", "test main hint", "test hint display name")


# Test get_description method
def test_get_description(hint_type_stub):
    assert "test description" == hint_type_stub.get_description()

def test_get_description_too_many_arguments_raises_error(hint_type_stub):
    with pytest.raises(TypeError):
        hint_type_stub.get_description("extra")


# Test get_main_hint method
def test_get_main_hint(hint_type_stub):
    assert "test main hint" == hint_type_stub.get_main_hint()

def test_get_main_hint_too_many_arguments_raises_error(hint_type_stub):
    with pytest.raises(TypeError):
        hint_type_stub.get_main_hint("extra")


# Test get_hint_display_name method
def test_get_hint_display_name(hint_type_stub):
    assert "test hint display name" == hint_type_stub.get_hint_display_name()

def test_get_hint_display_name_too_many_arguments_raises_error(hint_type_stub):
    with pytest.raises(TypeError):
        hint_type_stub.get_hint_display_name("extra")


# Test _get_data_point_info method
def test_get_data_point_info_hint_type(hint_type_stub):
    assert (1, "test", "test description") == hint_type_stub._get_data_point_info()

def test_get_data_point_info_hint_type_too_many_arguments_raises_error(hint_type_stub):
    with pytest.raises(TypeError):
        hint_type_stub._get_data_point_info("extra")



### FeedbackHintType Tests

@pytest.fixture
def feedback_hint_type_stub():
    return FeedbackHintType("test", 1, "test description", "test main hint", "test hint display name", "test feedback display name")


# Test get_feedback_display_name method
def test_get_feedback_display_name(feedback_hint_type_stub):
    assert "test feedback display name" == feedback_hint_type_stub.get_feedback_display_name()

def test_get_feedback_display_name_too_many_arguments_raises_error(feedback_hint_type_stub):
    with pytest.raises(TypeError):
        feedback_hint_type_stub.get_feedback_display_name("extra")



### GameOutcome Tests

@pytest.fixture
def game_outcome_stub():
    return GameOutcome("test", 1, "test outcome message")


# Test get_message method
def test_get_message_game_outcome(game_outcome_stub):
    assert "test outcome message" == game_outcome_stub.get_message()

def test_get_message_game_outcome_too_many_arguments_raises_error(game_outcome_stub):
    with pytest.raises(TypeError):
        game_outcome_stub.get_message("extra")



### SuccessfulOutcome Tests

@pytest.fixture
def successful_outcome_stub():
    outcome_stub = SuccessfulOutcome("test", 1, "test outcome message: score - {}")
    yield outcome_stub
    outcome_stub.message = "test outcome message: score - {}"


# Test score property
def test_score_property_default_score(successful_outcome_stub):
    assert None == successful_outcome_stub.score

def test_score_property_updated_score(successful_outcome_stub):
    successful_outcome_stub.score = 75
    assert 75 == successful_outcome_stub.score

def test_score_property_updated_message(successful_outcome_stub):
    successful_outcome_stub.score = 80
    assert "test outcome message: score - 80" == successful_outcome_stub.get_message()



##### Manager Data Objects

@pytest.fixture
def data_copy():
    objects_fake_global_easy = objects_fake_global_dict["easy"]
    return objects_fake_global_easy.get_object("data")


### LevelOfDifficultyTypes Tests

@pytest.fixture
def levels(data_copy):
    return data_copy._levels


# Test get_level_obj method
def test_get_level_obj_easy(levels):
    easy_level = levels.get_level_obj("easy")
    assert "easy" == easy_level.get_name()

def test_get_level_obj_medium(levels):
    medium_level = levels.get_level_obj("medium")
    assert "medium" == medium_level.get_name()

def test_get_level_obj_hard(levels):
    hard_level = levels.get_level_obj("hard")
    assert "hard" == hard_level.get_name()

def test_get_level_obj_custom(levels):
    custom_level = levels.get_level_obj("custom")
    assert "custom" == custom_level.get_name()

def test_get_level_obj_not_found(levels):
    assert None == levels.get_level_obj("eazy")

def test_get_level_obj_no_arguments_raises_error(levels):
    with pytest.raises(TypeError):
        levels.get_level_obj()

def test_get_level_obj_too_many_arguments_raises_error(levels):
    with pytest.raises(TypeError):
        levels.get_level_obj("easy", "extra")


# Test get_category method
def test_get_category_level_types(levels):
    assert "levels" == levels.get_category()

def test_get_category_level_types_too_many_arguments_raises_error(levels):
    with pytest.raises(TypeError):
        levels.get_category("extra")



### ErrorTypes Tests

@pytest.fixture
def errors(data_copy):
    return data_copy._errors


# Test _create_error_obj method
def test_create_error_obj(errors):
    error_stub = errors._create_error_obj(GuessEntryError, "non_integer", 7)
    assert 7 == error_stub.get_id()

def test_create_error_obj_no_arguments_raises_error(errors):
    with pytest.raises(TypeError):
        errors._create_error_obj()

def test_create_error_obj_too_many_arguments_raises_error(errors):
    with pytest.raises(TypeError):
        errors._create_error_obj(GuessEntryError, "new", 7, "extra")


# Test get_error_obj method
def test_get_error_obj_comparison(errors):
    comparison_error = errors.get_error_obj("comparison")
    assert "comparison" == comparison_error.get_name()

def test_get_error_obj_missing(errors):
    missing_error = errors.get_error_obj("missing")
    assert "missing" == missing_error.get_name()

def test_get_error_obj_invalid(errors):
    invalid_error = errors.get_error_obj("invalid")
    assert "invalid" == invalid_error.get_name()

def test_get_error_obj_non_integer(errors):
    non_integer_error = errors.get_error_obj("non_integer")
    assert "non_integer" == non_integer_error.get_name()

def test_get_error_obj_out_of_range(errors):
    out_of_range_error = errors.get_error_obj("out_of_range")
    assert "out_of_range" == out_of_range_error.get_name()

def test_get_error_obj_not_found(errors):
    assert None == errors.get_error_obj("mising")

def test_get_error_obj_no_arguments_raises_error(errors):
    with pytest.raises(TypeError):
        errors.get_error_obj()

def test_get_error_obj_too_many_arguments_raises_error(errors):
    with pytest.raises(TypeError):
        errors.get_error_obj("missing", "extra")


# Test get_category method
def test_get_category_error_types(errors):
    assert "errors" == errors.get_category()

def test_get_category_error_types_too_many_arguments_raises_error(errors):
    with pytest.raises(TypeError):
        errors.get_category("extra")



### HintTypes Tests

@pytest.fixture
def hints(data_copy):
    return data_copy._hints


# Test _create_hint_obj method
def test_create_hint_obj_no_feedback(hints):
    hint_stub = hints._create_hint_obj(NoFeedbackHintType, "greater_less", 10, "Higher|Lower")
    assert 10 == hint_stub.get_id()

def test_create_hint_obj_feedback(hints):
    hint_stub = hints._create_hint_obj(FeedbackHintType, "multiple", 10, "multiple", "my feedback")
    assert "my feedback" == hint_stub.get_feedback_display_name()

def test_create_hint_obj_no_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints._create_hint_obj()

def test_create_hint_obj_too_many_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints._create_hint_obj(FeedbackHintType, "multiple", 10, "multiple", "my feedback", "extra")


# Test get_hint_obj_from_hint_type method
def test_get_hint_obj_from_hint_type_factor(hints):
    factor_hint = hints.get_hint_obj_from_hint_type("factor")
    assert "factor" == factor_hint.get_name()

def test_get_hint_obj_from_hint_type_multiple(hints):
    multiple_hint = hints.get_hint_obj_from_hint_type("multiple")
    assert "multiple" == multiple_hint.get_name()

def test_get_hint_obj_from_hint_type_prime(hints):
    prime_hint = hints.get_hint_obj_from_hint_type("prime")
    assert "prime" == prime_hint.get_name()

def test_get_hint_obj_from_hint_type_even_odd(hints):
    even_odd_hint = hints.get_hint_obj_from_hint_type("even_odd")
    assert "even_odd" == even_odd_hint.get_name()

def test_get_hint_obj_from_hint_type_perfect_square(hints):
    perfect_square_hint = hints.get_hint_obj_from_hint_type("perfect_square")
    assert "perfect_square" == perfect_square_hint.get_name()

def test_get_hint_obj_from_hint_type_perfect_cube(hints):
    perfect_cube_hint = hints.get_hint_obj_from_hint_type("perfect_cube")
    assert "perfect_cube" == perfect_cube_hint.get_name()

def test_get_hint_obj_from_hint_type_digit_sum(hints):
    digit_sum_hint = hints.get_hint_obj_from_hint_type("digit_sum")
    assert "digit_sum" == digit_sum_hint.get_name()

def test_get_hint_obj_from_hint_type_digit_length(hints):
    digit_length_hint = hints.get_hint_obj_from_hint_type("digit_length")
    assert "digit_length" == digit_length_hint.get_name()

def test_get_hint_obj_from_hint_type_greater_less(hints):
    greater_less_hint = hints.get_hint_obj_from_hint_type("greater_less")
    assert "greater_less" == greater_less_hint.get_name()

def test_get_hint_obj_from_hint_type_not_found(hints):
    assert None == hints.get_hint_obj_from_hint_type("factors")

def test_get_hint_obj_from_hint_type_no_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints.get_hint_obj_from_hint_type()

def test_get_hint_obj_from_hint_type_too_many_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints.get_hint_obj_from_hint_type("factor", "extra")


# Test get_hint_obj_from_hint method
def test_get_hint_obj_from_hint_factor_main_hint(hints, factor_main_hint):
    factor_hint = hints.get_hint_obj_from_hint(factor_main_hint)
    assert "factor" == factor_hint.get_name()

def test_get_hint_obj_from_hint_factor_factor_hint(hints, factor_factor_hint):
    factor_hint = hints.get_hint_obj_from_hint(factor_factor_hint)
    assert "factor" == factor_hint.get_name()

def test_get_hint_obj_from_hint_factor_digit_hint(hints, factor_digit_hint):
    factor_hint = hints.get_hint_obj_from_hint(factor_digit_hint)
    assert "factor" == factor_hint.get_name()

def test_get_hint_obj_from_hint_multiple_main_hint(hints, multiple_main_hint):
    multiple_hint = hints.get_hint_obj_from_hint(multiple_main_hint)
    assert "multiple" == multiple_hint.get_name()

def test_get_hint_obj_from_hint_prime_main_hint(hints, prime_main_hint):
    prime_hint = hints.get_hint_obj_from_hint(prime_main_hint)
    assert "prime" == prime_hint.get_name()

def test_get_hint_obj_from_hint_prime_factor_hint(hints, prime_factor_hint):
    prime_hint = hints.get_hint_obj_from_hint(prime_factor_hint)
    assert "prime" == prime_hint.get_name()

def test_get_hint_obj_from_hint_prime_digit_hint(hints, prime_digit_hint):
    prime_hint = hints.get_hint_obj_from_hint(prime_digit_hint)
    assert "prime" == prime_hint.get_name()

def test_get_hint_obj_from_hint_even_odd_main_hint(hints, even_odd_main_hint):
    even_odd_hint = hints.get_hint_obj_from_hint(even_odd_main_hint)
    assert "even_odd" == even_odd_hint.get_name()

def test_get_hint_obj_from_hint_even_odd_digit_hint(hints, even_odd_digit_hint):
    even_odd_hint = hints.get_hint_obj_from_hint(even_odd_digit_hint)
    assert "even_odd" == even_odd_hint.get_name()

def test_get_hint_obj_from_hint_perfect_square_main_hint(hints, perfect_square_main_hint):
    perfect_square_hint = hints.get_hint_obj_from_hint(perfect_square_main_hint)
    assert "perfect_square" == perfect_square_hint.get_name()

def test_get_hint_obj_from_hint_perfect_square_digit_hint(hints, perfect_square_digit_hint):
    perfect_square_hint = hints.get_hint_obj_from_hint(perfect_square_digit_hint)
    assert "perfect_square" == perfect_square_hint.get_name()

def test_get_hint_obj_from_hint_perfect_cube_main_hint(hints, perfect_cube_main_hint):
    perfect_cube_hint = hints.get_hint_obj_from_hint(perfect_cube_main_hint)
    assert "perfect_cube" == perfect_cube_hint.get_name()

def test_get_hint_obj_from_hint_perfect_cube_digit_hint(hints, perfect_cube_digit_hint):
    perfect_cube_hint = hints.get_hint_obj_from_hint(perfect_cube_digit_hint)
    assert "perfect_cube" == perfect_cube_hint.get_name()

def test_get_hint_obj_from_hint_digit_sum_main_hint(hints, digit_sum_main_hint):
    digit_sum_hint = hints.get_hint_obj_from_hint(digit_sum_main_hint)
    assert "digit_sum" == digit_sum_hint.get_name()

def test_get_hint_obj_from_hint_digit_length_main_hint(hints, digit_length_main_hint):
    digit_length_hint = hints.get_hint_obj_from_hint(digit_length_main_hint)
    assert "digit_length" == digit_length_hint.get_name()

def test_get_hint_obj_from_hint_no_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints.get_hint_obj_from_hint()

def test_get_hint_obj_from_hint_too_many_arguments_raises_error(hints, digit_length_main_hint):
    with pytest.raises(TypeError):
        hints.get_hint_obj_from_hint(digit_length_main_hint, "extra")


# Test get_feedback_display_name method
feedback_display_names = [
    ("factor", "factors"),
    ("multiple", "multiples"),
    ("prime", "prime numbers"),
    ("even_odd", "even/odd numbers"),
    ("perfect_square", "perfect squares"),
    ("perfect_cube", ""),
    ("digit_sum", "digit sums"),
    ("digit_length", "n-digit numbers"),
    ("greater_less", "")
    ]

@pytest.mark.parametrize("hint_type, display_name", feedback_display_names)
def test_get_feedback_display_name(hints, hint_type, display_name):
    assert display_name == hints.get_feedback_display_name(hint_type)

def test_get_feedback_display_name_no_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints.get_feedback_display_name()

def test_get_feedback_display_name_too_many_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints.get_feedback_display_name("factor", "extra")


# Test get_category method
def test_get_category_hint_types(hints):
    assert "hints" == hints.get_category()

def test_get_category_hint_types_too_many_arguments_raises_error(hints):
    with pytest.raises(TypeError):
        hints.get_category("extra")



### OutcomeTypes Tests

@pytest.fixture
def outcomes(data_copy):
    return data_copy._outcomes


# Test _create_outcome_obj method
def test_create_outcome_obj(outcomes):
    outcome_stub = outcomes._create_outcome_obj(UnsuccessfulOutcome, "quit", 4)
    assert 4 == outcome_stub.get_id()

def test_create_outcome_obj_no_arguments_raises_error(outcomes):
    with pytest.raises(TypeError):
        outcomes._create_outcome_obj()

def test_create_outcome_obj_too_many_arguments_raises_error(outcomes):
    with pytest.raises(TypeError):
        outcomes._create_outcome_obj(UnsuccessfulOutcome, "quit", 4, "extra")


# Test get_outcome_obj method
def test_get_outcome_obj_win(outcomes):
    win_outcome = outcomes.get_outcome_obj("win")
    assert "win" == win_outcome.get_name()

def test_get_outcome_obj_lose(outcomes):
    lose_outcome = outcomes.get_outcome_obj("lose")
    assert "lose" == lose_outcome.get_name()

def test_get_outcome_obj_quit(outcomes):
    quit_outcome = outcomes.get_outcome_obj("quit")
    assert "quit" == quit_outcome.get_name()

def test_get_outcome_obj_not_found(outcomes):
    assert None == outcomes.get_outcome_obj("loose")

def test_get_outcome_obj_no_arguments_raises_error(outcomes):
    with pytest.raises(TypeError):
        outcomes.get_outcome_obj()

def test_get_outcome_obj_too_many_arguments_raises_error(outcomes):
    with pytest.raises(TypeError):
        outcomes.get_outcome_obj("win", "extra")


# Test get_category method
def test_get_category_outcome_types(outcomes):
    assert "outcomes" == outcomes.get_category()

def test_get_category_outcome_types_too_many_arguments_raises_error(outcomes):
    with pytest.raises(TypeError):
        outcomes.get_category("extra")


# Test reset method
def test_reset_outcome_types_set_score(outcomes):
    outcomes._win.score = 75
    assert 75 == outcomes._win.score

def test_reset_outcome_types_reset_score(outcomes):
    outcomes._win.score = 75
    outcomes.reset()
    assert None == outcomes._win.score

def test_reset_outcome_types_set_message(outcomes):
    outcomes._win.score = 75
    msg = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 75\n\n\nThanks for playing! Please come back soon."
    assert msg == outcomes._win.get_message()

def test_reset_outcome_types_reset_message(outcomes):
    outcomes._win.score = 75
    outcomes.reset()
    msg = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: {}\n\n\nThanks for playing! Please come back soon."
    assert msg == outcomes._win.get_message()

def test_reset_outcome_types_too_many_arguments_raises_error(outcomes):
    with pytest.raises(TypeError):
        outcomes.reset("extra")



### DataManager Tests


# Test get_data_object method
def test_get_data_object_levels(data_copy):
    data_object = data_copy.get_data_object("level_of_difficulty_types")
    assert "levels" == data_object.get_category()

def test_get_data_object_errors(data_copy):
    data_object = data_copy.get_data_object("error_types")
    assert "errors" == data_object.get_category()

def test_get_data_object_hints(data_copy):
    data_object = data_copy.get_data_object("hint_types")
    assert "hints" == data_object.get_category()

def test_get_data_object_outcomes(data_copy):
    data_object = data_copy.get_data_object("outcome_types")
    assert "outcomes" == data_object.get_category()

def test_get_data_object_not_found(data_copy):
    with pytest.raises(KeyError):
        data_copy.get_data_object("level_types")

def test_get_data_object_no_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.get_data_object()

def test_get_data_object_too_many_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.get_data_object("hint_types", "extra")


# Test get_sub_data_object method
def test_get_sub_data_object_levels(data_copy):
    sub_data_object = data_copy.get_sub_data_object("levels", "easy")
    assert "easy" == sub_data_object.get_name()

def test_get_sub_data_object_errors(data_copy):
    sub_data_object = data_copy.get_sub_data_object("errors", "comparison")
    assert "comparison" == sub_data_object.get_name()

def test_get_sub_data_object_hints(data_copy):
    sub_data_object = data_copy.get_sub_data_object("hints", "factor")
    assert "factor" == sub_data_object.get_name()

def test_get_sub_data_object_outcomes(data_copy):
    sub_data_object = data_copy.get_sub_data_object("outcomes", "win")
    assert "win" == sub_data_object.get_name()

def test_get_sub_data_object_category_not_found(data_copy):
    assert None == data_copy.get_sub_data_object("hint_types", "factor")

def test_get_sub_data_object_no_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.get_sub_data_object()

def test_get_sub_data_object_too_many_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.get_sub_data_object("outcome_types", "win", "extra")


# Test get_type_list method
def test_get_type_list_levels(data_copy):
    type_list = data_copy.get_type_list("levels")
    assert (1, "easy") == type_list[0]

def test_get_type_list_errors(data_copy):
    type_list = data_copy.get_type_list("errors")
    assert (1, "range_entry", "comparison") == type_list[0]

def test_get_type_list_hints(data_copy):
    type_list = data_copy.get_type_list("hints")
    assert (9, "greater_less", "greater_less") == type_list[-1]

def test_get_type_list_outcomes(data_copy):
    type_list = data_copy.get_type_list("outcomes")
    assert (1, "win") == type_list[0]

def test_get_type_list_not_found(data_copy):
    assert None == data_copy.get_type_list("hint_types")

def test_get_type_list_no_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.get_type_list()

def test_get_type_list_too_many_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.get_type_list("errors", "extra")


# Test get_hint_obj_from_hint method
def test_get_hint_obj_from_hint_data_manager(data_copy, factor_main_hint):
    factor_hint = data_copy.get_hint_obj_from_hint(factor_main_hint)
    assert "factor" == factor_hint.get_name()

def test_get_hint_obj_from_hint_data_manager_no_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.get_hint_obj_from_hint()

def test_get_hint_obj_from_hint_data_manager_too_many_arguments_raises_error(data_copy, factor_main_hint):
    with pytest.raises(TypeError):
        data_copy.get_hint_obj_from_hint(factor_main_hint, "extra")


# Test reset method
def test_reset_data_manager_set_score(data_copy):
    data_copy._outcomes._win.score = 75
    assert 75 == data_copy._outcomes._win.score

def test_reset_data_manager_reset_score(data_copy):
    data_copy._outcomes._win.score = 75
    data_copy.reset()
    assert None == data_copy._outcomes._win.score

def test_reset_data_manager_set_message(data_copy):
    data_copy._outcomes._win.score = 75
    msg = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: 75\n\n\nThanks for playing! Please come back soon."
    assert msg == data_copy._outcomes._win.get_message()

def test_reset_data_manager_reset_message(data_copy):
    data_copy._outcomes._win.score = 75
    data_copy.reset()
    msg = "That's correct! Congratulations! You are a winner!!!\n\nYour Score: {}\n\n\nThanks for playing! Please come back soon."
    assert msg == data_copy._outcomes._win.get_message()

def test_reset_data_manager_too_many_arguments_raises_error(data_copy):
    with pytest.raises(TypeError):
        data_copy.reset("extra")


