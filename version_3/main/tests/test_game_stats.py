import pytest
from main.tests.tests_setup import objects_fake_global_dict, ObjectManagerFake, numbers
from main.resources.infrastructure.data import LevelOfDifficultyTypes
from main.game.game_settings import GameSettings
from main.game.game_stats import *



### Object Manager Setup

objects_fake_global_easy = objects_fake_global_dict["easy"]
objects_fake_global_medium = objects_fake_global_dict["medium"]
objects_fake_global_hard = objects_fake_global_dict["hard"]


def test_settings_version_beginning():
    objects_fake_global = objects_fake_global_dict["easy"]
    settings = objects_fake_global.get_object("settings")
    assert "easy" == settings.get_setting("level of difficulty name")

### Stat Tests

class StatStub(Stat):
    def __init__(self, objects=None):
        super().__init__(objects)
    
    def _get_new_value(self):
        return 3
    
    def _set_default_value(self):
        return 2

@pytest.fixture
def stat_stub():
    return StatStub()


# Test value property
def test_value_default(stat_stub):
    assert 0 == stat_stub.value

def test_value_set_new_value_int(stat_stub):
    stat_stub.value = 1
    assert 1 == stat_stub.value

def test_value_set_new_value_decimal(stat_stub):
    stat_stub.value = .3
    assert .3 == stat_stub.value


# Test get_name method
def test_get_name(stat_stub):
    assert "" == stat_stub.get_name()

def test_get_name_too_many_arguments_raises_error(stat_stub):
    with pytest.raises(TypeError):
        stat_stub.get_name("extra")


# Test update_stat method
def test_update_stat_default(stat_stub):
    stat_stub.update_stat()
    assert 2 == stat_stub.value

def test_update_stat_new_value(stat_stub):
    stat_stub.value = 5
    stat_stub.update_stat()
    assert 3 == stat_stub.value

def test_update_stat_too_many_arguments_raises_error(stat_stub):
    with pytest.raises(TypeError):
        stat_stub.update_stat("extra")



### GameStat Tests

@pytest.fixture
def game_stat_fake_easy():
    return GameStat(objects_fake_global_easy)

@pytest.fixture
def game_stat_fake_medium():
    return GameStat(objects_fake_global_medium)

@pytest.fixture
def game_stat_fake_hard():
    return GameStat(objects_fake_global_hard)


# Test _set_default_value method
def test_set_default_value_easy(game_stat_fake_easy):
    game_stat_fake_easy._set_default_value()
    assert 10 == game_stat_fake_easy._penalty

def test_set_default_value_medium(game_stat_fake_medium):
    game_stat_fake_medium._set_default_value()
    assert 20 == game_stat_fake_medium._penalty

def test_set_default_value_hard(game_stat_fake_hard):
    game_stat_fake_hard._set_default_value()
    assert 25 == game_stat_fake_hard._penalty

def test_set_default_value_too_many_arguments_raises_error(game_stat_fake_easy):
    with pytest.raises(TypeError):
        game_stat_fake_easy._set_default_value("extra")



### GameScore Tests

@pytest.fixture
def game_score_fake_easy():
    return GameScore(objects_fake_global_easy)

@pytest.fixture
def game_score_fake_medium():
    return GameScore(objects_fake_global_medium)

@pytest.fixture
def game_score_fake_hard():
    return GameScore(objects_fake_global_hard)


# Test _get_new_value method
def test_get_new_value_score_easy(game_score_fake_easy):
    game_score_fake_easy._value = 100
    game_score_fake_easy._penalty = 10
    assert 90 == game_score_fake_easy._get_new_value()

def test_get_new_value_score_medium(game_score_fake_medium):
    game_score_fake_medium._value = 100
    game_score_fake_medium._penalty = 20
    assert 80 == game_score_fake_medium._get_new_value()

def test_get_new_value_score_hard(game_score_fake_hard):
    game_score_fake_hard._value = 100
    game_score_fake_hard._penalty = 25
    assert 75 == game_score_fake_hard._get_new_value()


# Test _set_default_value method
def test_set_default_value_score_easy(game_score_fake_easy):
    game_score_fake_easy._set_default_value()
    assert 100 == game_score_fake_easy._set_default_value()



### GuessesRemaining Tests

@pytest.fixture
def guesses_remaining_fake_easy():
    return GuessesRemaining(objects_fake_global_easy)

@pytest.fixture
def guesses_remaining_fake_medium():
    return GuessesRemaining(objects_fake_global_medium)

@pytest.fixture
def guesses_remaining_fake_hard():
    return GuessesRemaining(objects_fake_global_hard)


# Test _get_new_value method
def test_get_new_value_guesses_remaining_easy(guesses_remaining_fake_easy):
    guesses_remaining_fake_easy._value = 10
    assert 9 == guesses_remaining_fake_easy._get_new_value()

def test_get_new_value_guesses_remaining_medium(guesses_remaining_fake_medium):
    guesses_remaining_fake_medium._value = 5
    assert 4 == guesses_remaining_fake_medium._get_new_value()

def test_get_new_value_guesses_remaining_hard(guesses_remaining_fake_hard):
    guesses_remaining_fake_hard._value = 4
    assert 3 == guesses_remaining_fake_hard._get_new_value()


# Test _set_default_value method
def test_set_default_value_guesses_remaining_easy(guesses_remaining_fake_easy):
    guesses_remaining_fake_easy._set_default_value()
    assert 10 == guesses_remaining_fake_easy._set_default_value()

def test_set_default_value_guesses_remaining_medium(guesses_remaining_fake_medium):
    guesses_remaining_fake_medium._set_default_value()
    assert 5 == guesses_remaining_fake_medium._set_default_value()

def test_set_default_value_guesses_remaining_hard(guesses_remaining_fake_hard):
    guesses_remaining_fake_hard._set_default_value()
    assert 4 == guesses_remaining_fake_hard._set_default_value()



### GameStatsManager Tests

@pytest.fixture
def game_stats_fake_easy():
    return GameStatsManager(objects_fake_global_easy)


# Test update_game_stats method
def test_update_game_stats_score_easy(game_stats_fake_easy):
    game_stats_fake_easy.update_game_stats()
    assert 100 == game_stats_fake_easy._score.value

def test_update_game_stats_score_easy_updated_twice(game_stats_fake_easy):
    game_stats_fake_easy.update_game_stats()
    game_stats_fake_easy.update_game_stats()
    assert 90 == game_stats_fake_easy._score.value

def test_update_game_stats_guesses_remaining_easy(game_stats_fake_easy):
    game_stats_fake_easy.update_game_stats()
    assert 10 == game_stats_fake_easy._guesses_remaining.value

def test_update_game_stats_guesses_remaining_easy_updated_twice(game_stats_fake_easy):
    game_stats_fake_easy.update_game_stats()
    game_stats_fake_easy.update_game_stats()
    assert 9 == game_stats_fake_easy._guesses_remaining.value


# Test get_value method
def test_get_value_score_easy(game_stats_fake_easy):
    game_stats_fake_easy.update_game_stats()
    assert 100 == game_stats_fake_easy.get_value("score")

def test_get_value_guesses_remaining_easy(game_stats_fake_easy):
    game_stats_fake_easy.update_game_stats()
    assert 10 == game_stats_fake_easy.get_value("guesses remaining")


def test_settings_version_end():
    objects_fake_global = objects_fake_global_dict["easy"]
    settings = objects_fake_global.get_object("settings")
    assert "easy" == settings.get_setting("level of difficulty name")

