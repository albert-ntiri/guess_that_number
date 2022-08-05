"""
The number.py module is part of the infrastructure package.  It contains a set of a classes that involve
different types of operations on numbers, including getting characteristics about numbers, validating user
inputs expected to be numbers, and generating random numbers.

Classes:
    NumberInfo
    Validator
    RandomNumberGenerator
    Number
"""


import numpy as np



class NumberInfo:
    """
    The NumberInfo class provides the logic behind the different math concepts.  It also has some helper methods for those
    concepts, used when generating hints and evaluating guesses.
    """
    
    def __init__(self):
        self._formulas = {
            "prime factors": self._get_prime_factors,
            "digit factors": self._get_digit_factor_count,
            "factors": self._get_factors,
            "digits": self._get_digits,
            "is prime": self._is_prime,
            "is perfect square": self._is_perfect_square,
            "is perfect cube": self._is_perfect_cube,
            "is factor": self._is_factor
            }
    
    def get_formula(self, formula_name):
        return self._formulas[formula_name]
    
    def _get_prime_factors(self, x):
        factors = self._get_factors(x)
        prime_factors = [factor for factor in factors if self._is_prime(factor)]
        return prime_factors
    
    def _get_digit_factor_count(self, x):
        digits = self._get_digits(x)
        digit_factors = [d for d in digits if self._is_factor(x, d) and d != 0]
        return len(digit_factors)
    
    def _get_factors(self, x):
        factors = [i for i in range(1, x + 1) if self._is_factor(x, i)]
        return factors
    
    @staticmethod
    def _get_digits(x):
        digits = [int(d) for d in str(x) if d != "-"]
        return digits
    
    def _is_prime(self, x):
        factors = self._get_factors(x)
        return True if len(factors) == 2 else False
    
    @staticmethod
    def _is_perfect_square(x):
        result = True if x**.5 in range(0, x + 1) else False
        return result
    
    @staticmethod
    def _is_perfect_cube(x):
        if [i for i in range(-abs(x), abs(x) + 1) if i**3 == x]:
            return True
        return False
    
    @staticmethod
    def _is_factor(x, y):
        if y == 0:
            return False
        return True if x % y == 0 else False



class Validator:
    """
    The Validator class is for validating user inputs.  This includes custom ranges the user enters and guesses entered
    during games.
    """
    
    def validate_guess(self, guess, num_range):
        if not self._is_integer(guess):
            error_type = "non_integer"
        elif not self._is_in_range(guess, num_range):
            error_type = "out_of_range"
        else:
            return
        
        return error_type
    
    def validate_range(self, num_range):
        """This method takes in a range, checks each number the values exist, are integers, and if the low number is less 
        than the high number."""
        
        if len(num_range) != 2 and isinstance(num_range, tuple):
            return
        
        low = num_range[0]
        high = num_range[1]
        
        if self._is_integer(low) and self._is_integer(high):
            if int(high) > int(low):
                return (int(low), int(high))
            else:
                error_type = "comparison"
        elif not len(low.strip()) and not len(high.strip()):
            error_type = "missing"
        else:
            error_type = "invalid"
        
        return error_type
    
    @staticmethod
    def _is_integer(string):
        """This static method takes in a number as astring and returns a boolean value indicating whether it is an 
        integer."""
        
        try:
            float(string)
        except ValueError:
            return False
        else:
            return float(string).is_integer()
    
    @staticmethod
    def _is_in_range(x, num_range):
        return int(x) in [i for i in range(num_range[0], num_range[1] + 1)]



class RandomNumberGenerator:
    """
    The RandomNumberGenerator class is for generating random numbers, whether it is one number or muliple numbers,
    within a range.  It it used to select a winning number, and identify which hints to show.
    """
    
    def unique_random_numbers(self, num_range, n):
        """This method takes in a number range and generates a specified number of unique random numbers within that 
        range."""
        
        numbers = []
        while len(numbers) < n:
            number = self.generate_random_number(num_range)
            if number not in numbers:
                numbers.append(number)
        return numbers
    
    @staticmethod
    def generate_random_number(num_range):
        """This static method takes in a number range and generates a random number that is within that range."""
        
        low = num_range[0]
        high = num_range[1]
        number = np.random.randint(low, high, 1)[0]
        return number



class Number:
    """
    The Number class is composed with objects of the Formula, Validator, and RandomNumberGenerator classes.  It is a
    one-stop shop for mathematical calculations.  This is the only class in this module that is instantiated and
    utilized elsewhere in the app.
    """
    
    def __init__(self):
        self._info = NumberInfo()
        self._validator = Validator()
        self._random = RandomNumberGenerator()
    
    def get_number_info(self, info_type, *args):
        formula = self._info.get_formula(info_type)
        return formula(*args)
    
    def validate_user_entry(self, entry_type, *args):
        if entry_type == "guess":
            return self._validator.validate_guess(*args)
        elif entry_type == "number range":
            return self._validator.validate_range(*args)
    
    def get_random_numbers(self, num_range, n):
        if n == 1:
            return self._random.generate_random_number(num_range)
        elif n > 1:
            return self._random.unique_random_numbers(num_range, n)