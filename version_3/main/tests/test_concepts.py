import pytest
from main.tests.tests_setup import objects_fake_global_dict
from main.resources.infrastructure.number import Number
from main.resources.infrastructure.data import DataManager
from main.resources.infrastructure.application_text import TextManager
from main.tests.test_db import sqlite_db_fake, test_db_path
from resources.variables.create_db_queries import non_type_tables

from main.concepts.hints import *
from main.concepts.math_concept import MathConcept
from concepts.concept_manager import ConceptManager



### Object Manager Setup

objects_fake_global_easy = objects_fake_global_dict["easy"]
numbers = objects_fake_global_easy.get_object("numbers")
data = objects_fake_global_easy.get_object("data")


### Concept Component Tests

# Test get_hint_template method
def test_get_hint_template_main():
    test_hint_object = Hint()
    assert "Nice try!  Hint: " == test_hint_object.get_hint_template()

def test_get_hint_template_too_many_arguments_raises_error():
    test_hint_object = Hint()
    with pytest.raises(TypeError):
        test_hint_object.get_hint_template("extra")


# Test _get_factor_hint method
class FactorHintStub(FactorHint):
    def _satisfies_condition(self):
        pass

def test_get_factor_hint_main():
    test_factor_hint_object = FactorHintStub()
    assert "Nice try!  Hint: It has {} factor(s)." == test_factor_hint_object._get_factor_hint()

def test_get_factor_hint_too_many_arguments_raises_error():
    test_factor_hint_object = FactorHintStub()
    with pytest.raises(TypeError):
        test_factor_hint_object._get_factor_hint("extra")


# Test _get_count_based_hint method
class DigitHintStub(DigitHint):
    def _satisfies_condition(self):
        pass

@pytest.fixture
def test_digit_hint_object():
    return DigitHintStub()

def test_get_count_based_hint_none(test_digit_hint_object):
    assert "Nice try!  Hint: None of its digits are {}s." == test_digit_hint_object._get_count_based_hint(2, 0)

def test_get_count_based_hint_one(test_digit_hint_object):
    assert "Nice try!  Hint: 1 of its digits is a {}." == test_digit_hint_object._get_count_based_hint(3, 1)

def test_get_count_based_hint_all(test_digit_hint_object):
    assert "Nice try!  Hint: All of its digits are {}s." == test_digit_hint_object._get_count_based_hint(2, 2)

def test_get_count_based_hint_specific_number(test_digit_hint_object):
    assert "Nice try!  Hint: 2 of its digits are {}s." == test_digit_hint_object._get_count_based_hint(3, 2)

def test_get_count_based_hint_invalid_high(test_digit_hint_object):
    assert None == test_digit_hint_object._get_count_based_hint(2, 3)

def test_get_count_based_hint_invalid_low(test_digit_hint_object):
    assert None == test_digit_hint_object._get_count_based_hint(2, -1)

def test_get_count_based_hint_invalid_decimal(test_digit_hint_object):
    assert None == test_digit_hint_object._get_count_based_hint(2, 1.5)

def test_get_count_based_hint_no_arguments_raises_error(test_digit_hint_object):
    with pytest.raises(TypeError):
        test_digit_hint_object._get_count_based_hint()

def test_get_count_based_hint_too_many_arguments_raises_error(test_digit_hint_object):
    with pytest.raises(TypeError):
        test_digit_hint_object._get_count_based_hint(1, 1, "extra")


# Test _pattern_match method
@pytest.fixture
def math_concept():
    return MathConcept(10, numbers, data)

@pytest.fixture
def number_pattern():
    return r"\d+"

@pytest.fixture
def none_pattern():
    return "None"

@pytest.fixture
def digits_pattern():
    return "digits"

def test_pattern_match_number_beginning(math_concept, number_pattern):
    test_text = "Test text: 1"
    assert '1' == math_concept._pattern_match(number_pattern, test_text, value=True)

def test_pattern_match_number_end(math_concept, number_pattern):
    test_text = "2 test text"
    assert '2' == math_concept._pattern_match(number_pattern, test_text, value=True)

def test_pattern_match_number_middle(math_concept, number_pattern):
    test_text = "Test 3 text"
    assert '3' == math_concept._pattern_match(number_pattern, test_text, value=True)

def test_pattern_match_number_dash(math_concept, number_pattern):
    test_text = "Test 4-dash text"
    assert '4' == math_concept._pattern_match(number_pattern, test_text, value=True)

def test_pattern_match_number_multiple_digit(math_concept, number_pattern):
    test_text = "Test 56 text"
    assert '56' == math_concept._pattern_match(number_pattern, test_text, value=True)

def test_pattern_match_number_not_found(math_concept, number_pattern):
    test_text = "Test text"
    assert None == math_concept._pattern_match(number_pattern, test_text, value=True)

def test_pattern_match_none_yes(math_concept, none_pattern):
    test_text = "None test text"
    assert True == math_concept._pattern_match(none_pattern, test_text)

def test_pattern_match_none_no(math_concept, none_pattern):
    test_text = "All test text"
    assert False == math_concept._pattern_match(none_pattern, test_text)

def test_pattern_match_digits_yes(math_concept, digits_pattern):
    test_text = "Test digits text"
    assert True == math_concept._pattern_match(digits_pattern, test_text)

def test_pattern_match_digits_no(math_concept, digits_pattern):
    test_text = "Test text"
    assert False == math_concept._pattern_match(digits_pattern, test_text)

def test_pattern_match_no_arguments_raises_error(math_concept):
    with pytest.raises(TypeError):
        math_concept._pattern_match()

def test_pattern_match_too_many_arguments_raises_error(math_concept, number_pattern):
    test_text = "Test text"
    with pytest.raises(TypeError):
        math_concept._pattern_match(number_pattern, test_text, value=True, extra='no')


# Test _extract_number_from_hint method
def test_extract_number_from_hint_found(math_concept):
    test_text = "Test text: 1"
    assert 1 == math_concept._extract_number_from_hint(test_text)

def test_extract_number_from_hint_not_found(math_concept):
    test_text = "Test text"
    assert None == math_concept._extract_number_from_hint(test_text)

def test_extract_number_from_hint_no_arguments_raises_error(math_concept):
    with pytest.raises(TypeError):
        math_concept._extract_number_from_hint()

def test_extract_number_from_hint_too_many_arguments_raises_error(math_concept):
    test_text = "Test text"
    with pytest.raises(TypeError):
        math_concept._extract_number_from_hint(test_text, "extra")


# Test _get_count_satisfying_condition method
class SatisfiesConditionStubTrue(HintAddOn):
    def _satisfies_condition(self, x=None):
        return True

class SatisfiesConditionStubFalse(HintAddOn):
    def _satisfies_condition(self, x=None):
        return False

class SatisfiesConditionFakeCombo(HintAddOn):
    def _satisfies_condition(self, x=None):
        return True if x <= 5 else False

@pytest.fixture
def test_list_one_to_ten():
    return [i for i in range(1, 11)]

def test_get_count_satisfying_condition_all_meet_condition(test_list_one_to_ten):
    test_object = SatisfiesConditionStubTrue()
    assert 10 == test_object._get_count_satisfying_condition(test_list_one_to_ten)

def test_get_count_satisfying_condition_none_meet_condition(test_list_one_to_ten):
    test_object = SatisfiesConditionStubFalse()
    assert 0 == test_object._get_count_satisfying_condition(test_list_one_to_ten)

def test_get_count_satisfying_condition_some_meet_condition(test_list_one_to_ten):
    test_object = SatisfiesConditionFakeCombo()
    assert 5 == test_object._get_count_satisfying_condition(test_list_one_to_ten)

def test_get_count_satisfying_condition_no_arguments_raises_error(test_list_one_to_ten):
    test_object = SatisfiesConditionFakeCombo()
    with pytest.raises(TypeError):
        test_object._get_count_satisfying_condition()

def test_get_count_satisfying_condition_too_many_arguments_raises_error(math_concept):
    test_object = SatisfiesConditionFakeCombo()
    with pytest.raises(TypeError):
        test_object._get_count_satisfying_condition(test_list_one_to_ten, "extra")


# Test _get_number_count method
def test_get_number_count_digit(math_concept):
    test_text = "Test text: 1"
    assert "1" == math_concept._get_number_count(test_text, number=1)

def test_get_number_count_none(math_concept):
    test_text = "None test text"
    assert "none" == math_concept._get_number_count(test_text)

def test_get_number_count_all(math_concept):
    test_text = "All test text"
    assert "all" == math_concept._get_number_count(test_text)

def test_get_number_count_no_arguments_raises_error(math_concept):
    with pytest.raises(TypeError):
        math_concept._get_number_count()

def test_get_number_count_too_many_arguments_raises_error(math_concept, number_pattern):
    test_text = "Test text"
    with pytest.raises(TypeError):
        math_concept._get_number_count(test_text, number=1, extra='no')


# Test _get_guess_digit_count method
def test_get_guess_digit_count_zero(math_concept):
    assert "none" == math_concept._get_guess_digit_count(0, None)

def test_get_guess_digit_count_equal(math_concept):
    assert "all" == math_concept._get_guess_digit_count(1, 1)

def test_get_guess_digit_count_other(math_concept):
    assert "2" == math_concept._get_guess_digit_count(2, None)

def test_get_guess_digit_count_no_arguments_raises_error(math_concept):
    with pytest.raises(TypeError):
        math_concept._get_guess_digit_count()

def test_get_guess_digit_count_too_many_arguments_raises_error(math_concept, number_pattern):
    with pytest.raises(TypeError):
        math_concept._get_guess_digit_count(1, 1, "extra")



### Specific Concept Tests
@pytest.fixture
def mock_concepts_five():
    return ConceptManager(5, numbers, None, data)

@pytest.fixture
def mock_concepts_twenty_four():
    return ConceptManager(24, numbers, None, data)

@pytest.fixture
def mock_concepts_one():
    return ConceptManager(1, numbers, None, data)

@pytest.fixture
def mock_concepts_zero():
    return ConceptManager(0, numbers, None, data)

@pytest.fixture
def mock_concepts_negative_sixteen():
    return ConceptManager(-16, numbers, None, data)

@pytest.fixture
def mock_concepts_negative_one_thousand():
    return ConceptManager(-1000, numbers, None, data)

@pytest.fixture
def mock_concepts_three_fifty_seven():
    return ConceptManager(357, numbers, None, data)


# Test _get_main_hint method
def test_get_main_hint_factor(mock_concepts_five):
    assert "Nice try!  Hint: It is divisible by {}." == mock_concepts_five._factor._get_main_hint()

def test_get_main_hint_multiple(mock_concepts_five):
    assert "Nice try!  Hint: {} is a multiple." == mock_concepts_five._multiple._get_main_hint()

def test_get_main_hint_prime(mock_concepts_five):
    assert "Nice try!  Hint: It is a prime number." == mock_concepts_five._prime._get_main_hint()

def test_get_main_hint_even_odd(mock_concepts_five):
    assert "Nice try!  Hint: It is an {} number." == mock_concepts_five._even_odd._get_main_hint()

def test_get_main_hint_perfect_square(mock_concepts_five):
    assert "Nice try!  Hint: It is a perfect square." == mock_concepts_five._perfect_square._get_main_hint()

def test_get_main_hint_perfect_cube(mock_concepts_five):
    assert "Nice try!  Hint: It is a perfect cube." == mock_concepts_five._perfect_cube._get_main_hint()

def test_get_main_hint_digit_sum(mock_concepts_five):
    assert "Nice try!  Hint: The sum of its digits is {}." == mock_concepts_five._digit_sum._get_main_hint()

def test_get_main_hint_digit_length(mock_concepts_five):
    assert "Nice try!  Hint: It is a {}-digit number." == mock_concepts_five._digit_length._get_main_hint()

def test_get_main_hint_too_many_arguments_raises_error(mock_concepts_five):
    with pytest.raises(TypeError):
        mock_concepts_five._factor._get_main_hint("extra")


# Test include_concept method
def test_include_concept_factor_yes_positive(mock_concepts_one):
    assert True == mock_concepts_one._factor.include_concept()

def test_include_concept_factor_no_zero(mock_concepts_zero):
    assert False == mock_concepts_zero._factor.include_concept()

def test_include_concept_factor_yes_negative(mock_concepts_negative_sixteen):
    assert True == mock_concepts_negative_sixteen._factor.include_concept()

def test_include_concept_multiple_yes_positive(mock_concepts_five):
    assert True == mock_concepts_five._multiple.include_concept()

def test_include_concept_multiple_no_one(mock_concepts_one):
    assert False == mock_concepts_one._multiple.include_concept()

def test_include_concept_multiple_no_zero(mock_concepts_zero):
    assert False == mock_concepts_zero._multiple.include_concept()

def test_include_concept_multiple_yes_negative(mock_concepts_negative_sixteen):
    assert True == mock_concepts_negative_sixteen._multiple.include_concept()

def test_include_concept_prime_yes_positive(mock_concepts_five):
    assert True == mock_concepts_five._prime.include_concept()

def test_include_concept_prime_yes_zero(mock_concepts_zero):
    assert True == mock_concepts_zero._prime.include_concept()

def test_include_concept_prime_no_negative(mock_concepts_negative_sixteen):
    assert False == mock_concepts_negative_sixteen._prime.include_concept()

def test_include_concept_even_odd_positive_yes_one_digit(mock_concepts_five):
    assert True == mock_concepts_five._even_odd.include_concept()

def test_include_concept_even_odd_positive_no_three_digits(mock_concepts_three_fifty_seven):
    assert False == mock_concepts_three_fifty_seven._even_odd.include_concept()

def test_include_concept_even_odd_negative_yes_two_digits(mock_concepts_negative_sixteen):
    assert True == mock_concepts_negative_sixteen._even_odd.include_concept()

def test_include_concept_even_odd_negative_no_four_digits(mock_concepts_negative_one_thousand):
    assert False == mock_concepts_negative_one_thousand._even_odd.include_concept()

def test_include_concept_perfect_square_yes_positive(mock_concepts_five):
    assert True == mock_concepts_five._perfect_square.include_concept()

def test_include_concept_perfect_square_yes_zero(mock_concepts_zero):
    assert True == mock_concepts_zero._perfect_square.include_concept()

def test_include_concept_perfect_square_no_negative(mock_concepts_negative_sixteen):
    assert False == mock_concepts_negative_sixteen._perfect_square.include_concept()

def test_include_concept_perfect_cube_yes_positive(mock_concepts_five):
    assert True == mock_concepts_five._perfect_cube.include_concept()

def test_include_concept_perfect_cube_yes_zero(mock_concepts_zero):
    assert True == mock_concepts_zero._perfect_cube.include_concept()

def test_include_concept_perfect_cube_yes_negative(mock_concepts_negative_sixteen):
    assert True == mock_concepts_negative_sixteen._perfect_cube.include_concept()

def test_include_concept_digit_sum_no_single_digit(mock_concepts_five):
    assert False == mock_concepts_five._digit_sum.include_concept()

def test_include_concept_digit_sum_yes_positive(mock_concepts_twenty_four):
    assert True == mock_concepts_twenty_four._digit_sum.include_concept()

def test_include_concept_digit_sum_yes_negative(mock_concepts_negative_sixteen):
    assert True == mock_concepts_negative_sixteen._digit_sum.include_concept()

def test_include_concept_digit_length_positive_no_single_digit(mock_concepts_five):
    assert False == mock_concepts_five._digit_length.include_concept()

def test_include_concept_digit_length_positive_yes_three_digits(mock_concepts_three_fifty_seven):
    assert True == mock_concepts_three_fifty_seven._digit_length.include_concept()

def test_include_concept_digit_length_negative_no_two_digits(mock_concepts_negative_sixteen):
    assert False == mock_concepts_negative_sixteen._digit_length.include_concept()

def test_include_concept_digit_length_negative_yes_four_digits(mock_concepts_negative_one_thousand):
    assert True == mock_concepts_negative_one_thousand._digit_length.include_concept()

def test_include_concept_too_many_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._factor.include_concept("extra")


# Test _satisfies_condition method
def test_satisfies_condition_factor_yes(mock_concepts_twenty_four):
    assert True == mock_concepts_twenty_four._factor._satisfies_condition(6)

def test_satisfies_condition_factor_no(mock_concepts_twenty_four):
    assert False == mock_concepts_twenty_four._factor._satisfies_condition(20)

def test_satisfies_condition_prime_no_arg_yes(mock_concepts_five):
    assert True == mock_concepts_five._prime._satisfies_condition()

def test_satisfies_condition_prime_no_arg_no(mock_concepts_twenty_four):
    assert False == mock_concepts_twenty_four._prime._satisfies_condition()

def test_satisfies_condition_prime_arg_no(mock_concepts_five):
    assert False == mock_concepts_five._prime._satisfies_condition(24)

def test_satisfies_condition_prime_arg_yes(mock_concepts_twenty_four):
    assert True == mock_concepts_twenty_four._prime._satisfies_condition(5)

def test_satisfies_condition_prime_arg_zero_no(mock_concepts_five):
    assert False == mock_concepts_five._prime._satisfies_condition(0)

def test_satisfies_condition_even_odd_no_arg_no(mock_concepts_five):
    assert False == mock_concepts_five._even_odd._satisfies_condition()

def test_satisfies_condition_even_odd_no_arg_yes(mock_concepts_twenty_four):
    assert True == mock_concepts_twenty_four._even_odd._satisfies_condition()

def test_satisfies_condition_even_odd_arg_yes(mock_concepts_five):
    assert True == mock_concepts_five._even_odd._satisfies_condition(24)

def test_satisfies_condition_even_odd_arg_no(mock_concepts_twenty_four):
    assert False == mock_concepts_twenty_four._even_odd._satisfies_condition(5)

def test_satisfies_condition_even_odd_arg_zero_yes(mock_concepts_five):
    assert True == mock_concepts_five._even_odd._satisfies_condition(0)

def test_satisfies_condition_perfect_square_no_arg_no(mock_concepts_five):
    assert False == mock_concepts_five._perfect_square._satisfies_condition()

def test_satisfies_condition_perfect_square_no_arg_yes(mock_concepts_one):
    assert True == mock_concepts_one._perfect_square._satisfies_condition()

def test_satisfies_condition_perfect_square_arg_yes(mock_concepts_five):
    assert True == mock_concepts_five._perfect_square._satisfies_condition(1)

def test_satisfies_condition_perfect_square_arg_no(mock_concepts_one):
    assert False == mock_concepts_one._perfect_square._satisfies_condition(5)

def test_satisfies_condition_perfect_square_arg_zero_yes(mock_concepts_five):
    assert True == mock_concepts_five._perfect_square._satisfies_condition(0)

def test_satisfies_condition_perfect_cube_no_arg_no(mock_concepts_five):
    assert False == mock_concepts_five._perfect_cube._satisfies_condition()

def test_satisfies_condition_perfect_cube_no_arg_yes(mock_concepts_one):
    assert True == mock_concepts_one._perfect_cube._satisfies_condition()

def test_satisfies_condition_perfect_cube_arg_yes(mock_concepts_five):
    assert True == mock_concepts_five._perfect_cube._satisfies_condition(1)

def test_satisfies_condition_perfect_cube_arg_no(mock_concepts_one):
    assert False == mock_concepts_one._perfect_cube._satisfies_condition(5)

def test_satisfies_condition_perfect_cube_arg_zero_yes(mock_concepts_five):
    assert True == mock_concepts_five._perfect_cube._satisfies_condition(0)

def test_satisfies_condition_too_many_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._prime._satisfies_condition(1, "extra")

def test_satisfies_condition_factor_no_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._factor._satisfies_condition()

def test_satisfies_condition_factor_too_many_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._factor._satisfies_condition(1, "extra")


# Test _get_count_satisfying_condition method
def test_get_count_satisfying_condition_some_meet_condition(mock_concepts_one):
    test_list = [1,2,3,4,5]
    assert 3 == mock_concepts_one._prime._get_count_satisfying_condition(test_list)

def test_get_count_satisfying_condition_all_meet_condition(mock_concepts_one):
    test_list = [3,5,7,11,13]
    assert 5 == mock_concepts_one._prime._get_count_satisfying_condition(test_list)

def test_get_count_satisfying_condition_none_meet_condition(mock_concepts_one):
    test_list = [10,12,14,15,16,18]
    assert 0 == mock_concepts_one._prime._get_count_satisfying_condition(test_list)

def test_get_count_satisfying_condition_no_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._prime._get_count_satisfying_condition()

def test_get_count_satisfying_condition_too_many_arguments_raises_error(mock_concepts_one):
    test_list = [1,2,3,4,5]
    with pytest.raises(TypeError):
        mock_concepts_one._prime._get_count_satisfying_condition(test_list, "extra")


# Test _get_digit_hint_feedback method
def test_get_digit_hint_feedback_prime_good_one(mock_concepts_one):
    test_text = "Test text: 1"
    assert "good" == mock_concepts_one._prime._get_digit_hint_feedback(test_text, 1, 17)

def test_get_digit_hint_feedback_prime_good_all(mock_concepts_one):
    test_text = "Test text: All"
    assert "good" == mock_concepts_one._prime._get_digit_hint_feedback(test_text, None, 23)

def test_get_digit_hint_feedback_prime_good_none(mock_concepts_one):
    test_text = "Test text: None"
    assert "good" == mock_concepts_one._prime._get_digit_hint_feedback(test_text, None, 48)

def test_get_digit_hint_feedback_prime_bad_mismatch(mock_concepts_one):
    test_text = "Test text: 2"
    assert "bad" == mock_concepts_one._prime._get_digit_hint_feedback(test_text, 2, 17)

def test_get_digit_hint_feedback_even_odd_good_one(mock_concepts_one):
    test_text = "Test text: 1"
    assert "good" == mock_concepts_one._even_odd._get_digit_hint_feedback(test_text, 1, 18)

def test_get_digit_hint_feedback_even_odd_good_all(mock_concepts_one):
    test_text = "Test text: All"
    assert "good" == mock_concepts_one._even_odd._get_digit_hint_feedback(test_text, None, 20)

def test_get_digit_hint_feedback_even_odd_good_none(mock_concepts_one):
    test_text = "Test text: None"
    assert "good" == mock_concepts_one._even_odd._get_digit_hint_feedback(test_text, None, 31)

def test_get_digit_hint_feedback_even_odd_bad_mismatch(mock_concepts_one):
    test_text = "Test text: 2"
    assert "bad" == mock_concepts_one._even_odd._get_digit_hint_feedback(test_text, 2, 18)

def test_get_digit_hint_feedback_perfect_square_good_one(mock_concepts_one):
    test_text = "Test text: 1"
    assert "good" == mock_concepts_one._perfect_square._get_digit_hint_feedback(test_text, 1, 18)

def test_get_digit_hint_feedback_perfect_square_good_all(mock_concepts_one):
    test_text = "Test text: All"
    assert "good" == mock_concepts_one._perfect_square._get_digit_hint_feedback(test_text, None, 40)

def test_get_digit_hint_feedback_perfect_square_good_none(mock_concepts_one):
    test_text = "Test text: None"
    assert "good" == mock_concepts_one._perfect_square._get_digit_hint_feedback(test_text, None, 36)

def test_get_digit_hint_feedback_perfect_square_bad_mismatch(mock_concepts_one):
    test_text = "Test text: 2"
    assert "bad" == mock_concepts_one._perfect_square._get_digit_hint_feedback(test_text, 2, 18)

def test_get_digit_hint_feedback_perfect_cube_good_one(mock_concepts_one):
    test_text = "Test text: 1"
    assert "good" == mock_concepts_one._perfect_cube._get_digit_hint_feedback(test_text, 1, 17)

def test_get_digit_hint_feedback_perfect_cube_good_all(mock_concepts_one):
    test_text = "Test text: All"
    assert "good" == mock_concepts_one._perfect_cube._get_digit_hint_feedback(test_text, None, 80)

def test_get_digit_hint_feedback_perfect_cube_good_none(mock_concepts_one):
    test_text = "Test text: None"
    assert "good" == mock_concepts_one._perfect_cube._get_digit_hint_feedback(test_text, None, 34)

def test_get_digit_hint_feedback_perfect_cube_bad_mismatch(mock_concepts_one):
    test_text = "Test text: 2"
    assert "bad" == mock_concepts_one._perfect_cube._get_digit_hint_feedback(test_text, 2, 17)

def test_get_digit_hint_feedback_no_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._prime._get_digit_hint_feedback()

def test_get_digit_hint_feedback_too_many_arguments_raises_error(mock_concepts_one):
    test_text = "Test text: 1"
    with pytest.raises(TypeError):
        mock_concepts_one._prime._get_digit_hint_feedback(test_text, 1, 17, "extra")


# Test _get_non_digit_hint_feedback method
def test_get_non_digit_hint_feedback_prime_no_number_bad(mock_concepts_one):
    assert "bad" == mock_concepts_one._prime._get_non_digit_hint_feedback(None, 24)

def test_get_non_digit_hint_feedback_prime_no_number_good(mock_concepts_one):
    assert "good" == mock_concepts_one._prime._get_non_digit_hint_feedback(None, 5)

def test_get_non_digit_hint_feedback_prime_number_good(mock_concepts_one):
    assert "good" == mock_concepts_one._prime._get_non_digit_hint_feedback(2, 24)

def test_get_non_digit_hint_feedback_prime_number_bad(mock_concepts_one):
    assert "bad" == mock_concepts_one._prime._get_non_digit_hint_feedback(8, 24)

def test_get_non_digit_hint_feedback_even_odd_good_even(mock_concepts_one):
    assert "good" == mock_concepts_one._even_odd._get_non_digit_hint_feedback("Test text: even", 24)

def test_get_non_digit_hint_feedback_even_odd_good_odd(mock_concepts_one):
    assert "good" == mock_concepts_one._even_odd._get_non_digit_hint_feedback("Test text: odd", 5)

def test_get_non_digit_hint_feedback_even_odd_bad(mock_concepts_one):
    assert "bad" == mock_concepts_one._even_odd._get_non_digit_hint_feedback("Test text: even", 5)

def test_get_non_digit_hint_feedback_perfect_square_good(mock_concepts_one):
    assert "good" == mock_concepts_one._perfect_square._get_non_digit_hint_feedback(4)

def test_get_non_digit_hint_feedback_perfect_square_bad(mock_concepts_one):
    assert "bad" == mock_concepts_one._perfect_square._get_non_digit_hint_feedback(8)

def test_get_non_digit_hint_feedback_perfect_cube_good(mock_concepts_one):
    assert "good" == mock_concepts_one._perfect_cube._get_non_digit_hint_feedback(8)

def test_get_non_digit_hint_feedback_perfect_cube_bad(mock_concepts_one):
    assert "bad" == mock_concepts_one._perfect_cube._get_non_digit_hint_feedback(4)

def test_get_non_digit_hint_feedback_no_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._prime._get_non_digit_hint_feedback()

def test_get_non_digit_hint_feedback_too_many_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._prime._get_non_digit_hint_feedback(4, "extra")


# Test _generate_main_hints method
@pytest.fixture
def factor_list_twenty_four(mock_concepts_twenty_four):
    return [1, 2, 3, 4, 6, 8, 12, 24]

@pytest.fixture
def main_hints_factor_twenty_four(mock_concepts_twenty_four, factor_list_twenty_four):
    return mock_concepts_twenty_four._factor._generate_main_hints(factor_list_twenty_four)

def test_generate_main_hints_factor_in_list(main_hints_factor_twenty_four):
    assert "Nice try!  Hint: It is divisible by 12." in main_hints_factor_twenty_four

def test_generate_main_hints_factor_not_in_list_low_endpoint(main_hints_factor_twenty_four):
    assert "Nice try!  Hint: It is divisible by 1." not in main_hints_factor_twenty_four

def test_generate_main_hints_factor_not_in_list_high_endpoint(main_hints_factor_twenty_four):
    assert "Nice try!  Hint: It is divisible by 24." not in main_hints_factor_twenty_four

def test_generate_main_hints_factor_not_in_list_unformatted(main_hints_factor_twenty_four):
    assert "Nice try!  Hint: It is divisible by {}." not in main_hints_factor_twenty_four

def test_generate_main_hints_factor_no_arguments_raises_error(mock_concepts_twenty_four):
    with pytest.raises(TypeError):
        mock_concepts_twenty_four._factor._generate_main_hints()

def test_generate_main_hints_factor_too_many_arguments_raises_error(mock_concepts_twenty_four):
    with pytest.raises(TypeError):
        mock_concepts_twenty_four._factor._generate_main_hints([1, 2, 4], "extra")

@pytest.fixture
def main_hints_multiple_five_unfiltered(mock_concepts_five):
    return mock_concepts_five._multiple._generate_main_hints(filter_results=False)

@pytest.fixture
def main_hints_multiple_five_filtered(mock_concepts_five):
    return mock_concepts_five._multiple._generate_main_hints()

@pytest.fixture
def main_hints_multiple_zero(mock_concepts_zero):
    return mock_concepts_zero._multiple._generate_main_hints(filter_results=False)

def test_generate_main_hints_multiple_in_list(main_hints_multiple_five_unfiltered):
    assert "Nice try!  Hint: 10 is a multiple." in main_hints_multiple_five_unfiltered

def test_generate_main_hints_multiple_not_in_list_non_multiple(main_hints_multiple_five_unfiltered):
    assert "Nice try!  Hint: 1 is a multiple." not in main_hints_multiple_five_unfiltered

def test_generate_main_hints_multiple_not_in_list_unformatted(main_hints_multiple_five_unfiltered):
    assert "Nice try!  Hint: {} is a multiple." not in main_hints_multiple_five_unfiltered

def test_generate_main_hints_multiple_limit_to_two(main_hints_multiple_five_filtered):
    assert 2 == len(main_hints_multiple_five_filtered)

def test_generate_main_hints_multiple_zero_in_list(main_hints_multiple_zero):
    assert "Nice try!  Hint: 0 is a multiple." in main_hints_multiple_zero

def test_generate_main_hints_multiple_zero_length_of_one(main_hints_multiple_zero):
    assert 1 == len(main_hints_multiple_zero)

@pytest.fixture
def main_hints_prime_five(mock_concepts_five):
    return mock_concepts_five._prime._generate_main_hints()

@pytest.fixture
def main_hints_prime_twenty_four(mock_concepts_twenty_four):
    return mock_concepts_twenty_four._prime._generate_main_hints()

def test_generate_main_hints_prime_in_list(main_hints_prime_five):
    assert "Nice try!  Hint: It is a prime number." in main_hints_prime_five

def test_generate_main_hints_prime_length_of_one(main_hints_prime_five):
    assert 1 == len(main_hints_prime_five)

def test_generate_main_hints_prime_not_prime_empty(main_hints_prime_twenty_four):
    assert 0 == len(main_hints_prime_twenty_four)

@pytest.fixture
def main_hints_even_odd_five(mock_concepts_five):
    return mock_concepts_five._even_odd._generate_main_hints()

@pytest.fixture
def main_hints_even_odd_twenty_four(mock_concepts_twenty_four):
    return mock_concepts_twenty_four._even_odd._generate_main_hints()

def test_generate_main_hints_even_odd_odd_in_list(main_hints_even_odd_five):
    assert "Nice try!  Hint: It is an odd number." in main_hints_even_odd_five

def test_generate_main_hints_even_odd_odd_length_of_one(main_hints_even_odd_five):
    assert 1 == len(main_hints_even_odd_five)

def test_generate_main_hints_even_odd_even_in_list(main_hints_even_odd_twenty_four):
    assert "Nice try!  Hint: It is an even number." in main_hints_even_odd_twenty_four

def test_generate_main_hints_even_odd_even_length_of_one(main_hints_even_odd_twenty_four):
    assert 1 == len(main_hints_even_odd_twenty_four)

def test_generate_main_hints_even_odd_not_in_list_unformatted(main_hints_even_odd_twenty_four):
    assert "Nice try!  Hint: It is an {} number." not in main_hints_even_odd_twenty_four

@pytest.fixture
def main_hints_perfect_square_five(mock_concepts_five):
    return mock_concepts_five._perfect_square._generate_main_hints()

@pytest.fixture
def main_hints_perfect_square_one(mock_concepts_one):
    return mock_concepts_one._perfect_square._generate_main_hints()

def test_generate_main_hints_perfect_square_in_list(main_hints_perfect_square_one):
    assert "Nice try!  Hint: It is a perfect square." in main_hints_perfect_square_one

def test_generate_main_hints_perfect_square_length_of_one(main_hints_perfect_square_one):
    assert 1 == len(main_hints_perfect_square_one)

def test_generate_main_hints_perfect_square_not_perfect_square_empty(main_hints_perfect_square_five):
    assert 0 == len(main_hints_perfect_square_five)

@pytest.fixture
def main_hints_perfect_cube_five(mock_concepts_five):
    return mock_concepts_five._perfect_cube._generate_main_hints()

@pytest.fixture
def main_hints_perfect_cube_one(mock_concepts_one):
    return mock_concepts_one._perfect_cube._generate_main_hints()

def test_generate_main_hints_perfect_cube_in_list(main_hints_perfect_cube_one):
    assert "Nice try!  Hint: It is a perfect cube." in main_hints_perfect_cube_one

def test_generate_main_hints_perfect_cube_length_of_one(main_hints_perfect_cube_one):
    assert 1 == len(main_hints_perfect_cube_one)

def test_generate_main_hints_perfect_cube_not_perfect_cube_empty(main_hints_perfect_cube_five):
    assert 0 == len(main_hints_perfect_cube_five)

@pytest.fixture
def main_hints_digit_sum_three_fifty_seven(mock_concepts_three_fifty_seven):
    return mock_concepts_three_fifty_seven._digit_sum._generate_main_hints()

@pytest.fixture
def main_hints_digit_sum_negative_one_thousand(mock_concepts_negative_one_thousand):
    return mock_concepts_negative_one_thousand._digit_sum._generate_main_hints()

def test_generate_main_hints_digit_sum_three_fifty_seven_in_list(main_hints_digit_sum_three_fifty_seven):
    assert "Nice try!  Hint: The sum of its digits is 15." in main_hints_digit_sum_three_fifty_seven

def test_generate_main_hints_digit_sum_three_fifty_seven_length_of_one(main_hints_digit_sum_three_fifty_seven):
    assert 1 == len(main_hints_digit_sum_three_fifty_seven)

def test_generate_main_hints_digit_sum_three_fifty_seven_not_in_list_unformatted(main_hints_digit_sum_three_fifty_seven):
    assert "Nice try!  Hint: The sum of its digits is {}." not in main_hints_digit_sum_three_fifty_seven

def test_generate_main_hints_digit_sum_negative_one_thousand_in_list(main_hints_digit_sum_negative_one_thousand):
    assert "Nice try!  Hint: The sum of its digits is 1." in main_hints_digit_sum_negative_one_thousand

@pytest.fixture
def main_hints_digit_length_three_fifty_seven(mock_concepts_three_fifty_seven):
    return mock_concepts_three_fifty_seven._digit_length._generate_main_hints()

@pytest.fixture
def main_hints_digit_length_negative_one_thousand(mock_concepts_negative_one_thousand):
    return mock_concepts_negative_one_thousand._digit_length._generate_main_hints()

def test_generate_main_hints_digit_length_three_fifty_seven_in_list(main_hints_digit_length_three_fifty_seven):
    assert "Nice try!  Hint: It is a 3-digit number." in main_hints_digit_length_three_fifty_seven

def test_generate_main_hints_digit_length_three_fifty_seven_length_of_one(main_hints_digit_length_three_fifty_seven):
    assert 1 == len(main_hints_digit_length_three_fifty_seven)

def test_generate_main_hints_digit_length_three_fifty_seven_not_in_list_unformatted(main_hints_digit_length_three_fifty_seven):
    assert "Nice try!  Hint: It is a {}-digit number." not in main_hints_digit_length_three_fifty_seven

def test_generate_main_hints_digit_length_negative_one_thousand_in_list(main_hints_digit_length_negative_one_thousand):
    assert "Nice try!  Hint: It is a 4-digit number." in main_hints_digit_length_negative_one_thousand


# Test _generate_factor_hints method
@pytest.fixture
def factor_hints_factor_twenty_four(mock_concepts_twenty_four, factor_list_twenty_four):
    return mock_concepts_twenty_four._factor._generate_factor_hints(factor_list_twenty_four)

def test_generate_factor_hints_factor_in_list(factor_hints_factor_twenty_four):
    assert "Nice try!  Hint: It has 8 factor(s)." in factor_hints_factor_twenty_four

def test_generate_factor_hints_factor_length_of_one(factor_hints_factor_twenty_four):
    assert 1 == len(factor_hints_factor_twenty_four)

def test_generate_factor_hints_factor_not_in_list_unformatted(factor_hints_factor_twenty_four):
    assert "Nice try!  Hint: It has {} factor(s)." not in factor_hints_factor_twenty_four

@pytest.fixture
def factor_hints_prime_twenty_four(mock_concepts_twenty_four, factor_list_twenty_four):
    return mock_concepts_twenty_four._prime._generate_factor_hints(factor_list_twenty_four)

def test_generate_factor_hints_prime_in_list(factor_hints_prime_twenty_four):
    assert "Nice try!  Hint: It has 2 prime factor(s)." in factor_hints_prime_twenty_four

def test_generate_factor_hints_prime_length_of_one(factor_hints_prime_twenty_four):
    assert 1 == len(factor_hints_prime_twenty_four)

def test_generate_factor_hints_prime_not_in_list_unformatted(factor_hints_prime_twenty_four):
    assert "Nice try!  Hint: It has {} factor(s)." not in factor_hints_prime_twenty_four

def test_generate_factor_hints_factor_no_arguments_raises_error(mock_concepts_twenty_four):
    with pytest.raises(TypeError):
        mock_concepts_twenty_four._prime._generate_factor_hints()

def test_generate_factor_hints_factor_too_many_arguments_raises_error(mock_concepts_twenty_four):
    with pytest.raises(TypeError):
        mock_concepts_twenty_four._prime._generate_factor_hints([1, 2, 4], "extra")


# Test _generate_digit_hints method
@pytest.fixture
def digit_list_twenty_four():
    return [2, 4]

@pytest.fixture
def digit_hints_factor_twenty_four(mock_concepts_twenty_four, factor_list_twenty_four, digit_list_twenty_four):
    return mock_concepts_twenty_four._factor._generate_digit_hints(factor_list_twenty_four, digit_list_twenty_four)

def test_generate_digit_hints_factor_in_list(digit_hints_factor_twenty_four):
    assert "Nice try!  Hint: All of its digits are factors." in digit_hints_factor_twenty_four

def test_generate_digit_hints_factor_length_of_one(digit_hints_factor_twenty_four):
    assert 1 == len(digit_hints_factor_twenty_four)

def test_generate_digit_hints_factor_not_in_list_unformatted(digit_hints_factor_twenty_four):
    assert "Nice try!  Hint: All of its digits are {}s." not in digit_hints_factor_twenty_four

@pytest.fixture
def digit_hints_prime_twenty_four(mock_concepts_twenty_four, digit_list_twenty_four):
    return mock_concepts_twenty_four._prime._generate_digit_hints(digit_list_twenty_four)

def test_generate_digit_hints_prime_in_list(digit_hints_prime_twenty_four):
    assert "Nice try!  Hint: 1 of its digits is a prime number." in digit_hints_prime_twenty_four

def test_generate_digit_hints_prime_length_of_one(digit_hints_prime_twenty_four):
    assert 1 == len(digit_hints_prime_twenty_four)

def test_generate_digit_hints_prime_not_in_list_unformatted(digit_hints_prime_twenty_four):
    assert "Nice try!  Hint: 1 of its digits is a {}." not in digit_hints_prime_twenty_four

@pytest.fixture
def digit_hints_even_odd_twenty_four(mock_concepts_twenty_four, digit_list_twenty_four):
    return mock_concepts_twenty_four._even_odd._generate_digit_hints(digit_list_twenty_four)

def test_generate_digit_hints_even_odd_in_list(digit_hints_even_odd_twenty_four):
    assert "Nice try!  Hint: All of its digits are even numbers." in digit_hints_even_odd_twenty_four

def test_generate_digit_hints_even_odd_length_of_one(digit_hints_even_odd_twenty_four):
    assert 1 == len(digit_hints_even_odd_twenty_four)

def test_generate_digit_hints_even_odd_not_in_list_unformatted(digit_hints_even_odd_twenty_four):
    assert "Nice try!  Hint: All of its digits are {}s." not in digit_hints_even_odd_twenty_four

@pytest.fixture
def digit_hints_perfect_square_twenty_four(mock_concepts_twenty_four, digit_list_twenty_four):
    return mock_concepts_twenty_four._perfect_square._generate_digit_hints(digit_list_twenty_four)

def test_generate_digit_hints_perfect_square_in_list(digit_hints_perfect_square_twenty_four):
    assert "Nice try!  Hint: 1 of its digits is a perfect square." in digit_hints_perfect_square_twenty_four

def test_generate_digit_hints_perfect_square_length_of_one(digit_hints_perfect_square_twenty_four):
    assert 1 == len(digit_hints_perfect_square_twenty_four)

def test_generate_digit_hints_perfect_square_not_in_list_unformatted(digit_hints_perfect_square_twenty_four):
    assert "Nice try!  Hint: 1 of its digits is a {}." not in digit_hints_perfect_square_twenty_four

@pytest.fixture
def digit_hints_perfect_cube_twenty_four(mock_concepts_twenty_four, digit_list_twenty_four):
    return mock_concepts_twenty_four._perfect_cube._generate_digit_hints(digit_list_twenty_four)

def test_generate_digit_hints_perfect_cube_in_list(digit_hints_perfect_cube_twenty_four):
    assert "Nice try!  Hint: None of its digits are perfect cubes." in digit_hints_perfect_cube_twenty_four

def test_generate_digit_hints_perfect_cube_length_of_one(digit_hints_perfect_cube_twenty_four):
    assert 1 == len(digit_hints_perfect_cube_twenty_four)

def test_generate_digit_hints_perfect_cube_not_in_list_unformatted(digit_hints_perfect_cube_twenty_four):
    assert "Nice try!  Hint: None of its digits are {}s." not in digit_hints_perfect_cube_twenty_four

def test_generate_digit_hints_perfect_cube_no_arguments_raises_error(mock_concepts_twenty_four):
    with pytest.raises(TypeError):
        mock_concepts_twenty_four._perfect_cube._generate_digit_hints()

def test_generate_digit_hints_perfect_cube_too_many_arguments_raises_error(mock_concepts_twenty_four):
    with pytest.raises(TypeError):
        mock_concepts_twenty_four._perfect_cube._generate_digit_hints([2, 4], "extra")


# Test generate_hints method
@pytest.fixture
def all_hints_factor_twenty_four(mock_concepts_twenty_four):
    return mock_concepts_twenty_four._factor.generate_hints()

def test_generate_hints_factor_main_hint_in_list(all_hints_factor_twenty_four):
    assert "Nice try!  Hint: It is divisible by 12." in all_hints_factor_twenty_four

def test_generate_hints_factor_factor_hint_in_list(all_hints_factor_twenty_four):
    assert "Nice try!  Hint: It has 8 factor(s)." in all_hints_factor_twenty_four

def test_generate_hints_factor_digit_hint_in_list(all_hints_factor_twenty_four):
    assert "Nice try!  Hint: All of its digits are factors." in all_hints_factor_twenty_four

def test_generate_hints_factor_correct_length(all_hints_factor_twenty_four):
    assert 8 == len(all_hints_factor_twenty_four)

@pytest.fixture
def all_hints_multiple_five(mock_concepts_five):
    return mock_concepts_five._multiple.generate_hints(filter_results=False)

def test_generate_hints_multiple_main_hint_in_list(all_hints_multiple_five):
    assert "Nice try!  Hint: 10 is a multiple." in all_hints_multiple_five

def test_generate_hints_multiple_correct_length(all_hints_multiple_five):
    assert 5 == len(all_hints_multiple_five)

@pytest.fixture
def all_hints_prime_five(mock_concepts_five):
    return mock_concepts_five._prime.generate_hints()

@pytest.fixture
def all_hints_prime_twenty_four(mock_concepts_twenty_four):
    return mock_concepts_twenty_four._prime.generate_hints()

def test_generate_hints_prime_five_main_hint_in_list(all_hints_prime_five):
    assert "Nice try!  Hint: It is a prime number." in all_hints_prime_five

def test_generate_hints_prime_five_correct_length(all_hints_prime_five):
    assert 1 == len(all_hints_prime_five)

def test_generate_hints_prime_twenty_four_factor_hint_in_list(all_hints_prime_twenty_four):
    assert "Nice try!  Hint: It has 2 prime factor(s)." in all_hints_prime_twenty_four

def test_generate_hints_prime_twenty_four_digit_hint_in_list(all_hints_prime_twenty_four):
    assert "Nice try!  Hint: 1 of its digits is a prime number." in all_hints_prime_twenty_four

def test_generate_hints_prime_twenty_four_correct_length(all_hints_prime_twenty_four):
    assert 2 == len(all_hints_prime_twenty_four)

@pytest.fixture
def all_hints_even_odd_twenty_four(mock_concepts_twenty_four):
    return mock_concepts_twenty_four._even_odd.generate_hints()

def test_generate_hints_even_odd_main_hint_in_list(all_hints_even_odd_twenty_four):
    assert "Nice try!  Hint: It is an even number." in all_hints_even_odd_twenty_four

def test_generate_hints_even_odd_digit_hint_in_list(all_hints_even_odd_twenty_four):
    assert "Nice try!  Hint: All of its digits are even numbers." in all_hints_even_odd_twenty_four

def test_generate_hints_even_odd_correct_length(all_hints_even_odd_twenty_four):
    assert 2 == len(all_hints_even_odd_twenty_four)

@pytest.fixture
def all_hints_perfect_square_one(mock_concepts_one):
    return mock_concepts_one._perfect_square.generate_hints()

@pytest.fixture
def all_hints_perfect_square_twenty_four(mock_concepts_twenty_four):
    return mock_concepts_twenty_four._perfect_square.generate_hints()

def test_generate_hints_perfect_square_one_main_hint_in_list(all_hints_perfect_square_one):
    assert "Nice try!  Hint: It is a perfect square." in all_hints_perfect_square_one

def test_generate_hints_perfect_square_one_correct_length(all_hints_perfect_square_one):
    assert 1 == len(all_hints_perfect_square_one)

def test_generate_hints_perfect_square_twenty_four_digit_hint_in_list(all_hints_perfect_square_twenty_four):
    assert "Nice try!  Hint: 1 of its digits is a perfect square." in all_hints_perfect_square_twenty_four

def test_generate_hints_perfect_square_twenty_four_correct_length(all_hints_perfect_square_twenty_four):
    assert 1 == len(all_hints_perfect_square_twenty_four)

@pytest.fixture
def all_hints_perfect_cube_one(mock_concepts_one):
    return mock_concepts_one._perfect_cube.generate_hints()

@pytest.fixture
def all_hints_perfect_cube_twenty_four(mock_concepts_twenty_four):
    return mock_concepts_twenty_four._perfect_cube.generate_hints()

def test_generate_hints_perfect_cube_one_main_hint_in_list(all_hints_perfect_cube_one):
    assert "Nice try!  Hint: It is a perfect cube." in all_hints_perfect_cube_one

def test_generate_hints_perfect_cube_one_correct_length(all_hints_perfect_cube_one):
    assert 1 == len(all_hints_perfect_cube_one)

def test_generate_hints_perfect_cube_twenty_four_digit_hint_in_list(all_hints_perfect_cube_twenty_four):
    assert "Nice try!  Hint: None of its digits are perfect cubes." in all_hints_perfect_cube_twenty_four

def test_generate_hints_perfect_cube_twenty_four_correct_length(all_hints_perfect_cube_twenty_four):
    assert 1 == len(all_hints_perfect_cube_twenty_four)

@pytest.fixture
def all_hints_digit_sum_three_fifty_seven(mock_concepts_three_fifty_seven):
    return mock_concepts_three_fifty_seven._digit_sum.generate_hints()

def test_generate_hints_digit_sum_main_hint_in_list(all_hints_digit_sum_three_fifty_seven):
    assert "Nice try!  Hint: The sum of its digits is 15." in all_hints_digit_sum_three_fifty_seven

def test_generate_hints_digit_sum_correct_length(all_hints_digit_sum_three_fifty_seven):
    assert 1 == len(all_hints_digit_sum_three_fifty_seven)

@pytest.fixture
def all_hints_digit_length_three_fifty_seven(mock_concepts_three_fifty_seven):
    return mock_concepts_three_fifty_seven._digit_length.generate_hints()

def test_generate_hints_digit_length_main_hint_in_list(all_hints_digit_length_three_fifty_seven):
    assert "Nice try!  Hint: It is a 3-digit number." in all_hints_digit_length_three_fifty_seven

def test_generate_hints_digit_length_correct_length(all_hints_digit_length_three_fifty_seven):
    assert 1 == len(all_hints_digit_length_three_fifty_seven)

def test_generate_hints_digit_length_too_many_arguments_raises_error(mock_concepts_three_fifty_seven):
    with pytest.raises(TypeError):
        mock_concepts_three_fifty_seven._digit_length.generate_hints("extra")


# Test evaluate_guess method
@pytest.fixture
def factor_main_hint():
    return "Nice try!  Hint: It is divisible by 7."

def test_evaluate_guess_factor_main_hint_good(mock_concepts_one, factor_main_hint):
    assert "good" == mock_concepts_one._factor.evaluate_guess(21, factor_main_hint)

def test_evaluate_guess_factor_main_hint_bad(mock_concepts_one, factor_main_hint):
    assert "bad" == mock_concepts_one._factor.evaluate_guess(10, factor_main_hint)

@pytest.fixture
def factor_factor_hint():
    return "Nice try!  Hint: It has 4 factor(s)."

def test_evaluate_guess_factor_factor_hint_good(mock_concepts_one, factor_factor_hint):
    assert "good" == mock_concepts_one._factor.evaluate_guess(15, factor_factor_hint)

def test_evaluate_guess_factor_factor_hint_bad(mock_concepts_one, factor_factor_hint):
    assert "bad" == mock_concepts_one._factor.evaluate_guess(9, factor_factor_hint)

@pytest.fixture
def factor_digit_hint():
    return "Nice try!  Hint: 1 of its digits is a factor."

def test_evaluate_guess_factor_digit_hint_good(mock_concepts_one, factor_digit_hint):
    assert "good" == mock_concepts_one._factor.evaluate_guess(63, factor_digit_hint)

def test_evaluate_guess_factor_digit_hint_bad(mock_concepts_one, factor_digit_hint):
    assert "bad" == mock_concepts_one._factor.evaluate_guess(36, factor_digit_hint)

@pytest.fixture
def multiple_main_hint():
    return "Nice try!  Hint: 30 is a multiple."

def test_evaluate_guess_multiple_main_hint_good(mock_concepts_one, multiple_main_hint):
    assert "good" == mock_concepts_one._multiple.evaluate_guess(2, multiple_main_hint)

def test_evaluate_guess_multiple_main_hint_bad(mock_concepts_one, multiple_main_hint):
    assert "bad" == mock_concepts_one._multiple.evaluate_guess(4, multiple_main_hint)

@pytest.fixture
def prime_main_hint():
    return "Nice try!  Hint: It is a prime number."

def test_evaluate_guess_prime_main_hint_good(mock_concepts_one, prime_main_hint):
    assert "good" == mock_concepts_one._prime.evaluate_guess(5, prime_main_hint)

def test_evaluate_guess_prime_main_hint_bad(mock_concepts_one, prime_main_hint):
    assert "bad" == mock_concepts_one._prime.evaluate_guess(1, prime_main_hint)

@pytest.fixture
def prime_factor_hint():
    return "Nice try!  Hint: It has 1 prime factor(s)."

def test_evaluate_guess_prime_factor_hint_good(mock_concepts_one, prime_factor_hint):
    assert "good" == mock_concepts_one._prime.evaluate_guess(9, prime_factor_hint)

def test_evaluate_guess_prime_factor_hint_bad(mock_concepts_one, prime_factor_hint):
    assert "bad" == mock_concepts_one._prime.evaluate_guess(18, prime_factor_hint)

@pytest.fixture
def prime_digit_hint():
    return "Nice try!  Hint: None of its digits are prime numbers."

def test_evaluate_guess_prime_digit_hint_good(mock_concepts_one, prime_digit_hint):
    assert "good" == mock_concepts_one._prime.evaluate_guess(48, prime_digit_hint)

def test_evaluate_guess_prime_digit_hint_bad(mock_concepts_one, prime_digit_hint):
    assert "bad" == mock_concepts_one._prime.evaluate_guess(25, prime_digit_hint)

@pytest.fixture
def even_odd_main_hint():
    return "Nice try!  Hint: It is an odd number."

def test_evaluate_guess_even_odd_main_hint_good(mock_concepts_one, even_odd_main_hint):
    assert "good" == mock_concepts_one._even_odd.evaluate_guess(1, even_odd_main_hint)

def test_evaluate_guess_even_odd_main_hint_bad(mock_concepts_one, even_odd_main_hint):
    assert "bad" == mock_concepts_one._even_odd.evaluate_guess(24, even_odd_main_hint)

@pytest.fixture
def even_odd_digit_hint():
    return "Nice try!  Hint: All of its digits are even numbers."

def test_evaluate_guess_even_odd_digit_hint_good(mock_concepts_one, even_odd_digit_hint):
    assert "good" == mock_concepts_one._even_odd.evaluate_guess(48, even_odd_digit_hint)

def test_evaluate_guess_even_odd_digit_hint_bad(mock_concepts_one, even_odd_digit_hint):
    assert "bad" == mock_concepts_one._even_odd.evaluate_guess(218, even_odd_digit_hint)

@pytest.fixture
def perfect_square_main_hint():
    return "Nice try!  Hint: It is a perfect square."

def test_evaluate_guess_perfect_square_main_hint_good(mock_concepts_one, perfect_square_main_hint):
    assert "good" == mock_concepts_one._perfect_square.evaluate_guess(49, perfect_square_main_hint)

def test_evaluate_guess_perfect_square_main_hint_bad(mock_concepts_one, perfect_square_main_hint):
    assert "bad" == mock_concepts_one._perfect_square.evaluate_guess(27, perfect_square_main_hint)

@pytest.fixture
def perfect_square_digit_hint():
    return "Nice try!  Hint: 2 of its digits are perfect squares."

def test_evaluate_guess_perfect_square_digit_hint_good(mock_concepts_one, perfect_square_digit_hint):
    assert "good" == mock_concepts_one._perfect_square.evaluate_guess(493, perfect_square_digit_hint)

def test_evaluate_guess_perfect_square_digit_hint_bad(mock_concepts_one, perfect_square_digit_hint):
    assert "bad" == mock_concepts_one._perfect_square.evaluate_guess(114, perfect_square_digit_hint)

@pytest.fixture
def perfect_cube_main_hint():
    return "Nice try!  Hint: It is a perfect cube."

def test_evaluate_guess_perfect_cube_main_hint_good(mock_concepts_one, perfect_cube_main_hint):
    assert "good" == mock_concepts_one._perfect_cube.evaluate_guess(8, perfect_cube_main_hint)

def test_evaluate_guess_perfect_cube_main_hint_bad(mock_concepts_one, perfect_cube_main_hint):
    assert "bad" == mock_concepts_one._perfect_cube.evaluate_guess(4, perfect_cube_main_hint)

@pytest.fixture
def perfect_cube_digit_hint():
    return "Nice try!  Hint: All of its digits are perfect cubes."

def test_evaluate_guess_perfect_cube_digit_hint_good(mock_concepts_one, perfect_cube_digit_hint):
    assert "good" == mock_concepts_one._perfect_cube.evaluate_guess(80, perfect_cube_digit_hint)

def test_evaluate_guess_perfect_cube_digit_hint_bad(mock_concepts_one, perfect_cube_digit_hint):
    assert "bad" == mock_concepts_one._perfect_cube.evaluate_guess(41, perfect_cube_digit_hint)

@pytest.fixture
def digit_sum_main_hint():
    return "Nice try!  Hint: The sum of the digits is 8."

def test_evaluate_guess_digit_sum_main_hint_good(mock_concepts_one, digit_sum_main_hint):
    assert "good" == mock_concepts_one._digit_sum.evaluate_guess(26, digit_sum_main_hint)

def test_evaluate_guess_digit_sum_main_hint_bad(mock_concepts_one, digit_sum_main_hint):
    assert "bad" == mock_concepts_one._digit_sum.evaluate_guess(45, digit_sum_main_hint)

@pytest.fixture
def digit_length_main_hint():
    return "Nice try!  Hint: It is a 3-digit number."

def test_evaluate_guess_digit_length_main_hint_good(mock_concepts_one, digit_length_main_hint):
    assert "good" == mock_concepts_one._digit_length.evaluate_guess(108, digit_length_main_hint)

def test_evaluate_guess_digit_length_main_hint_bad(mock_concepts_one, digit_length_main_hint):
    assert "bad" == mock_concepts_one._digit_length.evaluate_guess(2455, digit_length_main_hint)

def test_evaluate_guess_digit_length_no_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._digit_length.evaluate_guess()

def test_evaluate_guess_digit_length_too_many_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._digit_length.evaluate_guess(108, digit_length_main_hint, "extra")



### Concept Manager Tests

# Test _create_hint_concept_list method
def test_create_hint_concept_list_concepts_one_no_arg(mock_concepts_one):
    concept_list = [
        mock_concepts_one._factor,
        mock_concepts_one._prime,
        mock_concepts_one._even_odd,
        mock_concepts_one._perfect_square,
        mock_concepts_one._perfect_cube
    ]
    assert concept_list == mock_concepts_one._create_hint_concept_list()

def test_create_hint_concept_list_concepts_zero_no_arg(mock_concepts_zero):
    concept_list = [
        mock_concepts_zero._prime,
        mock_concepts_zero._even_odd,
        mock_concepts_zero._perfect_square,
        mock_concepts_zero._perfect_cube
    ]
    assert concept_list == mock_concepts_zero._create_hint_concept_list()

def test_create_hint_concept_list_concepts_five_no_arg(mock_concepts_five):
    concept_list = [
        mock_concepts_five._factor,
        mock_concepts_five._multiple,
        mock_concepts_five._prime,
        mock_concepts_five._even_odd,
        mock_concepts_five._perfect_square,
        mock_concepts_five._perfect_cube
    ]
    assert concept_list == mock_concepts_five._create_hint_concept_list()

def test_create_hint_concept_list_concepts_twenty_four_no_arg(mock_concepts_twenty_four):
    concept_list = [
        mock_concepts_twenty_four._factor,
        mock_concepts_twenty_four._multiple,
        mock_concepts_twenty_four._prime,
        mock_concepts_twenty_four._even_odd,
        mock_concepts_twenty_four._perfect_square,
        mock_concepts_twenty_four._perfect_cube,
        mock_concepts_twenty_four._digit_sum
    ]
    assert concept_list == mock_concepts_twenty_four._create_hint_concept_list()

def test_create_hint_concept_list_concepts_three_fifty_seven_no_arg(mock_concepts_three_fifty_seven):
    concept_list = [
        mock_concepts_three_fifty_seven._factor,
        mock_concepts_three_fifty_seven._multiple,
        mock_concepts_three_fifty_seven._prime,
        mock_concepts_three_fifty_seven._perfect_square,
        mock_concepts_three_fifty_seven._perfect_cube,
        mock_concepts_three_fifty_seven._digit_sum,
        mock_concepts_three_fifty_seven._digit_length
    ]
    assert concept_list == mock_concepts_three_fifty_seven._create_hint_concept_list()

def test_create_hint_concept_list_concepts_three_fifty_seven_arg_main_concepts(mock_concepts_three_fifty_seven):
    concept_list = [
        mock_concepts_three_fifty_seven._factor,
        mock_concepts_three_fifty_seven._multiple,
        mock_concepts_three_fifty_seven._prime,
        mock_concepts_three_fifty_seven._perfect_square,
        mock_concepts_three_fifty_seven._perfect_cube,
        mock_concepts_three_fifty_seven._digit_sum,
        mock_concepts_three_fifty_seven._digit_length
    ]
    main_concepts = mock_concepts_three_fifty_seven._main_concepts
    assert concept_list == mock_concepts_three_fifty_seven._create_hint_concept_list(concepts=main_concepts)

def test_create_hint_concept_list_concepts_three_fifty_seven_arg_factor_concepts(mock_concepts_three_fifty_seven):
    concept_list = [
        mock_concepts_three_fifty_seven._factor,
        mock_concepts_three_fifty_seven._prime
    ]
    factor_concepts = mock_concepts_three_fifty_seven._factor_concepts
    assert concept_list == mock_concepts_three_fifty_seven._create_hint_concept_list(concepts=factor_concepts)

def test_create_hint_concept_list_concepts_three_fifty_seven_arg_digit_concepts(mock_concepts_three_fifty_seven):
    concept_list = [
        mock_concepts_three_fifty_seven._factor,
        mock_concepts_three_fifty_seven._prime,
        mock_concepts_three_fifty_seven._perfect_square,
        mock_concepts_three_fifty_seven._perfect_cube
    ]
    digit_concepts = mock_concepts_three_fifty_seven._digit_concepts
    assert concept_list == mock_concepts_three_fifty_seven._create_hint_concept_list(concepts=digit_concepts)

def test_create_hint_concept_list_concepts_negative_sixteen_no_arg(mock_concepts_negative_sixteen):
    concept_list = [
        mock_concepts_negative_sixteen._factor,
        mock_concepts_negative_sixteen._multiple,
        mock_concepts_negative_sixteen._even_odd,
        mock_concepts_negative_sixteen._perfect_cube,
        mock_concepts_negative_sixteen._digit_sum
    ]
    assert concept_list == mock_concepts_negative_sixteen._create_hint_concept_list()

def test_create_hint_concept_list_concepts_negative_one_thousand_no_arg(mock_concepts_negative_one_thousand):
    concept_list = [
        mock_concepts_negative_one_thousand._factor,
        mock_concepts_negative_one_thousand._multiple,
        mock_concepts_negative_one_thousand._perfect_cube,
        mock_concepts_negative_one_thousand._digit_sum,
        mock_concepts_negative_one_thousand._digit_length
    ]
    assert concept_list == mock_concepts_negative_one_thousand._create_hint_concept_list()

def test_create_hint_concept_list_concepts_too_many_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one._create_hint_concept_list(concepts=mock_concepts_zero, extra="no")


# Test check_greater_or_less method
@pytest.fixture
def higher_text():
    return "Nice try!  Higher."

@pytest.fixture
def lower_text():
    return "Nice try!  Lower."

def test_check_greater_or_less_concepts_positive_higher(mock_concepts_one, higher_text):
    assert higher_text == mock_concepts_one.check_greater_or_less(2, 5)

def test_check_greater_or_less_concepts_positive_lower(mock_concepts_one, lower_text):
    assert lower_text == mock_concepts_one.check_greater_or_less(8, 5)

def test_check_greater_or_less_concepts_negative_higher(mock_concepts_one, higher_text):
    assert higher_text == mock_concepts_one.check_greater_or_less(-17, -16)

def test_check_greater_or_less_concepts_negative_lower(mock_concepts_one, lower_text):
    assert lower_text == mock_concepts_one.check_greater_or_less(0, -16)

def test_check_greater_or_less_concepts_no_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one.check_greater_or_less()

def test_check_greater_or_less_concepts_too_many_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
       mock_concepts_one.check_greater_or_less(1, 2, "extra")


# Test generate_hints method
@pytest.fixture
def all_hints_three_fifty_seven(mock_concepts_three_fifty_seven):
    return mock_concepts_three_fifty_seven.generate_hints(check_db=False, filter_results=False)

def test_generate_hints_concepts_factor_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: 2 of its digits are factors." in all_hints_three_fifty_seven

def test_generate_hints_concepts_multiple_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: 714 is a multiple." in all_hints_three_fifty_seven

def test_generate_hints_concepts_prime_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: It has 3 prime factor(s)." in all_hints_three_fifty_seven

def test_generate_hints_concepts_even_odd_not_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: It is an odd number." not in all_hints_three_fifty_seven

def test_generate_hints_concepts_perfect_square_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: None of its digits are perfect squares." in all_hints_three_fifty_seven

def test_generate_hints_concepts_perfect_cube_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: None of its digits are perfect cubes." in all_hints_three_fifty_seven

def test_generate_hints_concepts_digit_sum_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: The sum of its digits is 15." in all_hints_three_fifty_seven

def test_generate_hints_concepts_digit_length_in_list(all_hints_three_fifty_seven):
    assert "Nice try!  Hint: It is a 3-digit number." in all_hints_three_fifty_seven

def test_generate_hints_concepts_correct_length(all_hints_three_fifty_seven):
    assert 19 == len(all_hints_three_fifty_seven)

def test_generate_hints_concepts_filter_results_correct_length(mock_concepts_three_fifty_seven):
    hint_list = mock_concepts_three_fifty_seven.generate_hints(check_db=False, filter_results=True)
    assert 16 == len(hint_list)

def test_generate_hints_concepts_too_many_arguments_raises_error(mock_concepts_three_fifty_seven):
    with pytest.raises(TypeError):
        mock_concepts_three_fifty_seven.generate_hints(check_db=False, filter_results=False, extra="no")


# Test evaluate_guess method
def test_evaluate_guess_concepts_factor_good(mock_concepts_one, factor_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("factor", 21, factor_main_hint)

def test_evaluate_guess_concepts_factor_bad(mock_concepts_one, factor_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("multiple", 21, factor_main_hint)

def test_evaluate_guess_concepts_multiple_good(mock_concepts_one, multiple_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("multiple", 2, multiple_main_hint)

def test_evaluate_guess_concepts_multiple_bad(mock_concepts_one, multiple_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("factor", 2, multiple_main_hint)

def test_evaluate_guess_concepts_prime_good(mock_concepts_one, prime_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("prime", 2, prime_main_hint)

def test_evaluate_guess_concepts_prime_bad(mock_concepts_one, prime_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("even_odd", 2, prime_main_hint)

def test_evaluate_guess_concepts_even_odd_good(mock_concepts_one, even_odd_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("even_odd", 1, even_odd_main_hint)

def test_evaluate_guess_concepts_even_odd_bad(mock_concepts_one, even_odd_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("prime", 1, even_odd_main_hint)

def test_evaluate_guess_concepts_perfect_square_good(mock_concepts_one, perfect_square_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("perfect_square", 49, perfect_square_main_hint)

def test_evaluate_guess_concepts_perfect_square_bad(mock_concepts_one, perfect_square_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("perfect_cube", 49, perfect_square_main_hint)

def test_evaluate_guess_concepts_perfect_cube_good(mock_concepts_one, perfect_cube_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("perfect_cube", 8, perfect_cube_main_hint)

def test_evaluate_guess_concepts_perfect_cube_bad(mock_concepts_one, perfect_cube_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("perfect_square", 8, perfect_cube_main_hint)

def test_evaluate_guess_concepts_digit_sum_good(mock_concepts_one, digit_sum_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("digit_sum", 26, digit_sum_main_hint)

def test_evaluate_guess_concepts_digit_sum_bad(mock_concepts_one, digit_sum_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("digit_length", 26, digit_sum_main_hint)

def test_evaluate_guess_concepts_digit_length_good(mock_concepts_one, digit_length_main_hint):
    assert "good" == mock_concepts_one.evaluate_guess("digit_length", 108, digit_length_main_hint)

def test_evaluate_guess_concepts_digit_length_bad(mock_concepts_one, digit_length_main_hint):
    assert "bad" == mock_concepts_one.evaluate_guess("digit_sum", 108, digit_length_main_hint)

def test_evaluate_guess_concepts_no_arguments_raises_error(mock_concepts_one):
    with pytest.raises(TypeError):
        mock_concepts_one.evaluate_guess()

def test_evaluate_guess_concepts_too_many_arguments_raises_error(mock_concepts_one, factor_main_hint):
    with pytest.raises(TypeError):
        mock_concepts_one.evaluate_guess("factor", 21, factor_main_hint, "extra")



### Tests Incorporating DB

@pytest.fixture
def mock_concepts_three(sqlite_db_fake, test_db_path):
    for table in non_type_tables:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    yield ConceptManager(3, numbers, sqlite_db_fake, data)
    for table in non_type_tables:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)


# Test _format_hint_types method
def test_format_hint_types_one(mock_concepts_three):
    assert "'factor'" == mock_concepts_three._format_hint_types(["factor"])

def test_format_hint_types_multiple(mock_concepts_three):
    assert "'factor','multiple','prime'" == mock_concepts_three._format_hint_types(["factor", "multiple", "prime"])

def test_format_hint_types_no_arguments_raises_error(mock_concepts_three):
    with pytest.raises(TypeError):
        mock_concepts_three._format_hint_types()

def test_format_hint_types_too_many_arguments_raises_error(mock_concepts_three):
    with pytest.raises(TypeError):
        mock_concepts_three._format_hint_types(["factor"], "extra")


# Test _check_db_for_hints method
def test_check_db_for_hints_one(mock_concepts_three, test_db_path):
    actual_hints = mock_concepts_three._check_db_for_hints(["prime"], _db_path=test_db_path)
    expected_hints = [("prime", "Nice try!  Hint: It is a prime number.")]
    assert expected_hints == actual_hints

def test_check_db_for_hints_multiple(mock_concepts_three, test_db_path):
    actual_hints = mock_concepts_three._check_db_for_hints(["prime", "even_odd"], _db_path=test_db_path)
    expected_hints = [("prime", "Nice try!  Hint: It is a prime number."),
                      ("even_odd", "Nice try!  Hint: It is an odd number.")]
    assert expected_hints == actual_hints

def test_check_db_for_hints_no_arguments_raises_error(mock_concepts_three):
    with pytest.raises(TypeError):
        mock_concepts_three._check_db_for_hints()

def test_check_db_for_hints_too_many_arguments_raises_error(mock_concepts_three):
    with pytest.raises(TypeError):
        mock_concepts_three._check_db_for_hints(["factor"], _db_path=test_db_path, extra="no")


# Test _get_hints_from_db method
def test_get_hints_from_db_without_multiple(mock_concepts_three, test_db_path):
    actual_hints = mock_concepts_three._get_hints_from_db(["prime", "even_odd"], _db_path=test_db_path)
    expected_hints = ["Nice try!  Hint: It is a prime number.",
                      "Nice try!  Hint: It is an odd number."]
    assert expected_hints == actual_hints

def test_get_hints_from_db_with_multiple_correct_length(mock_concepts_three, test_db_path):
    actual_hints = mock_concepts_three._get_hints_from_db(["multiple", "prime", "even_odd"], _db_path=test_db_path)
    assert 4 == len(actual_hints)

def test_get_hints_from_db_with_multiple_two_multiple_hints(mock_concepts_three, test_db_path):
    actual_hints = mock_concepts_three._get_hints_from_db(["multiple", "prime", "even_odd"], _db_path=test_db_path)
    multiple_hints = [hint for hint in actual_hints if "multiple" in hint]
    assert 2 == len(multiple_hints)

def test_get_hints_from_db_no_arguments_raises_error(mock_concepts_three):
    with pytest.raises(TypeError):
        mock_concepts_three._get_hints_from_db()

def test_get_hints_from_db_too_many_arguments_raises_error(mock_concepts_three, test_db_path):
    with pytest.raises(TypeError):
        mock_concepts_three._get_hints_from_db(["factor"], _db_path=test_db_path, extra="no")


# Test generate_hints method
@pytest.fixture
def all_hints_three(mock_concepts_three, test_db_path):
    return mock_concepts_three.generate_hints(check_db=True, _db_path=test_db_path)

def test_generate_hints_concepts_db_prime_in_list(all_hints_three):
    assert "Nice try!  Hint: It is a prime number." in all_hints_three

def test_generate_hints_concepts_db_even_odd_not_in_list(all_hints_three):
    assert "Nice try!  Hint: It is an odd number." in all_hints_three

def test_generate_hints_concepts_db_correct_length(all_hints_three):
    assert 4 == len(all_hints_three)



