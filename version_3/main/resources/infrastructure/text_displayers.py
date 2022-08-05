"""
The text_displayers.py module is part of the infrastructure package.  It contains a set of a classes
for accessing text from different sources and using Kivy variables to display it on the app.

Classes:
    KivyVariableManager
    TextDisplayer
    MainTextDisplayer
    DataTextDisplayer
    DynamicTextDisplayer
    TextDisplayManager
"""


from resources.infrastructure.subsystem import BaseClass, Manager
from resources.infrastructure.log_entries import TextLogEntry
from resources.infrastructure.application_text import TextContainer



class KivyVariableManager:
    """
    The KivyVariableManager class stores all of the Kivy variables for different widgets on the app
    and controls the text that is assigned to those variables at a given point in time.
    """
    
    def __init__(self, pages):
        self._pages = pages
        self._kivy_variables = {
            "low_range": self._pages.welcome_page.ids.low_range,
            "high_range": self._pages.welcome_page.ids.high_range,
            "range_error_msg": self._pages.welcome_page.ids.range_error_msg,
            "guess_prompt_text": self._pages.game_page.ids.guess_prompt_text,
            "status_text": self._pages.game_page.ids.status_text,
            "guess": self._pages.game_page.ids.guess,
            "hint_text": self._pages.game_page.ids.hint_text,
            "last_msg": self._pages.farewell_page.ids.last_msg,
            "feedback_text": self._pages.farewell_page.ids.feedback_text
            }
    
    def display_variable_text(self, var_name, content):
        variable = self._get_kivy_variable(var_name)
        variable.text = content
    
    def get_variable_text(self, var_name):
        variable = self._get_kivy_variable(var_name)
        return variable.text
    
    def clear_variable_text(self, var_name):
        variable = self._get_kivy_variable(var_name)
        variable.text = ""
    
    def clear_all_variables(self):
        for var_name in self._kivy_variables:
            self.clear_variable_text(var_name)
    
    def get_page(self, var_name):
        if var_name in list(self._pages.welcome_page.ids):
            return "Welcome Page"
        elif var_name in list(self._pages.game_page.ids):
            return "Game Page"
        elif var_name in list(self._pages.farewell_page.ids):
            return "Farewell Page"
        else:
            return "Variable not found"
    
    def _get_kivy_variable(self, var_name):
        return self._kivy_variables[var_name]



class TextDisplayer(BaseClass):
    """
    The TextDisplayer class is the base class for changing the text displayed on the app via Kivy
    variables.
    """
    
    def __init__(self, variables, objects):
        super().__init__()
        
        self._displayer_type = ""
        
        self._variables = variables
        self._objects = objects
        self._logs = self._objects.get_object("logs")
        
        self._obj_id_method = self.get_displayer_type
        self._standardized_method = self.display_text
    
    def display_text(self, var_name, *args):
        content = self._get_message(*args)
        self._variables.display_variable_text(var_name, content)
        
        if self._logs:
            page = self._variables.get_page(var_name)
            text_log_entry = TextLogEntry(self._logs, page, var_name, content)
            text_log_entry.add_log_entry("text")
    
    def get_displayer_type(self):
        return self._displayer_type
    
    def _get_message(self):
        pass



class MainTextDisplayer(TextDisplayer):
    """
    The MainTextDisplayer class is for changing text that is obtained via the TextManager class.  It inherits
    from TextDisplayer.
    """
    
    def __init__(self, variables, objects):
        super().__init__(variables, objects)
        self._displayer_type = "text"
        self._text = self._objects.get_object("text")
    
    def _get_message(self, keyword, *args):
        message = self._text.get_text(keyword, *args)
        return message



class DataTextDisplayer(TextDisplayer):
    """
    The DataTextDisplayer class is for changing text that is obtained via the DataManager class, or objects
    from the data.py module.  It inherits from TextDisplayer.
    """
    
    def __init__(self, variables, objects):
        super().__init__(variables, objects)
        self._displayer_type = "data"
    
    def _get_message(self, data_obj):
        return data_obj.get_message()



class DynamicTextDisplayer(TextDisplayer):
    """
    The DynamicTextDisplayer class is for changing text that is passed in directly.  It inherits from
    TextDisplayer.
    """
    
    def __init__(self, variables, objects):
        super().__init__(variables, objects)
        self._displayer_type = "dynamic"
    
    def _get_message(self, message):
        return message



class TextDisplayManager(Manager):
    """
    The TextDisplayManager class is composed of subclasses of TextDisplayer, as well as KivyVariableManager.
    It is the centralized location for changing text on the app.  It defers implementation for changing
    text to the appropriate TextDisplayer subclass to obtain text, and then uses the KivyVariableManager
    object to display that new text on the app.
    """
    
    def __init__(self, objects, page_manager):
        self._objects = objects
        self._variables = objects.create_object(KivyVariableManager, "variables", TextDisplayManager, page_manager)
        self._main_text_displayer = MainTextDisplayer(self._variables, self._objects)
        self._data_text_displayer = DataTextDisplayer(self._variables, self._objects)
        self._dynamic_text_displayer = DynamicTextDisplayer(self._variables, self._objects)
        super().__init__(TextDisplayer)
    
    def display_text(self, displayer_type, var_name, *args):
        self.run_subclass_method(displayer_type, var_name, *args)
    
    def get_text(self, var_name):
        text = self._variables.get_variable_text(var_name)
        return text
    
    def clear_text(self, var_name):
        self._variables.clear_variable_text(var_name)
    
    def clear_all_variables(self):
        self._variables.clear_all_variables()