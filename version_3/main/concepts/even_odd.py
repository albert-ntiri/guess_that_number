"""
The even_odd.py module is part of the concepts package.  It represents the math concept of even and odd numbers.
Hints related to even and odd numbers include main hints and digit hints.

Classes:
    EvenOdd
"""


from concepts.math_concept import StandardConcept



class EvenOdd(StandardConcept):
    """
    The EvenOdd class is for the math concept of even and odd numbers.  It inherits from StandardConcept.
    """
    
    _name = "even/odd"
    
    def __init__(self, number, numbers_obj, even_odd_data_obj):
        super().__init__(number, numbers_obj, even_odd_data_obj)
        self._digit_hint_display_name = "even number"
    
    def _generate_main_hints(self):
        hints = []
        
        tag = "even" if self._satisfies_condition() else "odd"
        main_hint = self._get_main_hint()
        main_hint = main_hint.format(tag)
        hints.append(main_hint)
        
        return hints
    
    def _generate_digit_hints(self, digits):
        digit_hints = super()._generate_digit_hints(digits)
        for index, hint in enumerate(digit_hints):
            if hint == "Nice try!  Hint: 1 of its digits is a even number.":
                digit_hints[index] = hint.replace("a ", "an ")
        
        return digit_hints
    
    def include_concept(self):
        return abs(self._number) < 100
    
    def evaluate_guess(self, guess, hint):
        number = self._extract_number_from_hint(hint)
        
        digit_hint = self._pattern_match("digits", hint)
        if not digit_hint:
            feedback = self._get_non_digit_hint_feedback(hint, guess)
        else:
            feedback = self._get_digit_hint_feedback(hint, number, guess)
        
        return feedback
    
    def _get_non_digit_hint_feedback(self, hint, guess):
        winning_number_tag = "even" if self._pattern_match("even", hint) else "odd"
        guess_tag = "even" if self._satisfies_condition(guess) else "odd"
        feedback = "good" if winning_number_tag == guess_tag else "bad"
        
        return feedback
    
    def _satisfies_condition(self, x=None):
        if not x and x != 0:
            return self._numbers_obj.get_number_info("is factor", self._number, 2)
        else:
            return self._numbers_obj.get_number_info("is factor", x, 2)