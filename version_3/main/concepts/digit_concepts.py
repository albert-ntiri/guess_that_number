"""
The digit_concepts.py module is part of the concepts package.  It represents the math concepts of counts and sums
of a number's digits.  Hints related to counts and sums of digits include main hints only.

Classes:
    DigitSum
    DigitLength
"""


from concepts.math_concept import DigitConcept



class DigitSum(DigitConcept):
    """
    The DigitSum class is for the math concept of the sum of a number's digits.  It inherits from DigitConcept.
    """
    
    _name = "digit sum"
    
    def __init__(self, number, numbers_obj, digit_sum_data_obj):
        super().__init__(number, numbers_obj, digit_sum_data_obj)
        self._formula = sum
        self._min_number_to_include = 10



class DigitLength(DigitConcept):
    """
    The DigitLength class is for the math concept of a number's size by count of digits.  It inherits from DigitConcept.
    """
    
    _name = "digit length"
    
    def __init__(self, number, numbers_obj, digit_length_data_obj):
        super().__init__(number, numbers_obj, digit_length_data_obj)
        self._formula = len
        self._min_number_to_include = 100