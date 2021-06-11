from application_text import AppText
from number import Number



class HintGenerator:
    """
    The HintGenerator class creates a list of hints to help users guess the winning number.  The hints are based on a
    variety of things, such as odd/even, prime, factor, multiple, and characteristics about the individual digits.
    
    Attributes:
        number: The winning number that the hints are used to help users guess.
        digits: A list of digits that make up the number.
        factors: A list of factors of the number.
        hints: A list of hints that is generated for the number.
        app_text: An object of the AppText class.
        num_obj: An object of the Number class.
        session_obj: An object of the Session class.
    """
    
    def __init__(self, number, session_obj=None):
        """The constructor for this class takes in a number and saves it as an attribute.  It also creates a list of digits
        that make up that number, as well as a list of factors of the number, and saves those lists as attributes."""
        
        self.number = number
        self.digits = [int(d) for d in str(self.number) if d != '-']
        self.factors = [i for i in range(1, self.number + 1) if self._is_factor(self.number, i)]
        self.hints = []
        self.app_text = AppText()
        self.num_obj = Number()
        self.session_obj = session_obj
    
    def check_greater_or_less(self, guess):
        """This method takes in a number guessed by the user, compares it to the winning number, and returns the appropriate
        message depending on whether the guess is too high or too low."""
        
        tag = "greater" if guess < self.number else "less"
        hint = self.app_text.get_static_hint("greater_less", "number", subtype=tag)
        return hint
    
    def generate_hints(self, check_db=True, filter_results=True):
        """This method runs all of the other methods below it to create a list of all of the hints.  The one hint not 
        included is check_greater_or_less, which is generated separately.  If check_db is True, it queries the database 
        first to see if there is an existing set of hints for the number and only runs the other methods if it does not 
        find the number in the database."""
        
        if not check_db:
            self._check_factors()
            self._check_multiples(filter_results)
            self._check_prime()
            self._check_even_odd()
            if self.number >= 0:
                self._check_perfect_square()
            self._check_digit_sum()
            self._check_digit_length()
        
        else:
            hints = self.session_obj.get_hint_list(self.number)
            
            if hints:
                multiple_hints = [hint for hint in hints if hint[0] == "multiple"]
                other_hints = [hint for hint in hints if hint[0] != "multiple"]
                indexes = self.num_obj.unique_random_numbers((0, len(multiple_hints)), 2)
                hints = [multiple_hints[index] for index in indexes] + other_hints
                self.hints = [hint[1] for hint in hints]
            
            else:
                self._check_factors()
                self._check_multiples(filter_results)
                self._check_prime()
                self._check_even_odd()
                if self.number >= 0:
                    self._check_perfect_square()
                self._check_digit_sum()
                self._check_digit_length()
        
        return self.hints
    
    def _check_factors(self):
        """This method checks what factors the winning number has and adds a separate hint for each factor, along with one
        for the number of factors.  It also adds a hint for the number of its digits that are factors."""
        
        # If the number is not prime (more than 2 factors), add a hint for number of factors.
        if len(self.factors) > 2:
            total_main_hint = self.app_text.get_value_based_hint("factor", "number", len(self.factors), subtype="count")
            self.hints.append(total_main_hint)
            
            # Add hints for specific factors, not including the number itself or 1.
            for factor in self.factors[1:-1]:
                ind_main_hint = self.app_text.get_value_based_hint("factor", "number", factor, subtype="individual")
                self.hints.append(ind_main_hint)
        
        # If the number has at least 2 digits and is not prime, add a hint for number of digits that are also factors.
        if len(self.digits) > 1 and len(self.factors) > 2:
            digit_factors = list(set(self.factors) & set(self.digits))
            digits_hint = self.app_text.get_count_based_hint("factor", len(self.digits), len(digit_factors))
            self.hints.append(digits_hint)
        
    def _check_multiples(self, filter_results=True):
        """This method generates a few multiples of the winning number, picks 2 of them at random, and adds a hint for each
        of those 2.  If filter_results is False, it returns all of the hints instead of picking 2 of them."""
        
        multiples = [self.number * i for i in range(1,6)]
        
        if filter_results:
            hint_indexes = self.num_obj.unique_random_numbers((0, len(multiples)), 2)
            for index in hint_indexes:
                hint = self.app_text.get_value_based_hint("multiple", "number", multiples[index])
                if hint not in self.hints:   # Special case to prevent "0 is a multiple" from appearing more than once.
                    self.hints.append(hint)
        
        else:
            for multiple in multiples:
                hint = self.app_text.get_value_based_hint("multiple", "number", multiple)
                if hint not in self.hints:   # Special case to prevent "0 is a multiple" from appearing more than once.
                    self.hints.append(hint)
    
    def _check_prime(self):
        """This method checks if the winning number is a prime number and adds a hint if it is.  It also checks if the
        individual digits are prime and adds a hint indicating the number of them that are, along with one for prime 
        factors."""
        
        # Add a hint if the number is prime (has exactly 2 factors).
        if len(self.factors) == 2:
            main_hint = self.app_text.get_static_hint("prime", "number", "overall")
            self.hints.append(main_hint)
        
        # If the number has more than 1 prime factor, add a hint for the number of prime factors.
        prime_factors = self._prime_count(self.factors[1:])
        if prime_factors > 1:
            prime_factors_hint = self.app_text.get_value_based_hint("prime", "number", prime_factors, "factors")
            self.hints.append(prime_factors_hint)
        
        # If it is at least a 2-digit number, add a hint for the number of prime digits.
        if len(self.digits) > 1:
            prime_digits = self._prime_count(self.digits)
            digits_hint = self.app_text.get_count_based_hint("prime", len(self.digits), prime_digits)
            self.hints.append(digits_hint)
    
    def _check_even_odd(self):
        """This method checks if the number is even or add and adds a hint indicating which it is.  It also checks the
        individual digits and adds another hint if all of them are even or all of them are odd."""
        
        # Add a hint indicating whether the number is even or odd.
        tag = "even" if self._is_factor(self.number, 2) else "odd"
        main_hint = self.app_text.get_static_hint("even_odd", "number", subtype=tag)
        self.hints.append(main_hint)
        
        # If it is at least a 2-digit number, add a hint if all of the digits are even or all of the digits are odd.
        if len(self.digits) > 1:
            even_count = len([d for d in self.digits if self._is_factor(d, 2)])
            
            if even_count == len(self.digits):
                digits_hint = self.app_text.get_static_hint("even_odd", "digits", subtype="even")
                self.hints.append(digits_hint)
            elif even_count == 0:
                digits_hint = self.app_text.get_static_hint("even_odd", "digits", subtype="odd")
                self.hints.append(digits_hint)
            
    def _check_perfect_square(self):
        """This method checks if the winning number is a perfect square and adds a hint if it is.  It also checks the
        individual digits and adds another hint indicating how many of the digits are perfect squares."""
        
        # Add a hint if the number is a perfect square.
        if self.number**.5 in range(0, self.number + 1):
            main_hint = self.app_text.get_static_hint("perfect_square", "number")
            self.hints.append(main_hint)
        
        # If it is at least a 2-digit number, add a hint for the number of digits that are perfect squares.
        if len(self.digits) > 1:
            digit_count = len([d for d in self.digits if (d**.5 in range(0, d+1))])
            digits_hint = self.app_text.get_count_based_hint("perfect_square", len(self.digits), digit_count)
            self.hints.append(digits_hint)
    
    def _check_digit_sum(self):
        """This method adds a hint indicating the sum of the individual digits of the winning number."""
        if len(self.digits) > 1:
            hint = self.app_text.get_value_based_hint("digit_sum", "number", sum(self.digits))
            self.hints.append(hint)
    
    def _check_digit_length(self):
        """This method adds a hint indicating the number of digits contained in the winning number."""
        if len(self.digits) > 2:
            hint = self.app_text.get_value_based_hint("digit_length", "number", len(self.digits))
            self.hints.append(hint)
    
    def _prime_count(self, num_list):
        """This method takes in a list of numbers and returns the number of prime numbers in the list."""
        return len([n for n in num_list if (len([n for i in range(2, n) if self._is_factor(n, i)]) == 0)
                    and n not in [0, 1]])
    
    @staticmethod
    def _is_factor(x, y):
        """This static method takes in 2 numbers and returns a boolean indicating if the second number is a factor of the 
        first."""
        return True if x % y == 0 else False
    
    def __repr__(self):
        return "HintGenerator({}, {}, {})".format(self.number, self.app_text, self.num_obj)
    
    def __str__(self):
        string = "number: {}\n\nhints:\n- ".format(self.number)
        for i in range(len(self.hints) - 1):
            string = string + self.hints[i] + '\n- '
        string = string + self.hints[-1]
        return string