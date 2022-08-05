"""
The hints.py module is part of the concepts package.  It consists of abstract classes that serve as
components of the concrete concept classes used for hint generation and guess evaluation.  None of the
classes in this module are meant to be instantiated directly.

Classes:
    Hint
    MainHint
    HintAddOn
    FactorHint
    DigitHint
    HintGenerator
    Evaluator
"""


from abc import ABC, abstractmethod
import re



class Hint:
    """
    The Hint class is the base class for all hints.  It defines the text at the beginning of every hint.  Its
    subclasses add more detail to the hints.
    """
    
    _hint_template = "Nice try!  Hint: "
    
    @classmethod
    def get_hint_template(cls):
        return Hint._hint_template



class MainHint(ABC, Hint):
    """
    The MainHint class is an abstract base class that also inherits from Hint.  It is for the main hint for a
    particular concept.  It is not instantiated on its own.  It is inherited by the math concepts that have a main
    hint.  It has an abstract method for generating the main hints for a math concept, deferring implementation to
    the concept classes.
    """
    
    @abstractmethod
    def _generate_main_hints(self):
        pass



class HintAddOn(ABC, Hint):
    """
    The HintAddOn class is an abstract base class that also inherits from Hint.  It is for additional hints besides
    the main hint.  It has an abstract method for indicating whether the condition for a particular concept has been
    met, deferring implementation to the concept classes.
    """
    
    def _get_count_satisfying_condition(self, num_list):
        """This method uses the satisfies condition method to get a count of them from a list."""
        
        condition_satisfiers = [num for num in num_list if self._satisfies_condition(num)]
        return len(condition_satisfiers)
    
    @abstractmethod
    def _satisfies_condition(self):
        pass



class FactorHint(HintAddOn):
    """
    The FactorHint class inherits from HintAddOn.  It is for hints related to the factors of a number.
    """
    
    _factor_hint = Hint.get_hint_template() + "It has {} factor(s)."
    
    def _generate_factor_hints(self):
        pass
    
    def _get_factor_hint(self):
        return FactorHint._factor_hint



class DigitHint(HintAddOn):
    """
    The DigitHint class inherits from HintAddOn.  It is for hints related to the digits of a number.
    """
    
    _digit_hints = {
        "digits_none": "None of its digits are ",
        "digits_one": "1 of its digits is a ",
        "digits_some": "{} of its digits are ",
        "digits_all": "All of its digits are "
    }
    
    def _generate_digit_hints(self):
        pass
    
    def _get_count_based_hint(self, digit_count, match_count):
        """This method looks up hints based on the number of digits that meet a certain criteria."""
        
        if match_count < 0 or type(match_count) != int:
            return
        
        if match_count == 0:
            keyword = "digits_none"
        elif match_count == 1:
            keyword = "digits_one"
        elif match_count == digit_count:
            keyword = "digits_all"
        elif match_count < digit_count:
            keyword = "digits_some"
        else:
            return
        
        hint = Hint.get_hint_template() + DigitHint._digit_hints[keyword]
        if "{}" in hint:
            hint = hint.format(match_count)
        
        if "1" in hint:
            hint = hint + "{}."
        else:
            hint = hint + "{}s."
        
        return hint



class HintGenerator(ABC):
    """
    The HintGenerator class is an interface that defines an abstract method for generating hints, as well as one that
    defines the condition in which the hints for a particular math concept should be included in an aggregate hint list.
    """
    
    @abstractmethod
    def generate_hints(self):
        pass
    
    @abstractmethod
    def include_concept(self):
        pass



class Evaluator(ABC):
    """
    The Evaluator class is an interface that defines an abstract method for evaluating whether a guess matches a hint,
    based on the specific math concept that generated the hint.
    """
    
    @abstractmethod
    def evaluate_guess(self):
        pass
    
    def _get_number_count(self, hint, number=None):
        if number:
            number_count = str(number)
        elif self._pattern_match("None", hint):
            number_count = "none"
        else:
            number_count = "all"
        
        return number_count
    
    def _get_guess_digit_count(self, digit_count, number):
        if digit_count == 0:
            guess_digit_count = "none"
        elif digit_count == number:
            guess_digit_count = "all"
        else:
            guess_digit_count = str(digit_count)
        
        return guess_digit_count
    
    def _extract_number_from_hint(self, hint):
        number = self._pattern_match(r"\d+", hint, value=True)
        number = int(number) if number else None
        return number
    
    @staticmethod
    def _pattern_match(pattern, string, value=False):
        """This static method searches a string for a pattern and returns a boolean indicating whether 
        it was found.  If value is True, it returns the pattern match."""
        
        match = re.search(re.compile(pattern), string)
        if value:
            try:
                result = match.group(0)
                return result
            except AttributeError:
                return
        else:
            if match:
                return True
            return False
