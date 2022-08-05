import pytest
from main.tests.tests_setup import objects_fake_global_dict, page_manager_fake
from main.resources.infrastructure.text_displayers import *
from main.tests.test_data import error_stub, game_outcome_stub



### KivyVariableManager Tests

@pytest.fixture
def variable_manager_fake():
    return KivyVariableManager(page_manager_fake)

kivy_variables = [("low_range", "Welcome Page", "low"),
                  ("high_range", "Welcome Page", "high"),
                  ("range_error_msg", "Welcome Page", "range error"),
                  ("guess_prompt_text", "Game Page", "guess prompt"),
                  ("status_text", "Game Page", "status"),
                  ("guess", "Game Page", "guess"),
                  ("hint_text", "Game Page", "hint"),
                  ("feedback_text", "Farewell Page", "feedback"),
                  ("last_msg", "Farewell Page", "last message")
                  ]

kivy_var_names = [var[0] for var in kivy_variables]
variable_pages = [(var[0], var[1]) for var in kivy_variables]
variable_values = [(var[0], var[2]) for var in kivy_variables]


# Test _get_kivy_variable method
@pytest.mark.parametrize("variable_name", kivy_var_names)
def test_get_kivy_variable(variable_manager_fake, variable_name):
    variable = variable_manager_fake._get_kivy_variable(variable_name)
    assert variable_name == variable.name

def test_get_kivy_variable_no_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake._get_kivy_variable()

def test_get_kivy_variable_too_many_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake._get_kivy_variable("guess", "extra")


# Test get_page method
@pytest.mark.parametrize("variable_name, page", variable_pages)
def test_get_page(variable_manager_fake, variable_name, page):
    assert page == variable_manager_fake.get_page(variable_name)

def test_get_page_not_found(variable_manager_fake):
    assert "Variable not found" == variable_manager_fake.get_page("empty")

def test_get_page_no_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.get_page()

def test_get_page_too_many_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.get_page("guess", "extra")


# Test display_variable_text method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_display_variable_text(variable_manager_fake, variable_name, text):
    variable_manager_fake.display_variable_text(variable_name, text)
    variable = variable_manager_fake._get_kivy_variable(variable_name)
    assert text == variable.text

def test_display_variable_text_no_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.display_variable_text()

def test_display_variable_text_too_many_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.display_variable_text("guess", "text", "extra")


# Test get_variable_text method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_get_variable_text(variable_manager_fake, variable_name, text):
    variable_manager_fake.display_variable_text(variable_name, f"test text: {text}")
    assigned_text = variable_manager_fake.get_variable_text(variable_name)
    assert assigned_text == f"test text: {text}"

def test_get_variable_text_no_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.get_variable_text()

def test_get_variable_text_too_many_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.get_variable_text("guess", "extra")


# Test clear_variable_text method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_clear_variable_text(variable_manager_fake, variable_name, text):
    variable_manager_fake.display_variable_text(variable_name, text)
    variable_manager_fake.clear_variable_text(variable_name)
    variable = variable_manager_fake._get_kivy_variable(variable_name)
    assert "" == variable.text

def test_clear_variable_text_no_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.clear_variable_text()

def test_clear_variable_text_too_many_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.clear_variable_text("guess", "extra")


# Test clear_all_variables method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_clear_all_variables(variable_manager_fake, variable_name, text):
    variable_manager_fake.display_variable_text(variable_name, text)
    variable_manager_fake.clear_all_variables()
    variable = variable_manager_fake._get_kivy_variable(variable_name)
    assert "" == variable.text

def test_clear_all_variables_too_many_arguments_raises_error(variable_manager_fake):
    with pytest.raises(TypeError):
        variable_manager_fake.clear_all_variables("extra")



### TextDisplayer Tests

@pytest.fixture
def text_displayer_fake(variable_manager_fake):
    return TextDisplayer(variable_manager_fake, objects_fake_global_dict["easy"])


# Test get_displayer_type method
def test_get_displayer_type(text_displayer_fake):
    text_displayer_fake._displayer_type = "test displayer type"
    assert "test displayer type" == text_displayer_fake.get_displayer_type()

def test_get_displayer_type_too_many_arguments_raises_error(text_displayer_fake):
    with pytest.raises(TypeError):
        text_displayer_fake.get_displayer_type("extra")



### MainTextDisplayer Tests

@pytest.fixture
def text_display_manager_fake():
    return TextDisplayManager(objects_fake_global_dict["easy"], page_manager_fake)

@pytest.fixture
def main_text_displayer_fake(text_display_manager_fake):
    return text_display_manager_fake._main_text_displayer


# Test _get_message method
def test_get_message_main_status(main_text_displayer_fake):
    assert "Guess a number between -1 and 1." == main_text_displayer_fake._get_message("guess_prompt", -1, 1)

def test_get_message_main_error(main_text_displayer_fake):
    assert "Please enter an integer." == main_text_displayer_fake._get_message("guess_entry_non_integer")

def test_get_message_main_hint(main_text_displayer_fake):
    assert "It is a 5-digit number." == main_text_displayer_fake._get_message("digit_length", 5)

def test_get_message_main_feedback(main_text_displayer_fake):
    assert "Remember:\nnew line" == main_text_displayer_fake._get_message("improvement_description", "new line")

def test_get_message_main_no_arguments_raises_error(main_text_displayer_fake):
    with pytest.raises(TypeError):
        main_text_displayer_fake._get_message()


# Test display_text method
def test_display_text_main_status(main_text_displayer_fake):
    main_text_displayer_fake.display_text("guess_prompt_text", "guess_prompt", -1, 1)
    assert "Guess a number between -1 and 1." == main_text_displayer_fake._variables.get_variable_text("guess_prompt_text")

def test_display_text_main_error(main_text_displayer_fake):
    main_text_displayer_fake.display_text("hint_text", "guess_entry_non_integer")
    assert "Please enter an integer." == main_text_displayer_fake._variables.get_variable_text("hint_text")

def test_display_text_main_hint(main_text_displayer_fake):
    main_text_displayer_fake.display_text("hint_text", "digit_length", 5)
    assert "It is a 5-digit number." == main_text_displayer_fake._variables.get_variable_text("hint_text")

def test_display_text_main_feedback(main_text_displayer_fake):
    main_text_displayer_fake.display_text("feedback_text", "improvement_description", "new line")
    assert "Remember:\nnew line" == main_text_displayer_fake._variables.get_variable_text("feedback_text")

def test_display_text_main_no_arguments_raises_error(main_text_displayer_fake):
    with pytest.raises(TypeError):
        main_text_displayer_fake.display_text()



### DataTextDisplayer Tests

@pytest.fixture
def data_text_displayer_fake(text_display_manager_fake):
    return text_display_manager_fake._data_text_displayer


# Test _get_message method
def test_get_message_data_error(data_text_displayer_fake, error_stub):
    assert "test error message" == data_text_displayer_fake._get_message(error_stub)

def test_get_message_data_game_outcome(data_text_displayer_fake, game_outcome_stub):
    assert "test outcome message" == data_text_displayer_fake._get_message(game_outcome_stub)

def test_get_message_data_no_arguments_raises_error(data_text_displayer_fake):
    with pytest.raises(TypeError):
        data_text_displayer_fake._get_message()

def test_get_message_data_too_many_arguments_raises_error(data_text_displayer_fake, error_stub):
    with pytest.raises(TypeError):
        data_text_displayer_fake._get_message(error_stub, "extra")


# Test display_text method
def test_display_text_data_error(data_text_displayer_fake, error_stub):
    data_text_displayer_fake.display_text("hint_text", error_stub)
    assert "test error message" == data_text_displayer_fake._variables.get_variable_text("hint_text")

def test_display_text_data_game_outcome(data_text_displayer_fake, game_outcome_stub):
    data_text_displayer_fake.display_text("last_msg", game_outcome_stub)
    assert "test outcome message" == data_text_displayer_fake._variables.get_variable_text("last_msg")

def test_display_text_data_no_arguments_raises_error(data_text_displayer_fake):
    with pytest.raises(TypeError):
        data_text_displayer_fake.display_text()

def test_display_text_data_too_many_arguments_raises_error(data_text_displayer_fake, error_stub):
    with pytest.raises(TypeError):
        data_text_displayer_fake.display_text("hint_text", error_stub, "extra")



### DynamicTextDisplayer Tests

@pytest.fixture
def dynamic_text_displayer_fake(text_display_manager_fake):
    return text_display_manager_fake._dynamic_text_displayer


# Test _get_message method
def test_get_message_dynamic(dynamic_text_displayer_fake):
    assert "test dynamic message" == dynamic_text_displayer_fake._get_message("test dynamic message")

def test_get_message_dynamic_no_arguments_raises_error(dynamic_text_displayer_fake):
    with pytest.raises(TypeError):
        dynamic_text_displayer_fake._get_message()

def test_get_message_dynamic_too_many_arguments_raises_error(dynamic_text_displayer_fake):
    with pytest.raises(TypeError):
        dynamic_text_displayer_fake._get_message("test dynamic message", "extra")


# Test display_text method
def test_display_text_dynamic(dynamic_text_displayer_fake):
    dynamic_text_displayer_fake.display_text("hint_text", "test dynamic message")
    assert "test dynamic message" == dynamic_text_displayer_fake._variables.get_variable_text("hint_text")

def test_display_text_dynamic_no_arguments_raises_error(dynamic_text_displayer_fake):
    with pytest.raises(TypeError):
        dynamic_text_displayer_fake.display_text()

def test_display_text_dynamic_too_many_arguments_raises_error(dynamic_text_displayer_fake):
    with pytest.raises(TypeError):
        dynamic_text_displayer_fake.display_text("hint_text", "test dynamic message", "extra")



### TextDisplayManager Tests


# Test display_text method
def test_display_text_manager_text(text_display_manager_fake):
    text_display_manager_fake.display_text("text", "guess_prompt_text", "guess_prompt", -1, 1)
    assert "Guess a number between -1 and 1." == text_display_manager_fake._variables.get_variable_text("guess_prompt_text")

def test_display_text_manager_data(text_display_manager_fake, game_outcome_stub):
    text_display_manager_fake.display_text("data", "last_msg", game_outcome_stub)
    assert "test outcome message" == text_display_manager_fake._variables.get_variable_text("last_msg")

def test_display_text_manager_dynamic(text_display_manager_fake):
    text_display_manager_fake.display_text("dynamic", "hint_text", "test dynamic message")
    assert "test dynamic message" == text_display_manager_fake._variables.get_variable_text("hint_text")

def test_display_text_manager_no_arguments_raises_error(text_display_manager_fake):
    with pytest.raises(TypeError):
        text_display_manager_fake.display_text()


# Test get_text method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_get_text(text_display_manager_fake, variable_name, text):
    text_display_manager_fake._variables.display_variable_text(variable_name, f"test text: {text}")
    assigned_text = text_display_manager_fake.get_text(variable_name)
    assert assigned_text == f"test text: {text}"

def test_get_text_no_arguments_raises_error(text_display_manager_fake):
    with pytest.raises(TypeError):
        text_display_manager_fake.get_text()

def test_get_text_too_many_arguments_raises_error(text_display_manager_fake):
    with pytest.raises(TypeError):
        text_display_manager_fake.get_text("guess", "extra")


# Test clear_text method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_clear_text(text_display_manager_fake, variable_name, text):
    text_display_manager_fake._variables.display_variable_text(variable_name, text)
    text_display_manager_fake.clear_text(variable_name)
    variable = text_display_manager_fake._variables._get_kivy_variable(variable_name)
    assert "" == variable.text

def test_clear_text_no_arguments_raises_error(text_display_manager_fake):
    with pytest.raises(TypeError):
        text_display_manager_fake.clear_text()

def test_clear_text_too_many_arguments_raises_error(text_display_manager_fake):
    with pytest.raises(TypeError):
        text_display_manager_fake.clear_text("guess", "extra")


# Test clear_all_variables method
@pytest.mark.parametrize("variable_name, text", variable_values)
def test_clear_all_variables_display_manager(text_display_manager_fake, variable_name, text):
    text_display_manager_fake._variables.display_variable_text(variable_name, text)
    text_display_manager_fake.clear_all_variables()
    variable = text_display_manager_fake._variables._get_kivy_variable(variable_name)
    assert "" == variable.text

def test_clear_all_variables_display_manager_too_many_arguments_raises_error(text_display_manager_fake):
    with pytest.raises(TypeError):
        text_display_manager_fake.clear_all_variables("extra")


