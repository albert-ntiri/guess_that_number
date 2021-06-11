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
                    "status": {
                        ("game_page", "status"): "Guesses Remaining: {}"
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
                            "number": "Nice try!  Hint: It is a perfect square.",
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
                    "feedback": {
                        ("farewell_page", "improvement"): {
                            "general": "Feedback:\nSome of your guesses did not match the hints.  For example: {}.",
                            "example": 'Your guess, {}, did not match the hint: "{}"',
                            "definition": "Remember:\n{}"
                        },
                        ("farewell_page", "recommendation"): "Recommended {} for your next game: {}."
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
    
    def get_status(self, n):
        """This method takes in a number and returns the text indicating the number of guesses the user has remaining."""
        text = self.application_text["dynamic"]["status"][("game_page", "status")]
        text = text.format(n)
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
        elif match_count < digit_count:
            hint = hint["some"]
            hint = hint.format(match_count)
        else:
            return
        
        return hint
    
    def get_hint_type(self, hint):
        """This method takes in a hint and returns the corresponding hint type."""
        
        import re
        keywords = {
            "multiple": "multiple",
            "prime": "prime",
            "factor": "factor|divisible",
            "perfect_square": "perfect square",
            "even_odd": "even|odd",
            "greater_less": "Higher|Lower",
            "digit_sum": "sum",
            "digit_length": "-digit number"
        }
        for key, value in keywords.items():
            match = re.findall(re.compile(value), hint)
            if match:
                return key
    
    def get_feedback(self, hint_type, hint_description, examples):
        """This method gets the different components of user feedback and returns the overall message."""
        
        general_feedback = self._get_general_feedback(hint_type)
        description_feedback = self._get_description_feedback(hint_description)
        example_feedback = []
        for ex in examples:
            guess, hint = ex
            ex_feedback = self._get_specific_feedback(guess, hint)
            example_feedback.append(ex_feedback)
        
        if len(example_feedback) == 1:
            example_feedback = example_feedback[0]
        elif len(example_feedback) > 1:
            example_feedback = "\n".join(example_feedback)
        
        feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
        
        return feedback
    
    def _get_general_feedback(self, hint_type):
        """This method returns the first component of user feedback, indicating the area of improveent."""
        
        topics = {
            "multiple": "multiples",
            "prime": "prime numbers",
            "factor": "factors",
            "perfect_square": "perfect squares",
            "even_odd": "even/odd numbers",
            "digit_sum": "digit sums",
            "digit_length": "n-digit numbers"
        }
        topic = topics[hint_type]
        
        feedback = self.application_text["dynamic"]["feedback"][("farewell_page", "improvement")]["general"]
        feedback = feedback.format(topic)
        return feedback
    
    def _get_specific_feedback(self, guess, hint):
        """This method returns the second component of user feedback, showing the example."""
        
        feedback = self.application_text["dynamic"]["feedback"][("farewell_page", "improvement")]["example"]
        feedback = feedback.format(guess, hint)
        return feedback
    
    def _get_description_feedback(self, description):
        """This method returns the third component of user feedback, showing the definition of the topic."""
        
        feedback = self.application_text["dynamic"]["feedback"][("farewell_page", "improvement")]["definition"]
        feedback = feedback.format(description)
        return feedback
    
    def get_recommendation_msg(self, rec_type, value):
        """This method returns a recommendation based on a target score or level of difficulty."""
        
        feedback = self.application_text["dynamic"]["feedback"][("farewell_page", "recommendation")]
        feedback = feedback.format(rec_type, value)
        return feedback
    
    def get_last_msg(self, outcome, score=None):
        """This method looks up the appropriate message to be displayed on the farewell page based on the outcome of the 
        game."""
        
        text = self.application_text["dynamic"]["outcome"][("farewell_page", outcome)]
        text = text.format(score) if outcome == "win" else text
        return text
    
    def __repr__(self):
        return "AppText({})".format(self.application_text)

