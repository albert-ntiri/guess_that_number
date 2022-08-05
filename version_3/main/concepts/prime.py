"""
The prime.py module is part of the concepts package.  It represents the math concept of prime numbers.
Hints related to prime numbers include main hints, factor hints, and digit hints.

Classes:
    PrimeNumber
"""


from concepts.math_concept import StandardConcept
from concepts.hints import FactorHint



class PrimeNumber(StandardConcept, FactorHint):
    """
    The PrimeNumber class is for the math concept of prime numbers.  It inherits from StandardConcept and FactorHint.
    """
    
    _name = "prime number"
    
    def __init__(self, number, numbers_obj, prime_data_obj):
        super().__init__(number, numbers_obj, prime_data_obj)
        self._digit_hint_display_name = PrimeNumber._name
    
    def generate_hints(self):
        hints = super().generate_hints()
        
        factors = self._numbers_obj.get_number_info("factors", self._number)
        if len(factors) > 2:
            factor_hints = self._generate_factor_hints(factors)
            hints = hints + factor_hints
        
        return hints
    
    def _generate_main_hints(self):
        hints = []
        
        # Add a hint if the number is prime (has exactly 2 factors).
        if self._satisfies_condition():
            main_hint = self._get_main_hint()
            hints.append(main_hint)
        
        return hints
    
    def _generate_factor_hints(self, factors):
        hints = []
        
        prime_factors_count = self._get_count_satisfying_condition(factors)
        
        prime_factors_hint = self._get_factor_hint()
        prime_factors_hint = prime_factors_hint.format(str(prime_factors_count) + " prime")
        hints.append(prime_factors_hint)
        
        return hints
    
    def include_concept(self):
        return self._number >= 0
    
    def evaluate_guess(self, guess, hint):
        number = self._extract_number_from_hint(hint)
        
        digit_hint = self._pattern_match("digits", hint)
        if not digit_hint:
            feedback = self._get_non_digit_hint_feedback(number, guess)
        else:
            feedback = self._get_digit_hint_feedback(hint, number, guess)
        
        return feedback
    
    def _get_non_digit_hint_feedback(self, number, guess):
        if not number:
            feedback = "good" if self._satisfies_condition(guess) else "bad"
        else:
            prime_factors = self._numbers_obj.get_number_info("prime factors", guess)
            feedback = "good" if len(prime_factors) == number else "bad"
        
        return feedback
    
    def _satisfies_condition(self, x=None):
        if not x and x != 0:
            return self._numbers_obj.get_number_info("is prime", self._number)
        else:
            return self._numbers_obj.get_number_info("is prime", x)