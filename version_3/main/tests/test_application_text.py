import pytest
from main.resources.infrastructure.application_text import *



### TextGenerator Tests

@pytest.fixture
def text_generator_stub():
    text = TextGenerator()
    text._application_text = {
        "regular": "Test text.",
        "format": "Test text {}."
        }
    text._text_type = "test"
    return text


# Test _lookup_text method
def test_lookup_text_regular(text_generator_stub):
    assert "Test text." == text_generator_stub._lookup_text("regular")

def test_lookup_text_format(text_generator_stub):
    assert "Test text {}." == text_generator_stub._lookup_text("format")

def test_lookup_text_not_found(text_generator_stub):
    assert "Keyword not found." == text_generator_stub._lookup_text("not_found")

def test_lookup_text_no_arguments_raises_error(text_generator_stub):
    with pytest.raises(TypeError):
        text_generator_stub._lookup_text()

def test_lookup_text_too_many_arguments_raises_error(text_generator_stub):
    with pytest.raises(TypeError):
        text_generator_stub._lookup_text("regular", "extra")


# Test _format_text method
def test_format_text_number(text_generator_stub):
    assert "Test text 3." == text_generator_stub._format_text("Test text {}.", 3)

def test_format_text_string(text_generator_stub):
    assert "Test text three." == text_generator_stub._format_text("Test text {}.", "three")

def test_format_text_extra_arg(text_generator_stub):
    assert "Test text three." == text_generator_stub._format_text("Test text {}.", "three", "four")

def test_format_text_no_arguments_raises_error(text_generator_stub):
    with pytest.raises(TypeError):
        text_generator_stub._format_text()


# Test get_text method
def test_get_text_regular(text_generator_stub):
    assert "Test text." == text_generator_stub.get_text("regular")

def test_get_text_format(text_generator_stub):
    assert "Test text 0." == text_generator_stub.get_text("format", 0)

def test_get_text_not_found(text_generator_stub):
    assert "Keyword not found." == text_generator_stub.get_text("not_found", 0)

def test_get_text_no_arguments_raises_error(text_generator_stub):
    with pytest.raises(TypeError):
        text_generator_stub.get_text()



### TextManager Tests

@pytest.fixture
def text_copy():
    return TextManager()


# Test _get_text_type_from_keyword method
def test_get_text_type_from_keyword_status(text_copy):
    assert "status" == text_copy._get_text_type_from_keyword("guess_prompt")

def test_get_text_type_from_keyword_error(text_copy):
    assert "error" == text_copy._get_text_type_from_keyword("guess_entry_non_integer")

def test_get_text_type_from_keyword_hint(text_copy):
    assert "hint" == text_copy._get_text_type_from_keyword("factor")

def test_get_text_type_from_keyword_feedback(text_copy):
    assert "feedback" == text_copy._get_text_type_from_keyword("recommendation")

def test_get_text_type_from_keyword_not_found(text_copy):
    assert None == text_copy._get_text_type_from_keyword("not_found")

def test_get_text_type_from_keyword_no_arguments_raises_error(text_copy):
    with pytest.raises(TypeError):
        text_copy._get_text_type_from_keyword()

def test_get_text_type_from_keyword_too_many_arguments_raises_error(text_copy):
    with pytest.raises(TypeError):
        text_copy._get_text_type_from_keyword("factor", "extra")


# Test get_text method
def test_get_text_manager_level_status(text_copy):
    assert "Guess a number between -1 and 1." == text_copy.get_text("guess_prompt", -1, 1)

def test_get_text_manager_level_error(text_copy):
    assert "Please enter an integer." == text_copy.get_text("guess_entry_non_integer")

def test_get_text_manager_level_hint(text_copy):
    assert "It is a 5-digit number." == text_copy.get_text("digit_length", 5)

def test_get_text_manager_level_feedback(text_copy):
    assert "Remember:\nnew line" == text_copy.get_text("improvement_description", "new line")

def test_get_text_manager_level_not_found_raises_error(text_copy):
    with pytest.raises(AttributeError):
        text_copy.get_text("not_found")

def test_get_text_manager_level_no_arguments_raises_error(text_copy):
    with pytest.raises(TypeError):
        text_copy.get_text()


# Test get_hint_description method
def test_get_hint_description_found(text_copy):
    multiple_description = "Multiple: The result of multiplying a number by an integer (not by a fraction)."
    assert multiple_description == text_copy.get_hint_description("multiple")

def test_get_hint_description_not_found(text_copy):
    assert "perfect_cube" == text_copy.get_hint_description("perfect_cube")

def test_get_hint_description_no_arguments_raises_error(text_copy):
    with pytest.raises(TypeError):
        text_copy.get_hint_description()

def test_get_hint_description_too_many_arguments_raises_error(text_copy):
    with pytest.raises(TypeError):
        text_copy.get_hint_description("factor", "extra")


