"""
The factor.py module is part of the concepts package.  It represents the math concept of factors.
Hints related to factors include main hints, factor hints, and digit hints.

Classes:
    Factor
"""


from concepts.math_concept import MathConcept
from concepts.hints import MainHint, FactorHint, DigitHint



class Factor(MathConcept, MainHint, FactorHint, DigitHint):
    """
    The Factor class is for the math concept of factors.  It inherits from MathConcept, MainHint, FactorHint, and
    DigitHint.  It inherits directly from MathConcept because it follows different logic from the StandardConcept
    class.
    """
    
    _name = "factor"
    
    def __init__(self, number, numbers_obj, factor_data_obj):
        super().__init__(number, numbers_obj, factor_data_obj)
    
    def generate_hints(self):
        """This method checks what factors the winning number has and adds a separate hint for each factor, along with one
        for the number of factors.  It also adds a hint for the number of its digits that are factors."""
        
        hints = []
        factors = self._numbers_obj.get_number_info("factors", self._number)
        digits = self._numbers_obj.get_number_info("digits", self._number)
        
        if len(factors) > 2 or self._number == 1:
            main_hints = self._generate_main_hints(factors)
            hints = hints + main_hints
            
            factor_hints = self._generate_factor_hints(factors)
            hints = hints + factor_hints
            
            if len(digits) > 1:
                digit_hints = self._generate_digit_hints(factors, digits)
                hints = hints + digit_hints
        
        return hints
    
    def _generate_main_hints(self, factors):
        hints = []
        
        # Add hints for specific factors, not including the number itself or 1.
        for factor in factors[1:-1]:
            ind_factor_hint = self._get_main_hint()
            ind_factor_hint = ind_factor_hint.format(factor)
            hints.append(ind_factor_hint)
        
        return hints
    
    def _generate_factor_hints(self, factors):
        hints = []
        
        factors_hint = self._get_factor_hint()
        factors_hint = factors_hint.format(len(factors))
        hints.append(factors_hint)
        
        return hints
    
    def _generate_digit_hints(self, factors, digits):
        hints = []
        
        # If the number has at least 2 digits and is not prime, add a hint for number of digits that are also factors.
        digit_factors = self._get_count_satisfying_condition(digits)
        
        digits_hint = self._get_count_based_hint(len(digits), digit_factors)
        digits_hint = digits_hint.format(Factor._name)
        hints.append(digits_hint)
        
        return hints
    
    def include_concept(self):
        return self._number != 0
    
    def evaluate_guess(self, guess, hint):
        number = self._extract_number_from_hint(hint)
        
        digit_hint = self._pattern_match("digits", hint)
        if not digit_hint:
            individual_factor_hint = self._pattern_match("divisible", hint)
            if individual_factor_hint:
                feedback = "good" if self._numbers_obj.get_number_info("is factor", guess, number) else "bad"
            else:
                factors = self._numbers_obj.get_number_info("factors", guess)
                feedback = "good" if len(factors) == number else "bad"
        
        else:
            number_count = self._get_number_count(hint, number)
            digits = self._numbers_obj.get_number_info("digits", guess)
            digit_count = self._numbers_obj.get_number_info("digit factors", guess)
            guess_digit_count = self._get_guess_digit_count(digit_count, len(digits))
            
            feedback = "good" if number_count == guess_digit_count else "bad"
        
        return feedback
    
    def _satisfies_condition(self, x):
        return self._numbers_obj.get_number_info("is factor", self._number, x)