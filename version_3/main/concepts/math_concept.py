"""
The math_concept.py module is part of the concepts package.  It represents different base classes for the
concepts included in games.  None of the classes in this module are meant to be instantiated directly.  Each
of these classes has building blocks from other classes they inherit from.  These building blocks are in the
hints.py module.

Classes:
    MathConcept
    DigitConcept
    StandardConcept
    PerfectExponentConcept
"""


from resources.infrastructure.subsystem import BaseClass
from concepts.hints import HintGenerator, Evaluator, Hint, MainHint, FactorHint, DigitHint



class MathConcept(HintGenerator, Evaluator, BaseClass):
    """
    The MathConcept class is a base class for all of the math concepts included in the game.  It inherits both
    the HintGenerator and Evaluator interfaces, deferring its abstract methods to its subclasses.  It also includes
    an object of the Number class which it uses to generate hints and evaluate guesses for each subclass's
    particular math concept.
    """
    
    _name = ""
    
    def __init__(self, number, numbers_obj, data_obj):
        super().__init__()
        
        self._number = number
        self._numbers_obj = numbers_obj
        self._data_obj = data_obj
        
        self._obj_id_method = self.get_name
        self._standardized_method = self.evaluate_guess
    
    def generate_hints(self):
        pass
    
    def include_concept(self):
        pass
    
    def evaluate_guess(self):
        pass
    
    def get_name(self):
        return self._data_obj.get_name()
    
    def _get_main_hint(self):
        return Hint.get_hint_template() + self._data_obj.get_main_hint()



class DigitConcept(MathConcept, MainHint):
    """
    The DigitConcept class is the base class for the math concepts covered in the digit_concepts.py module.
    It inherits from MathConcept and MainHint.
    """
    
    def __init__(self, number, numbers_obj, data_obj):
        super().__init__(number, numbers_obj, data_obj)
        self._formula = None
        self._min_number_to_include = 0
    
    def generate_hints(self):
        hints = self._generate_main_hints()
        return hints
    
    def _generate_main_hints(self):
        hints = []
        digits = self._numbers_obj.get_number_info("digits", self._number)
        
        hint = self._get_main_hint()
        hint = hint.format(self._formula(digits))
        hints.append(hint)
        
        return hints
    
    def include_concept(self):
        return abs(self._number) > self._min_number_to_include
    
    def evaluate_guess(self, guess, hint):
        number = self._extract_number_from_hint(hint)
        digits = self._numbers_obj.get_number_info("digits", guess)
        
        feedback = "good" if self._formula(digits) == number else "bad"
        
        return feedback



class StandardConcept(MathConcept, MainHint, DigitHint):
    """
    The StandardConcept class is the base class for most math concepts not covered in the digit_concepts.py
    module.  It defines the format that those concepts follow.  It inherits from MathConcept, MainHint, and
    DigitHint.
    """
    
    def __init__(self, number, numbers_obj, data_obj):
        super().__init__(number, numbers_obj, data_obj)
        self._digit_hint_display_name = ""
    
    def generate_hints(self):
        hints = []
        digits = self._numbers_obj.get_number_info("digits", self._number)
        
        main_hints = self._generate_main_hints()
        hints = hints + main_hints
        
        if len(digits) > 1:
            digit_hints = self._generate_digit_hints(digits)
            hints = hints + digit_hints
        
        return hints
    
    def _generate_digit_hints(self, digits):
        hints = []
        
        # If it is at least a 2-digit number, add a hint for the number of digits that are perfect squares.
        digit_count = self._get_count_satisfying_condition(digits)
        
        digits_hint = self._get_count_based_hint(len(digits), digit_count)
        digits_hint = digits_hint.format(self._digit_hint_display_name)
        hints.append(digits_hint)
        
        return hints
    
    def _get_digit_hint_feedback(self, hint, number, guess):
        number_count = self._get_number_count(hint, number)
        
        digits = self._numbers_obj.get_number_info("digits", guess)
        digit_count = self._get_count_satisfying_condition(digits)
        guess_digit_count = self._get_guess_digit_count(digit_count, len(digits))
        
        feedback = "good" if number_count == guess_digit_count else "bad"
        
        return feedback



class PerfectExponentConcept(StandardConcept):
    """
    The PerfectExponentConcept class is specific to the math concepts of perfect squares and perfect cubes.
    It inherits from StandardConcept.  Its subclasses are defined in the perfect_exponents.py module.
    """
    
    def _generate_main_hints(self):
        hints = []
        
        if self._satisfies_condition():
            main_hint = self._get_main_hint()
            hints.append(main_hint)
        
        return hints
    
    def evaluate_guess(self, guess, hint):
        number = self._extract_number_from_hint(hint)
        
        digit_hint = self._pattern_match("digits", hint)
        if not digit_hint:
            feedback = self._get_non_digit_hint_feedback(guess)
        else:
            feedback = self._get_digit_hint_feedback(hint, number, guess)
        
        return feedback
    
    def _get_non_digit_hint_feedback(self, guess):
        return "good" if self._satisfies_condition(guess) else "bad"
    
    def _satisfies_condition(self, x=None):
        if not x and x != 0:
            return self._numbers_obj.get_number_info(f"is {self._digit_hint_display_name}", self._number)
        else:
            return self._numbers_obj.get_number_info(f"is {self._digit_hint_display_name}", x)