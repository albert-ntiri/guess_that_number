"""
The application_text.py module is part of the infrastructure package.  It contains a set of a classes
that define the wording that appears in different places in the app, based on the context.

Classes:
    TextContainer
    TextGenerator
    StatusTextGenerator
    ErrorTextGenerator
    HintTextGenerator
    FeedbackTextGenerator
    TextManager
"""


from abc import ABC, abstractmethod
from resources.infrastructure.subsystem import BaseClass, Manager
import pandas as pd



class TextContainer(ABC):
    """
    The TextContainer class is an interface for objects that contain some type of text.  It has one
    abstract method for retrieving its text, which it defers to that classes that use it.
    """
    
    @abstractmethod
    def get_text(self):
        pass



class TextGenerator(TextContainer, BaseClass):
    """
    The TextGenerator class is the base class for text on the app that varies based on the context.
    Static text is defined in the kv file.  Each subclass has 2 class attributes, which it will implement
    specific to its area: _text_type and _application_text.  It defines a way to lookup the appropriate
    text and format it with any values, as appropriate.  It inherits from TextContainer
    """
    
    _text_type = ""
    
    def __init__(self):
        super().__init__()
        
        self._application_text = {}
        
        self._obj_id_method = self.get_text_type
        self._standardized_method = self.get_text
    
    def get_text(self, keyword, *args):
        text = self._lookup_text(keyword)
        if args:
            text = self._format_text(text, *args)
        
        return text
    
    def get_text_type_from_keyword(self, keyword):
        if self._lookup_text(keyword) != "Keyword not found.":
            return self.get_text_type()
    
    def _lookup_text(self, keyword):
        if keyword in self._application_text:
            return self._application_text[keyword]
        else:
            return "Keyword not found."
    
    def _format_text(self, text, *args):
        text = text.format(*args)
        return text
    
    @classmethod
    def get_text_type(cls):
        pass



class StatusTextGenerator(TextGenerator):
    """
    The StatusTextGenerator class covers the text providing the user with the guess range, showing the
    number of guesses remaining, and the final message showing the outcome of the game.  It inherits
    from TextGenerator.
    """
    
    _text_type = "status"
    
    def __init__(self):
        super().__init__()
        
        self._application_text = {
                "guess_prompt": "Guess a number between {} and {}.",
                "status": "Guesses Remaining: {}",
                "outcome_win": "That's correct! Congratulations! You are a winner!!!\n\nYour Score: {}\n\n\nThanks for playing! Please come back soon.",
                "outcome_lose": "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon.",
                "outcome_quit": "Thanks for playing! Please come back soon."
            }
    
    @classmethod
    def get_text_type(cls):
        return StatusTextGenerator._text_type



class ErrorTextGenerator(TextGenerator):
    """
    The ErrorTextGenerator class covers the different error messages shown to the user when inputing an
    invalid range or guess.  It inherits from TextGenerator.
    """
    
    _text_type = "error"
    
    def __init__(self):
        super().__init__()
        
        self._application_text = {
                "range_entry_comparison": "High value must be greater than low value.",
                "range_entry_missing": "No numbers were returned.",
                "range_entry_invalid": "Both values must be integers.",
                "guess_entry_non_integer": "Please enter an integer.",
                "guess_entry_out_of_range": "Your guess is out of range. Please try again."
            }
    
    @classmethod
    def get_text_type(cls):
        return ErrorTextGenerator._text_type



class HintTextGenerator(TextGenerator):
    """
    The HintTextGenerator class covers the different hints shown to the user during the course of the
    game.  It inherits from TextGenerator.
    """
    
    _text_type = "hint"
    
    def __init__(self):
        super().__init__()
        
        self._application_text = {
            "factor": "It is divisible by {}.",
            "multiple": "{} is a multiple.",
            "prime": "It is a prime number.",
            "even_odd": "It is an {} number.",
            "perfect_square": "It is a perfect square.",
            "perfect_cube": "It is a perfect cube.",
            "digit_sum": "The sum of its digits is {}.",
            "digit_length": "It is a {}-digit number.",
            "greater_less": "{}."
        }
        hint_descriptions_df = pd.read_csv("resources/hint_descriptions.csv", index_col="hint_type")
        self._hint_descriptions = hint_descriptions_df.hint_description.to_dict()
    
    def get_description(self, hint_type):
        try:
            hint_description = self._hint_descriptions[hint_type]
            return hint_description
        except KeyError:
            return hint_type
    
    @classmethod
    def get_text_type(cls):
        return HintTextGenerator._text_type



class FeedbackTextGenerator(TextGenerator):
    """
    The FeedbackTextGenerator class covers the text informing the user about a concept they misapplied or
    offering a recommendation for a target score or level of difficulty for their next game.  It inherits
    from TextGenerator.
    """
    
    _text_type = "feedback"
    
    def __init__(self):
        super().__init__()
        
        self._application_text = {
                "improvement_general": "Feedback:\nSome of your guesses did not match the hints.  For example: {}.",
                "improvement_example": 'Your guess, {}, did not match the hint: "{}"',
                "improvement_description": "Remember:\n{}",
                "recommendation": "Recommended {} for your next game: {}."
            }
    
    @classmethod
    def get_text_type(cls):
        return FeedbackTextGenerator._text_type



class TextManager(TextContainer, Manager):
    """
    The TextManager class serves as a centralized location for storing all of the variable text displayed
    on the app.  It is composed of objects of each of the subclasses of TextGenerator.  It inherits from
    TextContainer.
    """
    
    def __init__(self):
        self._status_text = StatusTextGenerator()
        self._error_text = ErrorTextGenerator()
        self._hint_text = HintTextGenerator()
        self._feedback_text = FeedbackTextGenerator()
        super().__init__(TextGenerator)
    
    def get_text(self, keyword, *args):
        text_type = self._get_text_type_from_keyword(keyword)
        text = self.run_subclass_method(text_type, keyword, *args)
        return text
    
    def _get_text_type_from_keyword(self, keyword):
        for instance in self._subclass_list:
            text_type = instance.get_text_type_from_keyword(keyword)
            if text_type:
                return text_type
    
    def get_hint_description(self, hint_type):
        return self._hint_text.get_description(hint_type)