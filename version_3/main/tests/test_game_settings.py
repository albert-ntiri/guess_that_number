import pytest
from main.tests.test_number import numbers
from main.resources.infrastructure.data import LevelOfDifficultyTypes
from main.game.game_settings import GameSettings



@pytest.fixture
def level_types():
    return LevelOfDifficultyTypes()

@pytest.fixture
def settings_easy(numbers, level_types):
    settings_easy = GameSettings(numbers, level_types.get_level_obj("easy"))
    yield settings_easy
    settings_easy._settings.clear()

@pytest.fixture
def settings_medium(numbers, level_types):
    settings_medium = GameSettings(numbers, level_types.get_level_obj("medium"))
    yield settings_medium
    settings_medium._settings.clear()

@pytest.fixture
def settings_hard(numbers, level_types):
    settings_hard = GameSettings(numbers, level_types.get_level_obj("hard"))
    yield settings_hard
    settings_hard._settings.clear()

@pytest.fixture
def settings_custom(numbers, level_types):
    settings_custom = GameSettings(numbers, level_types.get_level_obj("custom"))
    yield settings_custom
    settings_custom._settings.clear()


# Test get_setting method
def test_get_setting_number(settings_easy):
    settings_easy._settings = {"number": 1}
    assert 1 == settings_easy.get_setting("number")

def test_get_setting_text(settings_easy):
    settings_easy._settings = {"text": "test"}
    assert "test" == settings_easy.get_setting("text")

def test_get_setting_tuple(settings_easy):
    settings_easy._settings = {"tuple": (1, 5)}
    assert (1, 5) == settings_easy.get_setting("tuple")

def test_get_setting_no_arguments_raises_error(settings_easy):
    with pytest.raises(TypeError):
        settings_easy.get_setting()

def test_get_setting_too_many_arguments_raises_error(settings_easy):
    with pytest.raises(TypeError):
        settings_easy.get_setting("text", "extra")


# Test _add_level_to_settings_dict method
def test_add_level_to_settings_dict_easy_id(settings_easy):
    settings_easy._add_level_to_settings_dict()
    assert 1 == settings_easy.get_setting("level of difficulty id")

def test_add_level_to_settings_dict_easy_name(settings_easy):
    settings_easy._add_level_to_settings_dict()
    assert "easy" == settings_easy.get_setting("level of difficulty name")

def test_add_level_to_settings_dict_easy_number_range(settings_easy):
    settings_easy._add_level_to_settings_dict()
    assert (1, 10) == settings_easy.get_setting("number range")

def test_add_level_to_settings_dict_easy_penalty(settings_easy):
    settings_easy._add_level_to_settings_dict()
    assert 10 == settings_easy.get_setting("penalty")

def test_add_level_to_settings_dict_medium_id(settings_medium):
    settings_medium._add_level_to_settings_dict()
    assert 2 == settings_medium.get_setting("level of difficulty id")

def test_add_level_to_settings_dict_medium_name(settings_medium):
    settings_medium._add_level_to_settings_dict()
    assert "medium" == settings_medium.get_setting("level of difficulty name")

def test_add_level_to_settings_dict_medium_number_range(settings_medium):
    settings_medium._add_level_to_settings_dict()
    assert (1, 100) == settings_medium.get_setting("number range")

def test_add_level_to_settings_dict_medium_penalty(settings_medium):
    settings_medium._add_level_to_settings_dict()
    assert 20 == settings_medium.get_setting("penalty")

def test_add_level_to_settings_dict_hard_id(settings_hard):
    settings_hard._add_level_to_settings_dict()
    assert 3 == settings_hard.get_setting("level of difficulty id")

def test_add_level_to_settings_dict_hard_name(settings_hard):
    settings_hard._add_level_to_settings_dict()
    assert "hard" == settings_hard.get_setting("level of difficulty name")

def test_add_level_to_settings_dict_hard_number_range(settings_hard):
    settings_hard._add_level_to_settings_dict()
    assert (1, 1000) == settings_hard.get_setting("number range")

def test_add_level_to_settings_dict_hard_penalty(settings_hard):
    settings_hard._add_level_to_settings_dict()
    assert 25 == settings_hard.get_setting("penalty")

def test_add_level_to_settings_dict_hard_id(settings_custom):
    settings_custom._add_level_to_settings_dict()
    assert 4 == settings_custom.get_setting("level of difficulty id")

def test_add_level_to_settings_dict_hard_name(settings_custom):
    settings_custom._add_level_to_settings_dict()
    assert "custom" == settings_custom.get_setting("level of difficulty name")

def test_add_level_to_settings_dict_hard_number_range(settings_custom):
    settings_custom._add_level_to_settings_dict()
    assert None == settings_custom.get_setting("number range")

def test_add_level_to_settings_dict_hard_penalty(settings_custom):
    settings_custom._add_level_to_settings_dict()
    assert 10 == settings_custom.get_setting("penalty")

def test_add_level_to_settings_dict_too_many_arguments_raises_error(settings_easy):
    with pytest.raises(TypeError):
        settings_easy._add_level_to_settings_dict("extra")


# Test _set_range method
def test_set_range_valid_positive(settings_custom):
    settings_custom._set_range("1", "5")
    assert (1, 5) == settings_custom.get_setting("number range")

def test_set_range_valid_negative(settings_custom):
    settings_custom._set_range("-5", "-1")
    assert (-5, -1) == settings_custom.get_setting("number range")

def test_set_range_valid_zero(settings_custom):
    settings_custom._set_range("0", "10")
    assert (0, 10) == settings_custom.get_setting("number range")

def test_set_range_error_comparison(settings_custom):
    assert "comparison" == settings_custom._set_range("5", "1")

def test_set_range_error_invalid(settings_custom):
    assert "invalid" == settings_custom._set_range("5", "")

def test_set_range_blank_easy(settings_easy):
    settings_easy._set_range("", "")
    assert (1, 10) == settings_easy.get_setting("number range")

def test_set_range_blank_medium(settings_medium):
    settings_medium._set_range("", "")
    assert (1, 100) == settings_medium.get_setting("number range")

def test_set_range_blank_hard(settings_hard):
    settings_hard._set_range("", "")
    assert (1, 1000) == settings_hard.get_setting("number range")

def test_set_range_no_arguments_raises_error(settings_custom):
    with pytest.raises(TypeError):
        settings_custom._set_range()

def test_set_range_too_many_arguments_raises_error(settings_custom):
    with pytest.raises(TypeError):
        settings_custom._set_range("1", "5", "extra")


# Test _set_active_flag method
def test_set_active_flag_default(settings_easy):
    assert False == settings_easy.active

def test_set_active_flag(settings_easy):
    settings_easy._set_active_flag()
    assert True == settings_easy.active

def test_set_active_flag_too_many_arguments_raises_error(settings_easy):
    with pytest.raises(TypeError):
        settings_easy._set_active_flag("extra")


# Test _set_winning_number method
@pytest.fixture
def winning_number_easy(settings_easy):
    settings_easy._set_winning_number()
    return settings_easy._winning_number

def test_set_winning_number_easy_in_range(winning_number_easy):
    assert winning_number_easy in range(1, 11)

def test_set_winning_number_easy_matches_dict(settings_easy, winning_number_easy):
    assert winning_number_easy == settings_easy.get_setting("winning number")

@pytest.fixture
def winning_number_medium(settings_medium):
    settings_medium._set_winning_number()
    return settings_medium._winning_number

def test_set_winning_number_medium_in_range(winning_number_medium):
    assert winning_number_medium in range(1, 101)

def test_set_winning_number_medium_matches_dict(settings_medium, winning_number_medium):
    assert winning_number_medium == settings_medium.get_setting("winning number")

@pytest.fixture
def winning_number_hard(settings_hard):
    settings_hard._set_winning_number()
    return settings_hard._winning_number

def test_set_winning_number_hard_in_range(winning_number_hard):
    assert winning_number_hard in range(1, 1001)

def test_set_winning_number_hard_matches_dict(settings_hard, winning_number_hard):
    assert winning_number_hard == settings_hard.get_setting("winning number")

@pytest.fixture
def winning_number_custom(settings_custom):
    settings_custom._set_range("1", "5")
    settings_custom._set_winning_number()
    return settings_custom._winning_number

def test_set_winning_number_custom_in_range(winning_number_custom):
    assert winning_number_custom in range(1, 6)

def test_set_winning_number_custom_matches_dict(settings_custom, winning_number_custom):
    assert winning_number_custom == settings_custom.get_setting("winning number")

def test_set_winning_number_too_many_arguments_raises_error(settings_easy):
    with pytest.raises(TypeError):
        settings_easy._set_winning_number("extra")


# Test set_game_settings method
@pytest.fixture
def easy_settings_dict(settings_easy):
    settings_easy.set_game_settings("", "")
    return settings_easy._settings

def test_set_game_settings_easy_active(settings_easy, easy_settings_dict):
    assert True == settings_easy.active

def test_set_game_settings_easy_level_id(easy_settings_dict):
    assert 1 == easy_settings_dict["level of difficulty id"]

def test_set_game_settings_easy_level_name(easy_settings_dict):
    assert "easy" == easy_settings_dict["level of difficulty name"]

def test_set_game_settings_easy_number_range(easy_settings_dict):
    assert (1, 10) == easy_settings_dict["number range"]

def test_set_game_settings_easy_penalty(easy_settings_dict):
    assert 10 == easy_settings_dict["penalty"]

def test_set_game_settings_easy_winning_number_in_range(easy_settings_dict):
    assert easy_settings_dict["winning number"] in range(1, 11)

def test_set_game_settings_easy_winning_number_matches_dict(settings_easy, easy_settings_dict):
    assert settings_easy._winning_number == easy_settings_dict["winning number"]

@pytest.fixture
def medium_settings_dict(settings_medium):
    settings_medium.set_game_settings("", "")
    return settings_medium._settings

def test_set_game_settings_medium_active(settings_medium, medium_settings_dict):
    assert True == settings_medium.active

def test_set_game_settings_medium_level_id(medium_settings_dict):
    assert 2 == medium_settings_dict["level of difficulty id"]

def test_set_game_settings_medium_level_name(medium_settings_dict):
    assert "medium" == medium_settings_dict["level of difficulty name"]

def test_set_game_settings_medium_number_range(medium_settings_dict):
    assert (1, 100) == medium_settings_dict["number range"]

def test_set_game_settings_medium_penalty(medium_settings_dict):
    assert 20 == medium_settings_dict["penalty"]

def test_set_game_settings_medium_winning_number_in_range(medium_settings_dict):
    assert medium_settings_dict["winning number"] in range(1, 101)

def test_set_game_settings_medium_winning_number_matches_dict(settings_medium, medium_settings_dict):
    assert settings_medium._winning_number == medium_settings_dict["winning number"]

@pytest.fixture
def hard_settings_dict(settings_hard):
    settings_hard.set_game_settings("", "")
    return settings_hard._settings

def test_set_game_settings_hard_active(settings_hard, hard_settings_dict):
    assert True == settings_hard.active

def test_set_game_settings_hard_level_id(hard_settings_dict):
    assert 3 == hard_settings_dict["level of difficulty id"]

def test_set_game_settings_hard_level_name(hard_settings_dict):
    assert "hard" == hard_settings_dict["level of difficulty name"]

def test_set_game_settings_hard_number_range(hard_settings_dict):
    assert (1, 1000) == hard_settings_dict["number range"]

def test_set_game_settings_hard_penalty(hard_settings_dict):
    assert 25 == hard_settings_dict["penalty"]

def test_set_game_settings_hard_winning_number_in_range(hard_settings_dict):
    assert hard_settings_dict["winning number"] in range(1, 1001)

def test_set_game_settings_hard_winning_number_matches_dict(settings_hard, hard_settings_dict):
    assert settings_hard._winning_number == hard_settings_dict["winning number"]

@pytest.fixture
def custom_settings_dict(settings_custom):
    settings_custom.set_game_settings("20", "35")
    return settings_custom._settings

def test_set_game_settings_custom_active(settings_custom, custom_settings_dict):
    assert True == settings_custom.active

def test_set_game_settings_custom_level_id(custom_settings_dict):
    assert 4 == custom_settings_dict["level of difficulty id"]

def test_set_game_settings_custom_level_name(custom_settings_dict):
    assert "custom" == custom_settings_dict["level of difficulty name"]

def test_set_game_settings_custom_number_range(custom_settings_dict):
    assert (20, 35) == custom_settings_dict["number range"]

def test_set_game_settings_custom_penalty(custom_settings_dict):
    assert 10 == custom_settings_dict["penalty"]

def test_set_game_settings_custom_winning_number_in_range(custom_settings_dict):
    assert custom_settings_dict["winning number"] in range(20, 36)

def test_set_game_settings_custom_winning_number_matches_dict(settings_custom, custom_settings_dict):
    assert settings_custom._winning_number == custom_settings_dict["winning number"]

def test_set_game_settings_no_arguments_raises_error(settings_custom):
    with pytest.raises(TypeError):
        settings_custom.set_game_settings()

def test_set_game_settings_too_many_arguments_raises_error(settings_custom):
    with pytest.raises(TypeError):
        settings_custom.set_game_settings("1", "5", "extra")

