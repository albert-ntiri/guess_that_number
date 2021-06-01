# Import libraries.
from tkinter import *
import tkinter.font as font
from tkinter.ttk import *

import numpy as np



# Create main window, add a title, and set a screen size.
root = Tk()
root.title('Guess That Number')
root.geometry('500x500+400+150')



class Number:
    """
    The Number class validates whether specific numbers that come from user entries are integers and generates random 
    numbers for use in picking hints and creating a winning number for the game.
    """
    
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
    """
    
    def __init__(self, number, app_text, num_obj):
        """The constructor for this class takes in a number and saves it as an attribute.  It also creates a list of digits
        that make up that number and saves that list as another attribute."""
        
        self.number = number
        self.digits = [int(d) for d in str(self.number) if d != '-']
        self.factors = []
        self.hints = []
        self.app_text = app_text
        self.num_obj = num_obj
    
    def check_greater_or_less(self, guess):
        """This method takes in a number guessed by the user, compares it to the winning number, and returns the appropriate
        message depending on whether the guess is too high or too low."""
        
        tag = "greater" if guess < self.number else "less"
        hint = self.app_text.get_static_hint("greater_less", "number", subtype=tag)
        return hint
    
    def generate_hints(self):
        """This method runs all of the other methods below it to create a list of all of the hints.  The one hint not
        included is check_greater_or_less, which is generated separately."""
        
        self._check_factors()
        self._check_multiples()
        self._check_prime()
        self._check_even_odd()
        self._check_perfect_square()
        self._check_digit_sum()
        self._check_digit_length()
        return self.hints
    
    def _check_factors(self):
        """This method checks what factors the winning number has and adds a separate hint for each factor.  It also adds
        a hint for each digit that is a factor of the number."""
        
        # Create list of factors for the number.
        self.factors = [i for i in range(1, self.number + 1) if self._is_factor(self.number, i)]
        
        # If the number is not prime (more than 2 factors), add a hint for number of factors.
        if len(self.factors) > 2:
            total_main_hint = self.app_text.get_value_based_hint("factor", "number", len(self.factors), subtype="count")
            self.hints.append(total_main_hint)
            
            # Add a maximum of 2 hints for specific factors, selected randomly, not including the number itself or 1.
            hint_indexes = self.num_obj.unique_random_numbers((0, len(self.factors[1:-1])), 2)
            for i in hint_indexes:
                ind_main_hint = self.app_text.get_value_based_hint("factor", "number", self.factors[1:-1][i], 
                                                                   subtype="individual")
                self.hints.append(ind_main_hint)
        
        # If the number has at least 2 digits and is not prime, add a hint for number of digits that are also factors.
        if len(self.digits) > 1 and len(self.factors) > 2:
            digit_factors = list(set(self.factors) & set(self.digits))
            digits_hint = self.app_text.get_count_based_hint("factor", len(self.digits), len(digit_factors))
            self.hints.append(digits_hint)
        
    def _check_multiples(self):
        """This method generates a few multiples of the winning number, picks 2 of them at random, and adds a hint for each
        of those 2."""
        
        multiples = [self.number * i for i in range(2,6)]
        hint_indexes = self.num_obj.unique_random_numbers((0, len(multiples)), 2)
        for i in hint_indexes:
            hint = self.app_text.get_value_based_hint("multiple", "number", multiples[i])
            if hint not in self.hints:   # Special case to prevent "0 is a multiple" from appearing more than once.
                self.hints.append(hint)
    
    def _check_prime(self):
        """This method checks if the winning number is a prime number and adds a hint if it is.  It also checks if the
        individual digits are prime and adds a hint indicating the number of them that are."""
        
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
            digits_list = [d for d in self.digits if (d != 0) and (d != 1)]
            prime_digits = self._prime_count(digits_list)
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
        return len([n for n in num_list if (len([n for i in range(2, n) if self._is_factor(n, i)]) == 0)])
    
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



class Page():
    """
    The Page class serves as a toolkit for creating each of the pages.  It has defines the style and color variables,
    and provides a set of methods that can be used to create each page.

    Attributes:
        page_style: The variable used to assign the style of a page.
        title_style: The variable used to assign the style of the title.
        container_style: The variable used to assign the style of a container.
        button_style: The variable used to assign the style of a button.
        radiobutton_style: The variable used to assign the style of a radiobutton.
        text_style: The variable used to assign the style of text.
        error_msg_style: The variable used to assign the style of an error message.

        fg_title: The font color for the title
        bg_title: The background color for the title.
        bg_color: The background color for the the app. 
        error_color: The font color for error messages and hints. 
    """

    def __init__(self):
        """The constructor for this class sets values for each of the attributes."""
        
        # Set the names for the different styles used on the application.
        self.page_style = 'Page.TFrame'
        self.title_style = 'Title.TLabel'
        self.container_style = 'Container.TFrame'
        self.button_style = 'Action.TButton'
        self.radiobutton_style = 'Select.TRadiobutton'
        self.text_style = 'Text.TLabel'
        self.error_msg_style = 'Error.TLabel'
        
        # Define the colors used on the application.
        self.fg_title = 'mint cream'
        self.bg_title = 'dark green'
        self.bg_color = 'PaleGreen1'
        self.error_color = 'red'
    
    def create_frame(self, container, name, borderwidth=15):
        """This method creates of Tkinter frame based on the specified borderwidth."""
        
        frame = Frame(container, style=self.container_style, name=name)
        frame.configure(borderwidth=borderwidth)
        return frame
    
    def create_label(self, container, name, text=None, textvariable=None, anchor=None, justify=None, wraplength=None, 
                     style=None):
        """This method creates a label to display text on the page based on a variety of specifications."""
        
        style = self.text_style if style is None else style
        label = Label(container, text=text, textvariable=textvariable, anchor=anchor, justify=justify, 
                      wraplength=wraplength, style=style, name=name)
        return label
    
    def create_radiobutton(self, container, name, text, value):
        """This method creates a radiobutton on a page with the specified text and value passed in."""
        rb = Radiobutton(container, text=text, value=value, style=self.radiobutton_style, name=name)
        return rb
    
    def create_entry(self, container, name, width=5):
        """This method creates an entry field for users to type in a number."""
        entry = Entry(container, width=width, name=name)
        return entry
    
    def create_button(self, container, name, text, command=None):
        """This method creates a button with the specified text and command indicating what should happen when pressed."""
        
        command = '' if command is None else command
        button = Button(container, text=text, style=self.button_style, name=name, command=command)
        return button
    
    def __repr__(self):
        return "Page({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(
            self.page_style, self.title_style, self.container_style, self.button_style, self.radiobutton_style, 
            self.text_style, self.error_msg_style, self.fg_title, self.bg_title, self.bg_color, self.error_color)

    def __str__(self):
        style_names = ["page_style", "title_style", "container_style", "button_style", "radiobutton_style", "text_style", 
                       "error_msg_style"]
        styles = [self.page_style, self.title_style, self.container_style, self.button_style, self.radiobutton_style, 
                  self.text_style, self.error_msg_style]
        
        string1 = "Page Object\n\nStyles:\n- "
        for name, style in zip(style_names, styles):
            string1 = string1 + name + " - {}\n- ".format(style)
        string1 = string1[:-3]
        
        color_names = ["fg_title", "bg_title", "bg_color", "error_color"]
        colors = [self.fg_title, self.bg_title, self.bg_color, self.error_color]
        
        string2 = "Colors:\n- "
        for name, color in zip(color_names, colors):
            string2 = string2 + name + " - {}\n- ".format(color)
        string2 = string2[:-3]
        
        return string1 + "\n\n" + string2



class Header(Page):
    """
    The Header class defines how the title and surrounding header should be displayed, using methods inherited from the
    Page class.
    """
    
    def create_title(self, container, app_text):
        """This method creates the widgets for the header and places them on the page as specified."""
        
        title_container = self.create_frame(root, borderwidth=0, name='title_container')
        title_container.pack(fill=X, ipady=15)
        title_text = app_text.get_static_text("label", "header", "title")
        title_label = Label(title_container, text=title_text, style=self.title_style, anchor='center', name='title_label')
        title_label.pack(fill=BOTH, ipady=20)



class WelcomePage(Page):
    """
    The WelcomePage class defines how the welcome page, the landing page for the app, should be displayed, using methods 
    inherited from the Page class.
    """
    
    def build_page(self, container, app_text):
        """This method creates the widgets for the welcome page and places them on the page as specified."""
        
        # Create main page frame.
        welcome_page = self.create_frame(root, borderwidth=10, name='welcome_page')
        welcome_page.pack(fill=BOTH, ipady=485)
        
        
        # Create instructions container with the text to be displayed in it.
        instructions_container = self.create_frame(welcome_page, borderwidth=0, name='instructions_container')
        instructions_container.pack()
        instructions_text = app_text.get_static_text("label", "welcome_page", "instructions")
        instructions_label = self.create_label(instructions_container, text=instructions_text, anchor='w', justify=LEFT, 
                                         wraplength=478, name='instructions_label')
        instructions_label.pack(fill=X)
        
        
        # Create select level container with the text and the radio buttons to be displayed in it.
        select_level_container = self.create_frame(welcome_page, name='select_level_container')
        select_level_container.pack()
        select_level_text = app_text.get_static_text("label", "welcome_page", "select_level")
        select_level_label = self.create_label(select_level_container, text=select_level_text, anchor='n', 
                                               name='select_level_label')
        select_level_label.pack(side=LEFT, fill=Y)
        levels = ['easy', 'medium', 'hard']
        for l in levels:
            radiobutton = self.create_radiobutton(select_level_container, text=l.title(), value=l, 
                                                       name='radiobutton_{}'.format(l))
            radiobutton.pack(side=LEFT, fill=Y, padx=5)
        
        
        # Create custom range container with the text and entry fields to be displayed in it.
        custom_range_container = self.create_frame(welcome_page, name='custom_range_container')
        custom_range_container.pack()
        custom_range_text = app_text.get_static_text("label", "welcome_page", "custom_range")
        custom_range_label = self.create_label(custom_range_container, text=custom_range_text, name='custom_range_label')
        custom_range_label.pack(side=LEFT, fill=Y)
        
        low_range_text = app_text.get_static_text("label", "welcome_page", "low_range")
        low_range_label = self.create_label(custom_range_container, text=low_range_text, name='low_range_label')
        low_range_label.pack(side=LEFT, fill=Y)
        low_range_entry = self.create_entry(custom_range_container, name='low_range_entry')
        low_range_entry.pack(side=LEFT, fill=Y, padx=5)
        
        high_range_text = app_text.get_static_text("label", "welcome_page", "high_range")
        high_range_label = self.create_label(custom_range_container, text=high_range_text, name='high_range_label')
        high_range_label.pack(side=LEFT, fill=Y)
        high_range_entry = self.create_entry(custom_range_container, name='high_range_entry')
        high_range_entry.pack(side=LEFT, fill=Y, padx=5)
        
        
        # Create range error container with the text to be displayed in it.
        range_error_container = self.create_frame(welcome_page, name='range_error_container')
        range_error_container.pack()
        range_error_label = self.create_label(range_error_container, name='range_error_label')
        range_error_label.pack(side=LEFT, fill=Y)
        
        # Create play button with the text to be displayed in it.
        play_button_text = app_text.get_static_text("button", "welcome_page", "play_button")
        play_button = self.create_button(welcome_page, text=play_button_text, name='play_button')
        play_button.pack(side=BOTTOM, expand=True)



class GamePage(Page):
    """
    The GamePage class defines how the game page, the page the user sees while playing the game, should be displayed, using 
    methods inherited from the Page class.
    """
    
    def build_page(self, container, app_text):
        """This method creates the widgets for the game page and places them on the page as specified."""
        
        # Create main page frame.
        game_page = self.create_frame(root, borderwidth=10, name='game_page')
        game_page.pack(fill=BOTH, ipady=485)
        
        
        # Create guess prompt container with the text to be displayed in it.
        guess_prompt_container = self.create_frame(game_page, name='guess_prompt_container')
        guess_prompt_container.pack()
        guess_prompt_label = self.create_label(guess_prompt_container, wraplength=478, anchor=CENTER, justify=CENTER, 
                                               name='guess_prompt_label')
        guess_prompt_label.pack(ipadx=250, ipady=30)
        
        
        # Create guess container with the text and entry field to be displayed in it.
        guess_container = self.create_frame(game_page, name='guess_container')
        guess_container.pack()
        guess_text = app_text.get_static_text("label", "game_page", "guess_text")
        guess_label = self.create_label(guess_container, text=guess_text, name='guess_label')
        guess_label.pack(side=LEFT, fill=Y)
        guess_entry = self.create_entry(guess_container, name='guess_entry')
        guess_entry.pack(side=LEFT, ipadx=5)
        
        
        # Create hint container with the text to be displayed in it.
        hint_container = self.create_frame(game_page, name='hint_container')
        hint_container.pack()
        hint_label = self.create_label(hint_container, wraplength=478, anchor=CENTER, justify=CENTER, name='hint_label')
        hint_label.pack(ipadx=250, ipady=30)
        
        
        # Create button container with the buttons and text to be displayed in it.
        button_container = self.create_frame(game_page, name='button_container')
        button_container.pack()
        enter_button_text = app_text.get_static_text("button", "game_page", "enter_button")
        enter_button = self.create_button(button_container, text=enter_button_text, name='enter_button')
        enter_button.pack(side=LEFT, expand=True, padx=15)
        quit_button_text = app_text.get_static_text("button", "game_page", "quit_button")
        quit_button = self.create_button(button_container, text=quit_button_text, name='quit_button')
        quit_button.pack(side=LEFT, expand=True, padx=15)



class FarewellPage(Page):
    """
    The FarewellPage class defines how the farewell page, the page the user sees when the game is over, should be displayed,
    using methods inherited from the Page class.
    """
    
    def build_page(self, container, app_text):
        """This method creates the widgets for the farewell page and places them on the page as specified."""
        
        # Create main page frame.
        farewell_page = self.create_frame(root, borderwidth=10, name='farewell_page')
        farewell_page.pack(fill=BOTH, ipady=485)
        
        
        # Create end message container with the text to be displayed in it.
        end_msg_container = self.create_frame(farewell_page, name='end_msg_container')
        end_msg_container.pack()
        end_msg_label = self.create_label(end_msg_container, wraplength=478, anchor=CENTER, justify=CENTER, 
                                          name='end_msg_label')
        end_msg_label.pack(fill=X, ipadx=250, ipady=30)
        
        
        # Create play again button with the text to be displayed in it.
        play_again_button_text = app_text.get_static_text("button", "farewell_page", "play_again_button")
        play_again_button = self.create_button(farewell_page, text=play_again_button_text, name='play_again_button')
        play_again_button.pack(side=BOTTOM, expand=True, ipadx=25)



class AppText:
    """
    The AppText class serves as a centralized location for storing all of the text displayed on the app, including static
    text, hints, and error messages.
    
    Attributes:
        application_text: A dictionary containing all of the text for the app.
    """
    
    def __init__(self):
        """The constructor for this class defines the application_text dictionary for other classes to pull text from to 
        display."""
        
        self.application_text = {
                "static": {
                    "button": {
                        ("welcome_page", "play_button"): "PLAY",
                        ("game_page", "enter_button"): "ENTER",
                        ("game_page", "quit_button"): "QUIT",
                        ("farewell_page", "play_again_button"): "PLAY AGAIN"
                    },
                    "label": {
                        ("header", "title"): "Guess That Number!",
                        ("welcome_page", "instructions"): "Want to test your math skills?  See how quickly you can guess a number.  Select a level of difficulty and then use the hints to guess the number.  The range of numbers and the number of guesses you get depends on the level of difficulty.  Let's play!\n\n",
                        ("welcome_page", "select_level"): "Select a level of difficulty:",
                        ("welcome_page", "custom_range"): "Enter your own range: ",
                        ("welcome_page", "low_range"): "Low",
                        ("welcome_page", "high_range"): "High",
                        ("game_page", "guess_text"): "Enter a number:  "
                    }
                },
                "dynamic": {
                    "guess_prompt": {
                        ("game_page", "guess_prompt"): "Guess a number between {} and {}."
                    },
                    "error_message": {
                        ("welcome_page", "range_entry"): {
                            "comparison": "High value must be greater than low value.",
                            "missing": "No numbers were returned.",
                            "invalid": "Both values must be integers."
                        },
                        ("game_page", "guess_entry"): {
                            "non_integer": "Please enter an integer.",
                            "out_of_range": "Your guess is out of range. Please try again."
                        }
                    },
                    "hint": {
                        ("game_page", "factor"): {
                            "number": {
                                "individual": "Nice try!  Hint: It is divisible by {}.",
                                "count": "Nice try!  Hint: It has {} factors."
                            },
                            "digits": {
                                "none": "Nice try!  Hint: None of its digits are factors.",
                                "one": "Nice try!  Hint: 1 of its digits is a factor.",
                                "some": "Nice try!  Hint: {} of its digits are factors.",
                                "all": "Nice try!  Hint: All of its digits are factors."
                            }
                        },
                        ("game_page", "multiple"): {
                            "number": "Nice try!  Hint: {} is a multiple."
                        },
                        ("game_page", "prime"): {
                            "number": {
                                "overall": "Nice try!  Hint: It is a prime number.",
                                "factors": "Nice try!  Hint: It has {} prime factor(s)."
                            },
                            "digits": {
                                "none": "Nice try!  Hint: None of its digits are prime numbers.",
                                "one": "Nice try!  Hint: 1 of its digits is a prime number.",
                                "some": "Nice try!  Hint: {} of its digits are prime numbers.",
                                "all": "Nice try!  Hint: All of its digits are prime numbers."
                            }
                        },
                        ("game_page", "even_odd"): {
                            "number": {
                                "even": "Nice try!  Hint: It is an even number.",
                                "odd": "Nice try!  Hint: It is an odd number."
                            },
                            "digits": {
                                "even": "Nice try!  Hint: All of its digits are even.",
                                "odd": "Nice try!  Hint: All of its digits are odd."
                            }
                        },
                        ("game_page", "perfect_square"): {
                            "number": "Nice try!  Hint: It is a perfect square..",
                            "digits": {
                                "none": "Nice try!  Hint: None of its digits are perfect squares.",
                                "one": "Nice try!  Hint: 1 of its digits is a perfect square.",
                                "some": "Nice try!  Hint: {} of its digits are perfect squares.",
                                "all": "Nice try!  Hint: All of its digits are perfect squares."
                            }
                        },
                        ("game_page", "digit_sum"): {
                            "number": "Nice try!  Hint: The sum of the digits is {}."
                        },
                        ("game_page", "digit_length"): {
                            "number": "Nice try!  Hint: It is a {}-digit number."
                        },
                        ("game_page", "greater_less"): {
                            "number": {
                                "greater": "Nice try! Higher.",
                                "less": "Nice try! Lower."
                            }
                        }
                    },
                    "outcome": {
                        ("farewell_page", "win"): "That's correct! Congratulations! You are a winner!!!\n\nYour Score: {}\n\n\nThanks for playing! Please come back soon.",
                        ("farewell_page", "lose"): "I'm sorry! You ran out of tries.\n\nThanks for playing! Please come back soon.",
                        ("farewell_page", "quit"): "Thanks for playing! Please come back soon."
                    }
                }
            }
    
    def get_static_text(self, w_type, page, name):
        """This method looks up text for the location specified and returns it.  This text does not change or depend on 
        any variables."""
        
        text = self.application_text["static"][w_type][(page, name)]
        return text
    
    def get_guess_prompt_msg(self, num_range):
        """This method takes in a number range and returns the text instructing the user to guess between that range."""
        
        text = self.application_text["dynamic"]["guess_prompt"][("game_page", "guess_prompt")]
        low = num_range[0]
        high = num_range[1]
        text = text.format(low, high)
        return text
    
    def get_error_msg(self, page, widget, err_type):
        """This method looks up the appropriate error message for the situation specified and returns it."""
        
        text = self.application_text["dynamic"]["error_message"][(page, widget)][err_type]
        return text
    
    def get_static_hint(self, hint_type, scope, subtype=None):
        """This method looks up hints that do not depend on any variables."""
        
        if subtype is None:
            hint = self.application_text["dynamic"]["hint"][("game_page", hint_type)][scope]
        else:
            hint = self.application_text["dynamic"]["hint"][("game_page", hint_type)][scope][subtype]
        
        return hint
    
    def get_value_based_hint(self, hint_type, scope, value, subtype=None):
        """This method looks up hints where a specific value of variable must be included in the hint."""
        
        if subtype is None:
            hint = self.application_text["dynamic"]["hint"][("game_page", hint_type)][scope]
        else:
            hint = self.application_text["dynamic"]["hint"][("game_page", hint_type)][scope][subtype]
        
        hint = hint.format(value)
        
        return hint
    
    def get_count_based_hint(self, hint_type, digit_count, match_count):
        """This method looks up hints based on the number of digits that meet a certain criteria."""
        
        hint = self.application_text["dynamic"]["hint"][("game_page", hint_type)]['digits']
        
        if match_count == 0:
            hint = hint["none"]
        elif match_count == 1:
            hint = hint["one"]
        elif match_count == digit_count:
            hint = hint["all"]
        else:
            hint = hint["some"]
            hint = hint.format(match_count)
        
        return hint
    
    def get_last_msg(self, outcome, score=None):
        """This method looks up the appropriate message to be displayed on the farewell page based on the outcome of the 
        game."""
        
        text = self.application_text["dynamic"]["outcome"][("farewell_page", outcome)]
        text = text.format(score) if outcome == "win" else text
        return text
    
    def __repr__(self):
        return "AppText({})".format(self.application_text)



class AppManager(Page):
    """
    The AppManager class builds the app, adds styling, configures widgets, switches between pages, and looks up widgets.
    
    Attributes:
        pages: A dictionary of the 3 main pages of the app.
        game: An object of the Game class.
        app_text: An object of the AppText class.
        level_of_difficulty: A Tkinter variable for the value the user selects for level of difficulty.
        range_error_message: A Tkinter variable for displaying error messages related to the custom range inputs from users.
        guess_prompt_text: A Tkinter variable for displaying text asking the user to guess between a specific range.
        hint_text: A Tkinter variable for displaying hints if the user guesses incorrectly.
        last_message: A Tkinter variable for displaying the message users see after the game has ended.
    """
    
    def __init__(self, game):
        """The constructor for this class inherits from Page and establishes all of the attributes."""
        
        super().__init__()
        self.pages = {}
        self.game = game
        self.app_text = AppText()
        self.level_of_difficulty = StringVar(value='easy', name='level_of_difficulty')
        self.range_error_message = StringVar(name='range_error_message')
        self.guess_prompt_text = StringVar(name='guess_prompt_text')
        self.hint_text = StringVar(name='hint_text')
        self.last_message = StringVar(name='last_message')
    
    def open_app(self):
        """This method builds the header and each page of the app, sets the styles, configures the widgets, and creates a 
        dictionary of the pages."""
        
        # Assign the appropriate styles to the different widgets
        self.define_styles()
        
        # Create the header and title.
        header = Header()
        header.create_title(self.game.window, self.app_text)
        
        # Create a dictionary of the 3 pages, for reference.
        for p in [WelcomePage, GamePage, FarewellPage]:
            page = p()
            page.build_page(self.game.window, self.app_text)
            self.pages[p] = page
        
        # Configure the widgets with the appropriate text variables and commands.
        self.define_settings()
        
        return self.pages
    
    def define_styles(self):
        """This method defines the style for each widget type, in terms of font and colors."""
        
        self.game.window.s = Style()
        self.game.window.s.configure(self.page_style, background=self.bg_color)
        self.game.window.s.theme_use('alt')
        self.game.window.s.configure(self.title_style, font=('TkDefaultFont', 26, 'bold'), background=self.bg_title, 
                              foreground=self.fg_title)
        self.game.window.s.configure(self.container_style, background=self.bg_color)
        self.game.window.s.configure(self.button_style, font=('TkDefaultFont', 15, 'bold'))
        self.game.window.s.configure(self.radiobutton_style, font=('TkDefaultFont', 11), background=self.bg_color)
        self.game.window.s.configure(self.text_style, font=('TkDefaultFont', 11), background=self.bg_color)
        self.game.window.s.configure(self.error_msg_style, font=('TkDefaultFont', 11, 'bold'), background=self.bg_color, 
                              foreground=self.error_color)
    
    def define_settings(self):
        """This method configures each of the appropriate widgets with variables and commands after they have been 
        initialized."""
        
        # Assign set level of difficulty method to radiobuttons with the argument from the level of difficulty variable.
        levels = ['easy', 'medium', 'hard']
        rb_command = lambda: self.game._set_level_of_difficulty(self.level_of_difficulty.get())
        for l in levels:
            rb = self.get_tk_object(('welcome_page', 'select_level_container', 'radiobutton_{}'.format(l)))
            rb.configure(variable=self.level_of_difficulty, 
                         command=rb_command)
        
        # Assign range error message variable to the range error label.
        range_error_label = self.get_tk_object(('welcome_page', 'range_error_container', 'range_error_label'))
        range_error_label.configure(textvariable=self.range_error_message, style=self.error_msg_style)
        
        # Assign guess prompt text variable to the guess prompt label.
        guess_prompt_label = self.get_tk_object(('game_page', 'guess_prompt_container', 'guess_prompt_label'))
        guess_prompt_label.configure(textvariable=self.guess_prompt_text)
        
        # Assign hint text variable to the hint label.
        hint_label = self.get_tk_object(('game_page', 'hint_container', 'hint_label'))
        hint_label.configure(textvariable=self.hint_text, style=self.error_msg_style)
        
        # Assign last message variable to the end message label.
        end_msg_label = self.get_tk_object(('farewell_page', 'end_msg_container', 'end_msg_label'))
        end_msg_label.configure(textvariable=self.last_message)
        
        # Assign appropriate methods to the 4 buttons.
        play_button = self.get_tk_object(('welcome_page', 'play_button'))
        enter_button = self.get_tk_object(('game_page', 'button_container', 'enter_button'))
        quit_button = self.get_tk_object(('game_page', 'button_container', 'quit_button'))
        play_again_button = self.get_tk_object(('farewell_page', 'play_again_button'))
        play_button.configure(command=self.game.start_game)
        enter_button.configure(command=self.game.check_answer)
        quit_button.configure(command=lambda: self.game.end_game("quit"))
        play_again_button.configure(command=self.game.play_again)
    
    def show_page(self, page):
        """This method changes the page users see to the one passed in."""
        
        # Remove any existing widgets from the main window.
        for p in ['welcome_page', 'game_page', 'farewell_page']:
            frame = self.game.window.children[p]
            frame.pack_forget()
        
        # Place the specified page in the main window so it is visible on the screen.
        pg = self.get_tk_object((page))
        pg.pack(fill=BOTH, ipady=485)
    
    def get_tk_object(self, hierarchy):
        """This helper method looks up the Tkinter object for a specific widget and returns it."""
        
        tk_object = self.game.window
        
        if type(hierarchy) == str:
            tk_object = tk_object.children[hierarchy]
        else:
            for obj in hierarchy:
                tk_object = tk_object.children[obj]
        
        return tk_object
    
    def get_var_value(self, variable):
        """This helper method accesses the current value of a Tkinter variable."""
        return self.game.window.getvar(name=variable)
    
    def set_var_value(self, variable, value):
        """This helper method sets the value of a Tkinter variable to the one specified."""
        self.game.window.setvar(name=variable, value=value)
    
    def __repr__(self):
        return "AppManager({}, {}, {}, {}, {}, {}, {})".format(
            self.pages, self.app_text, self.level_of_difficulty, self.range_error_message, self.guess_prompt_text, 
            self.hint_text, self.last_message)
    
    def __str__(self):
        attr_names = ["pages", "app_text", "level_of_difficulty", "range_error_message", "guess_prompt_text", "hint_text", 
                      "last_message"]
        attrs = [self.pages, self.app_text, self.level_of_difficulty, self.range_error_message, self.guess_prompt_text, 
            self.hint_text, self.last_message]
        
        string = "AppManager Object\n\nAttributes:\n- "
        for name, attribute in zip(attr_names, attrs):
            string = string + name + " - {}\n- ".format(color)
        string = string[:-3]
        
        return string



class Game:
    """
    The Game class defines how the game works.  It creates a winning number, activates the game, evaluates each guess, 
    manages the score, and gives out the hints.  It also sets the level of difficulty of the game.
    
    Attributes:
        self.window: The root window for the application.
        self.app: An object of the AppManager class.
        self.pages: A dictionary of the 3 pages of the app.
        
        number_range: The range in which the winning number is contained and the user has to guess.
        winning_number: The number the user has to guess to win the game.
        active: A boolean value indicating whether the game is currently being played.
        score: The current score of the user.
        penalty: The number of points deducted from the score for each incorrect guess.
        num_object: The object of the Number class that generates random numbers and verifies user entries.
        hint_object: The object of the Hint_Generator class that generated the list of hints.
        hints: A list of hints generated to help the user guess the winning number.
    """
    
    def __init__(self, parent):
        """The constructor method for this class takes in an optional number_range and saves it as an attribute.  If no
        number range is provided, it will be determined by the level of difficulty the user selects."""
        
        self.window = parent
        self.app = AppManager(self)
        self.pages = self.app.open_app()
        
        self.number_range = ()
        self.winning_number = 0
        self.active = False
        self.score = 100
        self.penalty = 0
        self.num_object = Number()
        self.hint_object = None
        self.hints = []
    
    def start_game(self):
        """This method begins the game, setting the active flag to True, setting the level of difficulty, generating the
        winning number, generating a list of hints based on the winning number, and prompting the user to enter their first
        guess."""
        
        # Set active flag to True.
        self.active = True
        
        # Call the set range method to establish the range based on user inputs. Show an error message if applicable.
        result = self._set_range()
        if result is not None:
            message = self.app.app_text.get_error_msg("welcome_page", "range_entry", result)
            self.app.range_error_message.set(message)
            return
        
        # Use Number object to get a winning number, pass it to a HintGenerator object to generate hints, show the game 
        # page, and display the guess prompt message.
        self.winning_number = self.num_object.generate_random_number((self.number_range[0], self.number_range[1] + 1))
        self.hint_object = HintGenerator(self.winning_number, self.app.app_text, self.num_object)
        self.hints = self.hint_object.generate_hints()
        self.app.show_page('game_page')
        message = self.app.app_text.get_guess_prompt_msg(self.number_range)
        self.app.guess_prompt_text.set(message)
    
    def end_game(self, outcome, score=None):
        """This method concludes the game, setting all of the attributes back to their default values, and displaying a 
        thank you message to the user."""
        
        # Reset attributes to default values.
        self._reset_game()
        
        # Retrieve last message based on the outcome of the game.
        if outcome == "win":
            message = self.app.app_text.get_last_msg(outcome, score=self.score).replace('100', str(score))
        else:
            message = self.app.app_text.get_last_msg(outcome)
        
        # Display last message and show the farewell page.
        self.app.last_message.set(message)
        self.app.show_page('farewell_page')
    
    def check_answer(self):
        """This method takes in a number guessed by the user and evaluates whether it matches the winning number.  If it
        is correct, it displays a congratulatory message and ends the game.  If it is not correct, it deducts the penalty
        from the score and displays the appropriate message depending on the situation."""
        
        # Retrieve the user's guess from the guess entry widget.
        guess = self.app.get_tk_object(('game_page', 'guess_container', 'guess_entry')).get()
        
        # Use the Number object to convert it to an integer. Display an error message if it is not an integer.
        if not self.num_object.convert_to_int(guess) and self.num_object.convert_to_int(guess) != 0:
            message = self.app.app_text.get_error_msg("game_page", "guess_entry", "non_integer")
            self.app.hint_text.set(message)
            return
        else:
            guess = self.num_object.convert_to_int(guess)
        
        # Evaluate whether the guess is correct and end the game or display a hint based on that. If the score runs out, end
        # the game.
        if guess == self.winning_number:
            self.end_game("win", score=self.score)
        elif guess not in [i for i in range(self.number_range[0], self.number_range[1] + 1)]:
            message = self.app.app_text.get_error_msg("game_page", "guess_entry", "out_of_range")
            self.app.hint_text.set(message)
            self.score -= self.penalty
        elif len(self.hints) > 0 and self.score > 0:
            hint_index = self.num_object.generate_random_number((0, len(self.hints)))
            hint = self.hints.pop(hint_index)
            self.score -= self.penalty
            self.app.hint_text.set(hint)
        elif self.score > 0:
            hint = self.hint_object.check_greater_or_less(guess)
            self.score -= self.penalty
            self.app.hint_text.set(hint)
        else:
            self.end_game("lose")
    
    def play_again(self):
        """This method brings the user back to the welcome page to play the game again."""
        self.app.show_page('welcome_page')
        self.app.last_message.set('')
    
    def _set_range(self):
        """This method sets the range for the game based on user inputs or the selected level of difficulty."""
        
        # Retrieve user inputs for the custom range.
        low_range = self.app.get_tk_object(('welcome_page', 'custom_range_container', 'low_range_entry')).get()
        high_range = self.app.get_tk_object(('welcome_page', 'custom_range_container', 'high_range_entry')).get()
        
        # Use Number object to validate the range and return the result.
        result = self.num_object.validate_range((low_range, high_range))
        if type(result) == tuple:
            self.number_range = result
            self.penalty = 10
        elif result == "missing":
            level = self.app.level_of_difficulty.get()
            self._set_level_of_difficulty(level=level)
        else:
            return result
    
    def _set_level_of_difficulty(self, level='easy'):
        """This method takes in a level of difficulty (easy, medium, or hard) and sets the number_range and penalty
        attributes based on the level."""
        
        if level == 'easy':
            self.number_range = (1, 10)
            self.penalty = 10
        elif level == 'medium':
            self.number_range = (1, 100)
            self.penalty = 20
        elif level == 'hard':
            self.number_range = (1, 1000)
            self.penalty = 25
    
    def _reset_game(self):
        """This method changes attributes to default values and clears message variables and entry fields at the end of a 
        game."""
        
        self.winning_number = 0
        self.active = False
        self.score = 100
        self.hints.clear()
        self.app.hint_text.set('')
        self.app.range_error_message.set('')
        self.app.get_tk_object(('welcome_page', 'custom_range_container', 'low_range_entry')).delete(0,'end')
        self.app.get_tk_object(('welcome_page', 'custom_range_container', 'high_range_entry')).delete(0,'end')
        self.app.get_tk_object(('game_page', 'guess_container', 'guess_entry')).delete(0,'end')
    
    def __repr__(self):
        string = "Game({}, {}, {}, {}, {}, {}, {})".format(self.number_range, self.winning_number, self.active, self.score,
                                                        self.penalty, self.hint_object, self.hints)
        return string
    
    def __str__(self):
        string1 = "Here is the status for the game:\n\n"
        string2 = "number_range: {}\nwinning_number: {}\nactive: {}\nscore: {}\nhints remaining:\n- ".format(
            self.number_range, self.winning_number, self.active, self.score)
        for i in range(len(self.hints) - 1):
            string2 = string2 + self.hints[i] + '\n- '
        string2 = string2 + self.hints[-1]
        
        return string1 + string2



g = Game(root)
root.mainloop()