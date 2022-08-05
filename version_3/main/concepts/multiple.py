"""
The multiple.py module is part of the concepts package.  It represents the math concept of multiples.
Hints related to multiples include main hints only.

Classes:
    Multiple
"""


from concepts.math_concept import MathConcept
from concepts.hints import MainHint



class Multiple(MathConcept, MainHint):
    """
    The Multiple class is for the math concept of multiples.  It inherits from MathConcept and MainHint.
    It inherits directly from MathConcept because it follows different logic from the StandardConcept class.
    """
    
    _name = "multiple"
    
    def __init__(self, number, numbers_obj, multiple_data_obj):
        super().__init__(number, numbers_obj, multiple_data_obj)
    
    def generate_hints(self, filter_results=True):
        """This method generates a few multiples of the winning number, picks 2 of them at random, and adds a hint for each
        of those 2.  If filter_results is False, it returns all of the hints instead of picking 2 of them."""
        
        hints = self._generate_main_hints(filter_results)
        
        return hints
    
    def _generate_main_hints(self, filter_results=True):
        hints = []
        multiples = [self._number * i for i in range(1,6)]
        
        if filter_results:
            hint_indexes = self._numbers_obj.get_random_numbers((0, len(multiples)), n=2)
            for index in hint_indexes:
                self._add_multiple_hint_to_list(hints, multiples[index])
        else:
            for multiple in multiples:
                self._add_multiple_hint_to_list(hints, multiple)
        
        return hints
    
    def _add_multiple_hint_to_list(self, hints, multiple):
        hint = self._get_main_hint()
        hint = hint.format(multiple)
        if hint not in hints:
            hints.append(hint)
    
    def include_concept(self):
        return self._number not in (0, 1)
    
    def evaluate_guess(self, guess, hint):
        number = self._extract_number_from_hint(hint)
        
        if guess != 0:
            feedback = "good" if self._numbers_obj.get_number_info("is factor", number, guess) else "bad"
        else:
            feedback = "good" if number == guess else "bad"
        
        return feedback