import pytest
from main.tests.tests_setup import objects_fake_global_dict, ObjectManagerFake, GameSettings
from main.tests.test_db import sqlite_db_fake, test_db_path
from main.game.hint_manager import *
from resources.variables.create_db_queries import non_type_tables



### Object Manager Setup

objects_fake_global = objects_fake_global_dict["easy"]
numbers = objects_fake_global.get_object("numbers")
data = objects_fake_global.get_object("data")


### HintManager Tests

@pytest.fixture
def hints_fake(sqlite_db_fake, test_db_path):
    for table in non_type_tables:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)
    hints_fake = HintManager(objects_fake_global)
    yield hints_fake
    for hints in [hints_fake._hint_pool, hints_fake._relevant_hints, hints_fake._redundant_hints, hints_fake._hints_given]:
        hints.clear()
    for table in non_type_tables:
        sqlite_db_fake.run_query(f"DELETE FROM {table};", _db_path=test_db_path)


# Test _update_hint_pool method
def test_update_hint_pool(hints_fake):
    hints_fake._hint_pool = []
    hints_fake._relevant_hints = ["relevant hint"]
    hints_fake._redundant_hints = ["redundant hint"]
    hints_fake._update_hint_pool()
    assert ["relevant hint", "redundant hint"] == hints_fake._hint_pool

def test_update_hint_pool_too_many_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake._update_hint_pool("extra")


# Test _get_hint_from_list method
@pytest.fixture
def test_hint_list():
    return ["hint 1", "hint 2", "hint 3"]

def test_get_hint_from_list_hint_in_original_list(hints_fake, test_hint_list):
    hint_list = test_hint_list.copy()
    hint = hints_fake._get_hint_from_list(hint_list)
    assert hint in test_hint_list

def test_get_hint_from_list_hint_not_in_updated_list(hints_fake, test_hint_list):
    hint_list = test_hint_list.copy()
    hint = hints_fake._get_hint_from_list(hint_list)
    assert hint not in hint_list

def test_get_hint_from_list_updated_list_has_1_fewer_items(hints_fake, test_hint_list):
    hint_list = test_hint_list.copy()
    hint = hints_fake._get_hint_from_list(hint_list)
    assert len(hint_list) == len(test_hint_list) - 1

def test_get_hint_from_list_empty(hints_fake):
    with pytest.raises(ValueError):
        hints_fake._get_hint_from_list([])

def test_get_hint_from_list_no_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake._get_hint_from_list()

def test_get_hint_from_list_too_many_arguments_raises_error(hints_fake, test_hint_list):
    with pytest.raises(TypeError):
        hints_fake._get_hint_from_list(test_hint_list, "extra")


# Test _select_hint method
def test_select_hint_relevant(hints_fake):
    hints_fake._relevant_hints = ["relevant hint 1", "relevant hint 2"]
    hints_fake._redundant_hints = ["redundant hint 1", "redundant hint 2"]
    hints_fake._update_hint_pool()
    hint = hints_fake._select_hint()
    assert hint in ["relevant hint 1", "relevant hint 2"]

def test_select_hint_redundant(hints_fake):
    hints_fake._relevant_hints = []
    hints_fake._redundant_hints = ["redundant hint 1", "redundant hint 2"]
    hints_fake._update_hint_pool()
    hint = hints_fake._select_hint()
    assert hint in ["redundant hint 1", "redundant hint 2"]

def test_select_hint_too_many_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake._select_hint("extra")


# Test _get_relevant_hints method
@pytest.fixture
def mock_concepts_four():
    return ConceptManager(4, numbers, None, data)

def test_get_relevant_hints_redundant_hints_added(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 2 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hints_fake._get_relevant_hints(mock_concepts_four, _check_db=False)
    assert "Nice try!  Hint: It is a perfect square." in hints_fake._redundant_hints

def test_get_relevant_hints_relevant_hints_reduced(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 2 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hints_fake._get_relevant_hints(mock_concepts_four, _check_db=False)
    assert "Nice try!  Hint: It is a perfect square." not in hints_fake._relevant_hints

def test_get_relevant_hints_relevant_hints_correct_length(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 2 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hints_fake._get_relevant_hints(mock_concepts_four, _check_db=False)
    assert 4 == len(hints_fake._relevant_hints)

def test_get_relevant_hints_multiple_redundant_hints_added(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 4 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hints_fake._get_relevant_hints(mock_concepts_four, _check_db=False)
    assert "Nice try!  Hint: It is a perfect square." in hints_fake._redundant_hints
    assert "Nice try!  Hint: 4 is a multiple." in hints_fake._redundant_hints

def test_get_relevant_hints_multiple_relevant_hints_reduced(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 4 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hints_fake._get_relevant_hints(mock_concepts_four, _check_db=False)
    assert "Nice try!  Hint: It is a perfect square." not in hints_fake._relevant_hints
    assert "Nice try!  Hint: 4 is a multiple." not in hints_fake._relevant_hints

def test_get_relevant_hints_multiple_relevant_hints_correct_length(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 4 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hints_fake._get_relevant_hints(mock_concepts_four, _check_db=False)
    assert 3 == len(hints_fake._relevant_hints)

def test_get_relevant_hints_no_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake._get_relevant_hints()

def test_get_relevant_hints_too_many_arguments_raises_error(hints_fake, mock_concepts_four):
    with pytest.raises(TypeError):
        hints_fake._get_relevant_hints(mock_concepts_four, False, "extra")


# Test get_hints method
def test_get_hints_pool(hints_fake):
    hints_fake._relevant_hints = ["relevant hint"]
    hints_fake._redundant_hints = ["redundant hint"]
    hints_fake._update_hint_pool()
    hints_fake._hints_given = ["hints given"]
    hint_list = hints_fake.get_hints("pool")
    assert hint_list == hints_fake._hint_pool

def test_get_hints_relevant(hints_fake):
    hints_fake._relevant_hints = ["relevant hint"]
    hints_fake._redundant_hints = ["redundant hint"]
    hints_fake._update_hint_pool()
    hints_fake._hints_given = ["hints given"]
    hint_list = hints_fake.get_hints("relevant")
    assert hint_list == hints_fake._relevant_hints

def test_get_hints_redundant(hints_fake):
    hints_fake._relevant_hints = ["relevant hint"]
    hints_fake._redundant_hints = ["redundant hint"]
    hints_fake._update_hint_pool()
    hints_fake._hints_given = ["hints given"]
    hint_list = hints_fake.get_hints("redundant")
    assert hint_list == hints_fake._redundant_hints

def test_get_hints_given(hints_fake):
    hints_fake._relevant_hints = ["relevant hint"]
    hints_fake._redundant_hints = ["redundant hint"]
    hints_fake._update_hint_pool()
    hints_fake._hints_given = ["hints given"]
    hint_list = hints_fake.get_hints("given")
    assert hint_list == hints_fake._hints_given

def test_get_hints_not_found(hints_fake):
    hints_fake._relevant_hints = ["relevant hint"]
    hints_fake._redundant_hints = ["redundant hint"]
    hints_fake._update_hint_pool()
    hints_fake._hints_given = ["hints given"]
    hint_list = hints_fake.get_hints("not found")
    assert hint_list == None

def test_get_hints_copy(hints_fake):
    hints_fake._relevant_hints = ["relevant hint"]
    hints_fake._redundant_hints = ["redundant hint"]
    hints_fake._update_hint_pool()
    hints_fake._hints_given = ["hints given"]
    hint_list = hints_fake.get_hints("pool")
    hint_list.remove("redundant hint")
    assert hint_list != hints_fake._hint_pool

def test_get_hints_no_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake.get_hints()

def test_get_hints_too_many_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake.get_hints("given", "extra")


# Test get_hint_count method
def test_get_hint_count(hints_fake):
    hints_fake._hint_pool = ["relevant hint", "redundant hint"]
    assert 2 == hints_fake.get_hint_count("pool")

def test_get_hint_count_no_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake.get_hint_count()

def test_get_hint_count_too_many_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake.get_hint_count("pool", "extra")


# Test get_new_hint method
def test_get_new_hint_hint_in_original_list(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 2 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    original_hint_list = hints_fake._hint_pool.copy()
    hint = hints_fake.get_new_hint(mock_concepts_four, 4, _check_db=False)
    assert hint in original_hint_list

def test_get_new_hint_hint_added_to_hints_given(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = [
        "Nice try!  Hint: It is a perfect square.",
        "Nice try!  Hint: It is a perfect cube.",
        "Nice try!  Hint: It is an odd number.",
        "Nice try!  Hint: 1 is a multiple.",
        "Nice try!  Hint: 2 is a multiple."
        ]
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    original_hint_list = hints_fake._hint_pool.copy()
    hint = hints_fake.get_new_hint(mock_concepts_four, 4, _check_db=False)
    assert hint in hints_fake._hints_given

def test_get_new_hint_hint_pool_empty_correct_hint(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = []
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hint = hints_fake.get_new_hint(mock_concepts_four, 15, _check_db=False)
    assert "Nice try!  Lower." == hint

def test_get_new_hint_hint_pool_empty_hints_given_not_updated(hints_fake, mock_concepts_four):
    hints_fake._relevant_hints = []
    hints_fake._redundant_hints = []
    hints_fake._update_hint_pool()
    hint = hints_fake.get_new_hint(mock_concepts_four, 4, _check_db=False)
    assert not hints_fake._hints_given

def test_get_new_hint_no_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake.get_new_hint()

def test_get_new_hint_too_many_arguments_raises_error(hints_fake, mock_concepts_four):
    with pytest.raises(TypeError):
        hints_fake.get_new_hint(mock_concepts_four, 4, False, "extra")


# Test get_concepts method
def test_get_concepts_object_of_ConceptManager(hints_fake):
    concepts = hints_fake.get_concepts(1, _db=False)
    assert isinstance(concepts, ConceptManager)

def test_get_concepts_correct_number(hints_fake):
    concepts = hints_fake.get_concepts(1, _db=False)
    assert 1 == concepts._number

def test_get_concepts_store_object(hints_fake):
    concepts = hints_fake.get_concepts(1, _db=False, store_object=True)
    concepts_stored = objects_fake_global.get_object("game_concepts")
    assert concepts_stored._number == concepts._number
    del objects_fake_global._object_dict["game_concepts"]

def test_get_concepts_no_arguments_raises_error(hints_fake):
    with pytest.raises(TypeError):
        hints_fake.get_concepts()

def test_get_concepts_too_many_arguments_raises_error(hints_fake, mock_concepts_four):
    with pytest.raises(TypeError):
        hints_fake.get_concepts(mock_concepts_four, False, False, "extra")


# Test get_hint_list method
def test_get_hint_list_more_than_two_hints(hints_fake):
    hints_fake.get_hint_list(_db=False)
    assert len(hints_fake._hint_pool) > 2

def test_get_hint_list_two_multiple_hints(hints_fake):
    hints_fake.get_hint_list(_db=False)
    multiple_hints = [hint for hint in hints_fake._hint_pool if "multiple" in hint]
    assert 2 == len(multiple_hints)

def test_get_hint_list_relevant_hints_matches_hint_pool(hints_fake):
    hints_fake.get_hint_list(_db=False)
    assert hints_fake._relevant_hints == hints_fake._hint_pool

def test_get_hint_list_too_many_arguments_raises_error(hints_fake, mock_concepts_four):
    with pytest.raises(TypeError):
        hints_fake.get_hint_list(False, "extra")



### Tests Incorporating DB


# Test get_concepts method
def test_get_concepts_db_object_of_ConceptManager(hints_fake):
    concepts = hints_fake.get_concepts(1)
    assert isinstance(concepts, ConceptManager)

def test_get_concepts_db_correct_number(hints_fake):
    concepts = hints_fake.get_concepts(1)
    assert 1 == concepts._number


# Test get_hint_list method

level_custom = data.get_sub_data_object("levels", "custom")
settings = objects_fake_global.create_object(GameSettings, "settings", ObjectManagerFake, numbers, level_custom)
settings.set_game_settings("2", "5")

def test_get_hint_list_db_more_than_two_hints(hints_fake):
    hints_fake._settings._level_obj = level_custom
    hints_fake.get_hint_list()
    assert len(hints_fake._hint_pool) > 2

def test_get_hint_list_db_two_multiple_hints(hints_fake):
    hints_fake._settings._level_obj = level_custom
    hints_fake.get_hint_list()
    multiple_hints = [hint for hint in hints_fake._hint_pool if "multiple" in hint]
    assert 2 == len(multiple_hints)

def test_get_hint_list_db_relevant_hints_matches_hint_pool(hints_fake):
    hints_fake._settings._level_obj = level_custom
    hints_fake.get_hint_list()
    assert hints_fake._relevant_hints == hints_fake._hint_pool


