import pytest
from main.tests.tests_setup import objects_fake_global_dict



@pytest.fixture
def numbers():
    objects_fake_global = objects_fake_global_dict["easy"]
    return objects_fake_global.get_object("numbers")


def test_settings_version_beginning():
    objects_fake_global = objects_fake_global_dict["easy"]
    settings = objects_fake_global.get_object("settings")
    assert "easy" == settings.get_setting("level of difficulty name")

### Validator Object Tests

@pytest.fixture
def validator(numbers):
    return numbers._validator


# Test _is_integer method
def test_is_integer_positive_integer(validator):
    assert True == validator._is_integer('3')

def test_is_integer_positive_decimal(validator):
    assert False == validator._is_integer('.5')

def test_is_integer_negative_integer(validator):
    assert True == validator._is_integer('-10')

def test_is_integer_negative_decimal(validator):
    assert False == validator._is_integer('-2.1')

def test_is_integer_zero(validator):
    assert True == validator._is_integer('0')

def test_is_integer_letter(validator):
    assert False == validator._is_integer('a')

def test_is_integer_blank(validator):
    assert False == validator._is_integer('')

def test_is_integer_no_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator._is_integer()

def test_is_integer_too_many_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator._is_integer(1, 2)


# Test _is_in_range method
def test_is_in_range_inside(validator):
    assert True == validator._is_in_range('5', (1, 10))

def test_is_in_range_low_endpoint(validator):
    assert True == validator._is_in_range('-5', (-5, 5))

def test_is_in_range_high_endpoint(validator):
    assert True == validator._is_in_range('1000', (1, 1000))

def test_is_in_range_outside_low(validator):
    assert False == validator._is_in_range('0', (1, 100))

def test_is_in_range_outside_high(validator):
    assert False == validator._is_in_range('101', (1, 100))

def test_is_in_range_no_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator._is_in_range()

def test_is_in_range_too_many_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator._is_integer('5', (1, 10), 3)


# Test validate_range method
def test_validate_range_positive_valid(validator):
    assert (1, 10) == validator.validate_range(('1', '10'))

def test_validate_range_negative_valid(validator):
    assert (-10, -1) == validator.validate_range(('-10', '-1'))

def test_validate_range_zero_valid(validator):
    assert (0, 100) == validator.validate_range(('0', '100'))

def test_validate_range_missing(validator):
    assert 'missing' == validator.validate_range(('', ''))

def test_validate_range_positive_comparison(validator):
    assert 'comparison' == validator.validate_range(('10', '1'))

def test_validate_range_negative_comparison(validator):
    assert 'comparison' == validator.validate_range(('-1', '-10'))

def test_validate_range_equal_comparison(validator):
    assert 'comparison' == validator.validate_range(('5', '5'))

def test_validate_range_zero_comparison(validator):
    assert 'comparison' == validator.validate_range(('0', '0'))

def test_validate_range_first_invalid(validator):
    assert 'invalid' == validator.validate_range(('', '10'))

def test_validate_range_second_invalid(validator):
    assert 'invalid' == validator.validate_range(('1', '5.5'))

def test_validate_range_both_invalid(validator):
    assert 'invalid' == validator.validate_range(('a', 'b'))

def test_validate_range_tuple_too_large(validator):
    assert None == validator.validate_range((1, 2, 5))

def test_validate_range_no_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator.validate_range()

def test_validate_range_too_many_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator.validate_range((1, 2), (3, 4))


# Test validate_guess method
def test_validate_guess_non_integer(validator):
    assert 'non_integer' == validator.validate_guess('8.1', (1, 10))

def test_validate_guess_non_integer_out_of_range(validator):
    assert 'non_integer' == validator.validate_guess('11.1', (1, 10))

def test_validate_guess_out_of_range(validator):
    assert 'out_of_range' == validator.validate_guess('-2', (1, 10))

def test_validate_guess_valid(validator):
    assert None == validator.validate_guess('5', (1, 10))

def test_validate_guess_no_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator.validate_guess()

def test_validate_guess_too_many_arguments_raises_error(validator):
    with pytest.raises(TypeError):
        validator.validate_guess('5', (1, 10), 3)


# Test validate_user_entry method
def test_validate_user_entry_guess(numbers):
    assert None == numbers.validate_user_entry('guess', '5', (1, 10))

def test_validate_user_entry_number_range(numbers):
    assert (1, 10) == numbers.validate_user_entry('number range', ('1', '10'))

def test_validate_user_entry_first_argument_not_found(numbers):
    assert None == numbers.validate_user_entry('number_range', ('1', '10'))

def test_validate_user_entry_no_arguments_raises_error(numbers):
    with pytest.raises(TypeError):
        numbers.validate_user_entry()



### RandomNumberGenerator Object Tests

@pytest.fixture
def random(numbers):
    return numbers._random


# Test generate_random_number method
def test_generate_random_number_easy(random):
    test_set = set([random.generate_random_number((1, 10)) for i in range(1, 51)])
    assert True == all([n in range(1, 11) for n in test_set])

def test_generate_random_number_medium(random):
    test_set = set([random.generate_random_number((1, 100)) for i in range(1, 501)])
    assert True == all([n in range(1, 101) for n in test_set])

def test_generate_random_number_hard(random):
    test_set = set([random.generate_random_number((1, 1000)) for i in range(1, 5001)])
    assert True == all([n in range(1, 1001) for n in test_set])

def test_generate_random_number_custom_positive_zero(random):
    test_set = set([random.generate_random_number((0, 5)) for i in range(1, 31)])
    assert True == all([n in range(0, 6) for n in test_set])

def test_generate_random_number_custom_negative(random):
    test_set = set([random.generate_random_number((-5, -1)) for i in range(1, 26)])
    assert True == all([n in [-5,-4,-3,-2,-1] for n in test_set])

def test_generate_random_number_custom_negative_positive(random):
    test_set = set([random.generate_random_number((-2, 2)) for i in range(1, 26)])
    assert True == all([n in [-2,-1,0,1,2] for n in test_set])

def test_generate_random_number_no_arguments_raises_error(random):
    with pytest.raises(TypeError):
        random.generate_random_number()

def test_generate_random_number_too_many_arguments_raises_error(random):
    with pytest.raises(TypeError):
        random.generate_random_number((1, 2), (3, 4))


# Test unique_random_numbers method
@pytest.fixture
def random_number_list_2(random):
    return random.unique_random_numbers((1, 5), 2)

def test_unique_random_numbers_length(random_number_list_2):
    assert 2 == len(random_number_list_2)

def test_unique_random_numbers_no_repeats(random_number_list_2):
    assert len(set(random_number_list_2)) == len(random_number_list_2)

def test_unique_random_numbers_each_in_range(random_number_list_2):
    assert True == all([n in range(1, 6) for n in random_number_list_2])

def test_unique_random_numbers_no_arguments_raises_error(random):
    with pytest.raises(TypeError):
        random.unique_random_numbers()

def test_unique_random_numbers_too_many_arguments_raises_error(random):
    with pytest.raises(TypeError):
        random.unique_random_numbers((1, 5), 2, 3)


# Test get_random_numbers method
def test_get_random_numbers_one(numbers):
    assert False == isinstance(numbers.get_random_numbers((1, 10), 1), list)

def test_get_random_numbers_multiple(numbers):
    assert True == isinstance(numbers.get_random_numbers((1, 10), 2), list)

def test_get_random_numbers_neither(numbers):
    assert None == numbers.get_random_numbers((1, 10), 0)

def test_get_random_numbers_arguments_wrong_order(numbers):
    with pytest.raises(TypeError):
        numbers.get_random_numbers(1, (1, 10))

def test_get_random_numbers_no_arguments_raises_error(numbers):
    with pytest.raises(TypeError):
        numbers.get_random_numbers()

def test_get_random_numbers_too_many_arguments_raises_error(numbers):
    with pytest.raises(TypeError):
        numbers.get_random_numbers((1, 10), 1, 2)



### NumberInfo Object Tests

@pytest.fixture
def info(numbers):
    return numbers._info


# Test _is_factor method
def test_is_factor_positive_yes_different(info):
    assert True == info._is_factor(21, 7)

def test_is_factor_positive_no_different(info):
    assert False == info._is_factor(10, 7)

def test_is_factor_positive_yes_same(info):
    assert True == info._is_factor(7, 7)

def test_is_factor_positive_no_zero_numerator(info):
    assert True == info._is_factor(0, 7)

def test_is_factor_positive_no_zero_denominator(info):
    assert False == info._is_factor(7, 0)

def test_is_factor_negative_yes(info):
    assert True == info._is_factor(-4, -2)

def test_is_factor_negative_no(info):
    assert False == info._is_factor(-5, -2)

def test_is_factor_negative_positive_yes(info):
    assert True == info._is_factor(-8, 1)

def test_is_factor_negative_positive_no(info):
    assert False == info._is_factor(-8, 3)

def test_is_factor_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_factor()

def test_is_factor_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_factor(20, 10, 5)


# Test _get_factors method
def test_get_factors_prime(info):
    assert [1, 2] == info._get_factors(2)

def test_get_factors_perfect_square(info):
    assert [1, 3, 9] == info._get_factors(9)

def test_get_factors_two_prime_no_repeats(info):
    assert [1, 2, 3, 6] == info._get_factors(6)

def test_get_factors_two_prime_repeats(info):
    assert [1, 2, 3, 6, 9, 18] == info._get_factors(18)

def test_get_factors_perfect_cube(info):
    assert [1, 5, 25, 125] == info._get_factors(125)

def test_get_factors_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_factors()

def test_get_factors_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_factors(20, 10)


# Test _is_prime method
def test_is_prime_yes_positive(info):
    assert True == info._is_prime(5)

def test_is_prime_no_positive(info):
    assert False == info._is_prime(6)

def test_is_prime_no_one(info):
    assert False == info._is_prime(1)

def test_is_prime_no_zero(info):
    assert False == info._is_prime(0)

def test_is_prime_no_negative(info):
    assert False == info._is_prime(-1)

def test_is_prime_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_prime()

def test_is_prime_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_prime(20, 10)


# Test _get_prime_factors method
def test_get_prime_factors_two_no_repeats(info):
    assert [2, 5] == info._get_prime_factors(10)

def test_get_prime_factors_three_no_repeats(info):
    assert [2, 3, 11] == info._get_prime_factors(66)

def test_get_prime_factors_perfect_cube(info):
    assert [3] == info._get_prime_factors(27)

def test_get_prime_factors_two_repeats(info):
    assert [2, 3] == info._get_prime_factors(72)

def test_get_prime_factors_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_prime_factors()

def test_get_prime_factors_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_prime_factors(20, 10)


# Test _get_digits method
def test_get_digits_positive_no_repeats(info):
    assert [6, 8] == info._get_digits(68)

def test_get_digits_positive_repeats(info):
    assert [7, 7] == info._get_digits(77)

def test_get_digits_positive_zero(info):
    assert [1, 0] == info._get_digits(10)

def test_get_digits_positive_three_digits(info):
    assert [3, 6, 1] == info._get_digits(361)

def test_get_digits_negative(info):
    assert [4, 6] == info._get_digits(-46)

def test_get_digits_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_digits()

def test_get_digits_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_digits(20, 10)


# Test _get_digit_factor_count method
def test_get_digit_factor_count_all_digits(info):
    assert 2 == info._get_digit_factor_count(36)

def test_get_digit_factor_count_one_digit(info):
    assert 1 == info._get_digit_factor_count(63)

def test_get_digit_factor_count_no_digits(info):
    assert 0 == info._get_digit_factor_count(27)

def test_get_digit_factor_count_zero(info):
    assert 2 == info._get_digit_factor_count(105)

def test_get_digit_factor_count_repeats(info):
    assert 3 == info._get_digit_factor_count(888)

def test_get_digit_factor_count_negative(info):
    assert 1 == info._get_digit_factor_count(-64)

def test_get_digit_factor_count_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_digit_factor_count()

def test_get_digit_factor_count_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._get_digit_factor_count(20, 10)


# Test _is_perfect_square method
def test_is_perfect_square_yes_positive(info):
    assert True == info._is_perfect_square(49)

def test_is_perfect_square_no_positive(info):
    assert False == info._is_perfect_square(27)

def test_is_perfect_square_yes_zero(info):
    assert True == info._is_perfect_square(0)

def test_is_perfect_square_yes_one(info):
    assert True == info._is_perfect_square(1)

def test_is_perfect_square_no_negative(info):
    assert False == info._is_perfect_square(-4)

def test_is_perfect_square_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_perfect_square()

def test_is_perfect_square_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_perfect_square(20, 10)


# Test _is_perfect_cube method
def test_is_perfect_cube_yes_positive(info):
    assert True == info._is_perfect_cube(8)

def test_is_perfect_cube_no_positive(info):
    assert False == info._is_perfect_cube(16)

def test_is_perfect_cube_yes_negative(info):
    assert True == info._is_perfect_cube(-27)

def test_is_perfect_cube_no_negative(info):
    assert False == info._is_perfect_cube(-900)

def test_is_perfect_cube_yes_zero(info):
    assert True == info._is_perfect_cube(0)

def test_is_perfect_cube_yes_one(info):
    assert True == info._is_perfect_cube(1)

def test_is_perfect_cube_no_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_perfect_cube()

def test_is_perfect_cube_too_many_arguments_raises_error(info):
    with pytest.raises(TypeError):
        info._is_perfect_cube(20, 10)


# Test get_number_info method
def test_get_number_info_is_factor(numbers):
    assert True == numbers.get_number_info('is factor', 21, 7)

def test_get_number_info_get_factors(numbers):
    result = numbers.get_number_info('factors', 12)
    assert True == isinstance(result, list)
    assert [1, 2, 3, 4, 6, 12] == result

def test_get_number_info_is_prime(numbers):
    result = numbers.get_number_info('is prime', 13)
    assert True == isinstance(result, bool)
    assert True == result

def test_get_number_info_get_prime_factors(numbers):
    result = numbers.get_number_info('prime factors', 12)
    assert True == isinstance(result, list)
    assert [2, 3] == result

def test_get_number_info_get_digits(numbers):
    result = numbers.get_number_info('digits', 12)
    assert True == isinstance(result, list)
    assert [1, 2] == result

def test_get_number_info_get_digit_factor_count(numbers):
    assert 2 == numbers.get_number_info('digit factors', 36)

def test_get_number_info_is_perfect_square(numbers):
    result = numbers.get_number_info('is perfect square', 4)
    assert True == isinstance(result, bool)
    assert True == result

def test_get_number_info_is_perfect_cube(numbers):
    result = numbers.get_number_info('is perfect cube', 27)
    assert True == isinstance(result, bool)
    assert True == result

def test_get_number_info_first_argument_not_found(numbers):
    with pytest.raises(KeyError):
        numbers.get_number_info('factor', 21, 7)

def test_get_number_info_no_arguments_raises_error(numbers):
    with pytest.raises(TypeError):
        numbers.get_number_info()


def test_settings_version_end():
    objects_fake_global = objects_fake_global_dict["easy"]
    settings = objects_fake_global.get_object("settings")
    assert "easy" == settings.get_setting("level of difficulty name")

