# -*- coding: utf-8 -*-
"""
Created on Tue May 18 07:39:42 2021

@author: alber
"""


import numpy as np
import re



class Number:
    """
    The Number class validates whether specific numbers that come from user entries are integers and generates random 
    numbers for use in picking hints and creating a winning number for the game.
    """
    
    def validate_guess(self, guess, hint, hint_type):
        number = self._pattern_match("\d+", hint, value=True)
        number = int(number) if number else None
        digits = [int(d) for d in str(guess) if d != "-"]
        
        if hint_type == "factor":
            digit_hint = self._pattern_match("digits", hint)
            if not digit_hint:
                individual_factor_hint = self._pattern_match("divisible", hint)
                if individual_factor_hint:
                    feedback = "good" if guess % number == 0 else "bad"
                else:
                    factor_count = len([i for i in range(1, guess + 1) if guess % i == 0])
                    feedback = "good" if factor_count == number else "bad"
            
            else:
                if number:
                    number_count = str(number)
                elif self._pattern_match("None", hint):
                    number_count = "none"
                else:
                    number_count = "all"
                
                digit_count = len([d for d in digits if guess % d == 0 and d != 0])
                if digit_count == 0:
                    guess_digit_count = "none"
                elif digit_count == len(digits):
                    guess_digit_count = "all"
                else:
                    guess_digit_count = str(digit_count)
                
                feedback = "good" if number_count == guess_digit_count else "bad"
        
        elif hint_type == "multiple":
            feedback = "good" if number % guess == 0 else "bad"
        
        elif hint_type == "prime":
            digit_hint = self._pattern_match("digits", hint)
            if not digit_hint:
                factors = [i for i in range(1, guess + 1) if guess % i == 0]
                if not number:
                    feedback = "good" if len(factors) == 2 else "bad"
                else:
                    prime_factors = [f for f in factors if len(
                        [i for i in range(1, f + 1) if f % i == 0]) == 2]
                    feedback = "good" if len(prime_factors) == number else "bad"
            
            else:
                if number:
                    number_count = str(number)
                elif self._pattern_match("None", hint):
                    number_count = "none"
                else:
                    number_count = "all"
                
                digit_count = len([d for d in digits if len(
                        [i for i in range(1, d + 1) if d % i == 0]) == 2])
                if digit_count == 0:
                    guess_digit_count = "none"
                elif digit_count == len(digits):
                    guess_digit_count = "all"
                else:
                    guess_digit_count = str(digit_count)
                
                feedback = "good" if number_count == guess_digit_count else "bad"
        
        elif hint_type == "even_odd":
            winning_number_tag = "even" if self._pattern_match("even", hint) else "odd"
            digit_hint = self._pattern_match("All", hint)
            if not digit_hint:
                guess_tag = "even" if guess % 2 == 0 else "odd"
                feedback = "good" if winning_number_tag == guess_tag else "bad"
            
            else:
                even_digits = len([d for d in digits if d % 2 == 0])
                if even_digits == 0 and winning_number_tag == "odd":
                    feedback = "good"
                elif even_digits == len(digits) and winning_number_tag == "even":
                    feedback = "good"
                else:
                    feedback = "bad"
        
        elif hint_type == "perfect_square":
            digit_hint = self._pattern_match("digits", hint)
            if not digit_hint:
                feedback = "good" if guess**.5 in range(guess + 1) else "bad"
            
            else:
                if number:
                    number_count = str(number)
                elif self._pattern_match("None", hint):
                    number_count = "none"
                else:
                    number_count = "all"
                
                digit_count = len([d for d in digits if d**.5 in range(d + 1)])
                if digit_count == 0:
                    guess_digit_count = "none"
                elif digit_count == len(digits):
                    guess_digit_count = "all"
                else:
                    guess_digit_count = str(digit_count)
                
                feedback = "good" if number_count == guess_digit_count else "bad"
        
        elif hint_type == "digit_sum":
            digit_sum = sum(digits)
            feedback = "good" if digit_sum == number else "bad"
        
        elif hint_type == "digit_length":
            feedback = "good" if len(digits) == len(str(number)) else "bad"
        
        return feedback
    
    def validate_range(self, num_range):
        """This method takes in a range, checks each number the values exist, are integers, and if the low number is less 
        than the high number."""
        
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
    
    def convert_to_int(self, string):
        """This method converts a number in the form of a string and converts it to an integer type. If it is not an 
        integer, it returns False."""
        
        if self._is_integer(string):
            result = int(string)
        else:
            result = False
        
        return result
    
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
    def _pattern_match(pattern, text, value=False):
        match = re.search(re.compile(pattern), text)
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
    def generate_random_number(num_range):
        """This static method takes in a number range and generates a random number that is within that range."""
        
        low = num_range[0]
        high = num_range[1]
        number = np.random.randint(low, high, 1)[0]
        return number