"""
The perfect_exponents.py module is part of the concepts package.  It represents the math concepts of perfect
squares and perfect cubes.  Hints related to perfect squares and perfect cubes include main hints and digit hints.

Classes:
    PerfectSquare
    PerfectCube
"""


from concepts.math_concept import PerfectExponentConcept



class PerfectSquare(PerfectExponentConcept):
    """
    The PerfectSquare class is for the math concept of perfect squares.  It inherits from PerfectExponentConcept.
    """
    
    _name = "perfect square"
    
    def __init__(self, number, numbers_obj, perfect_square_data_obj):
        super().__init__(number, numbers_obj, perfect_square_data_obj)
        self._digit_hint_display_name = PerfectSquare._name
    
    def include_concept(self):
        return self._number >= 0



class PerfectCube(PerfectExponentConcept):
    """
    The PerfectCube class is for the math concept of perfect cubes.  It inherits from PerfectExponentConcept.
    """
    
    _name = "perfect cube"
    
    def __init__(self, number, numbers_obj, perfect_cube_data_obj):
        super().__init__(number, numbers_obj, perfect_cube_data_obj)
        self._digit_hint_display_name = PerfectCube._name
    
    def include_concept(self):
        return True