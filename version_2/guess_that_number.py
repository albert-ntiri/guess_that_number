# -*- coding: utf-8 -*-
"""
Created on Thu May 20 13:10:10 2021

@author: alber
"""

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from number import Number
from application_text import AppText
from hints import HintGenerator
from session import Session
import pandas as pd



class WelcomePage(Screen):
    low_range = ObjectProperty(None)
    high_range = ObjectProperty(None)
    range_error_msg = ObjectProperty(None)
    
    def start_game(self, game_obj):
        """This method begins the game, setting the active flag to True, 
        setting the level of difficulty, generating the winning number, 
        generating a list of hints based on the winning number, and prompting
        the user to enter their first guess."""
        
        # Set active flag to True.
        game_obj.active = True
        
        # Call the set range method to establish the range based on user inputs.
        # Show an error message if applicable.
        result = self._set_range(game_obj)
        if result is not None:
            message = game_obj.app_text.get_error_msg("welcome_page", "range_entry", result)
            self.ids.range_error_msg.text = message
            game_obj.session.add_game_record_to_db(error=True, error_type=result)
            return
        game_obj.level_of_difficulty = self._get_level_of_difficulty()
        
        # Use Number object to get a winning number, pass it to a HintGenerator
        # object to generate hints.
        game_obj.winning_number = game_obj.num_obj.generate_random_number(
            (game_obj.number_range[0], game_obj.number_range[1] + 1))
        game_obj.hint_obj = HintGenerator(game_obj.winning_number, game_obj.session)
        game_obj.hints = game_obj.hint_obj.generate_hints()
        
        # Add a new record to the game table in the database, show the game page, and
        # display the guess prompt message and status.
        game_obj.session.add_game_record_to_db()
        game_obj.root.current = "game_page"
        self.manager.transition.direction = "left"
        message = game_obj.app_text.get_guess_prompt_msg(game_obj.number_range)
        self.manager.game_page.ids.guess_prompt_text.text = message
        status = game_obj.app_text.get_status(int(game_obj.score / game_obj.penalty))
        self.manager.game_page.ids.status_text.text = status
    
    def _get_level_of_difficulty(self):
        if not self.ids.low_range.text and not self.ids.high_range.text:
            easy = self.ids.radiobutton_easy.active
            medium = self.ids.radiobutton_medium.active
            hard = self.ids.radiobutton_hard.active
            if easy:
                level = 1
            elif medium:
                level = 2
            elif hard:
                level = 3
        else:
            level = 4
        
        return level
    
    def _set_range(self, game_obj):
        """This method sets the range for the game based on user inputs or the
        selected level of difficulty."""
        
        # Retrieve user inputs for the custom range.
        low_range = self.ids.low_range.text
        high_range = self.ids.high_range.text
        
        # Use Number object to validate the range and return the result.
        result = game_obj.num_obj.validate_range((low_range, high_range))
        if type(result) == tuple:
            game_obj.number_range = result
            game_obj.penalty = 10
        elif result == "comparison" or result == "invalid":
            return result
        else:
            return
    
    def set_level_of_difficulty(self, instance, game_obj, value, level="easy"):
        """This method takes in a level of difficulty (easy, medium, or hard) 
        and sets the number range and penalty attributes based on that level."""
        
        if level == "easy":
            game_obj.number_range = (1, 10)
            game_obj.penalty = 10
        elif level == "medium":
            game_obj.number_range = (1, 100)
            game_obj.penalty = 20
        elif level == "hard":
            game_obj.number_range = (1, 1000)
            game_obj.penalty = 25
    


class GamePage(Screen):
    guess_prompt_text = ObjectProperty(None)
    status_text = ObjectProperty(None)
    guess = ObjectProperty(None)
    hint_text = ObjectProperty(None)
    
    def check_answer(self, game_obj):
        """This method takes in a number guessed by the user and evaluates 
        whether it matches the winning number.  If it is correct, it displays 
        a congratulatory message and ends the game.  If it is not correct, it 
        deducts the penalty from the score and displays the appropriate 
        message depending on the situation."""
        
        # Retrieve the user's guess from the guess text input widget.
        guess = self.ids.guess.text
        
        # Use the Number object to convert it to an integer.  Display an error 
        # message if it is not an integer.
        if not game_obj.num_obj.convert_to_int(guess) and game_obj.num_obj.convert_to_int(guess) != 0:
            message = game_obj.app_text.get_error_msg("game_page", "guess_entry", "non_integer")
            self._display_hint(game_obj, guess, message, error=True, error_type="non_integer")
            return
        else:
            guess = game_obj.num_obj.convert_to_int(guess)
        
        # Evaluate whether the guess is correct and end the game or display a 
        # hint based on that.  If the score runs out, end the game.
        if guess == game_obj.winning_number:
            game_obj.session.add_guess_record_to_db(guess)
            self.end_game(game_obj, "win", score=game_obj.score)
        elif guess not in [i for i in range(game_obj.number_range[0], 
                                            game_obj.number_range[1] + 1)]:
            message = game_obj.app_text.get_error_msg("game_page", "guess_entry", "out_of_range")
            self._display_hint(game_obj, guess, message, error=True, error_type="out_of_range")
            game_obj.score -= game_obj.penalty
            self._update_status(game_obj)
        elif len(game_obj.hints) > 0 and game_obj.score > 0:
            guess_hint_obj = HintGenerator(guess, game_obj.session)
            guess_hints = guess_hint_obj.generate_hints(filter_results=False)
            game_obj.redundant_hints = list(set(game_obj.redundant_hints + guess_hints))
            relevant_hints = [hint for hint in game_obj.hints if hint not in game_obj.redundant_hints]
            
            try:
                hint_index = game_obj.num_obj.generate_random_number((0, len(relevant_hints)))
                hint = relevant_hints[hint_index]
                game_obj.hints.remove(hint)
            except ValueError:
                hint_index = game_obj.num_obj.generate_random_number((0, len(game_obj.hints)))
                hint = game_obj.hints.pop(hint_index)
            
            game_obj.score -= game_obj.penalty
            self._generate_feedback(game_obj, guess)
            self._display_hint(game_obj, guess, hint)
            self._update_status(game_obj)
        elif game_obj.score > 0:
            hint = game_obj.hint_obj.check_greater_or_less(guess)
            game_obj.score -= game_obj.penalty
            self._display_hint(game_obj, guess, hint)
            self._update_status(game_obj)
        else:
            self.end_game(game_obj, "lose")
    
    def end_game(self, game_obj, outcome, score=None):
        """This method concludes the game, setting all of the attributes back
        to their default values, and displaying a thank you message to the 
        user."""
        
        # Update outcome table in database.
        game_obj.session.add_outcome_record_to_db(outcome, score)
        
        # Generate feedback text from feedback dataframe.
        self._compile_feedback(game_obj)
        
        # Retrieve last message based on the outcome of the game.
        if outcome == "win":
            message = game_obj.app_text.get_last_msg(outcome, score=game_obj.score).replace(
                "100", str(score))
        else:
            message = game_obj.app_text.get_last_msg(outcome)
        
        # Display last message and feedback, and show the farewell page.
        self.manager.farewell_page.ids.last_msg.text = message
        game_obj.root.current = "farewell_page"
        self.manager.transition.direction = "left"
    
    def _display_hint(self, game_obj, guess, hint, error=False, error_type=None):
        self.ids.hint_text.text = hint
        if error:
            game_obj.session.add_guess_record_to_db(guess, hint, error=True, error_type=error_type)
        else:
            game_obj.session.add_guess_record_to_db(guess, hint)
    
    def _update_status(self, game_obj):
        guesses_remaining = int(game_obj.score / game_obj.penalty)
        status = game_obj.app_text.get_status(guesses_remaining)
        self.ids.status_text.text = status
    
    def _compile_feedback(self, game_obj):
        improvement_areas = game_obj.feedback[(game_obj.feedback.feedback_ind == "bad") & (game_obj.feedback.hint_type != "greater_less")]
        if len(improvement_areas):
            top_improvement_area = list(improvement_areas.hint_type.value_counts().index)[0]
            hint_description = game_obj.session.get_hint_description(top_improvement_area)
            
            examples = improvement_areas.loc[improvement_areas.hint_type == top_improvement_area, ["guess", "hint"]].copy()
            examples = examples.values.tolist()
            
            feedback = game_obj.app_text.get_feedback(top_improvement_area, hint_description, examples)
            
            self.manager.farewell_page.ids.feedback_text.text = feedback
    
    def _generate_feedback(self, game_obj, guess):
        if not game_obj.session.get_total_hints_given()[0]:
            return
        else:
            last_hint_type, last_hint = game_obj.session.get_last_hint()
            feedback_ind = game_obj.num_obj.validate_guess(guess, last_hint, last_hint_type)
            
            if not len(game_obj.feedback):
                feedback_number = 1
            else:
                feedback_number = len(game_obj.feedback) + 1
            
            game_obj.feedback.loc[feedback_number] = [last_hint_type, last_hint, guess, feedback_ind]
    


class FarewellPage(Screen):
    last_msg = ObjectProperty(None)
    feedback_text = ObjectProperty(None)
    
    def play_again(self, game_obj):
        """This method brings the user back to the welcome page to play the 
        game again."""
        
        # Update play_again column to 1 on outcome record in database.
        game_obj.session.update_outcome_record_in_db()
        
        # Reset game object attributes to default values.
        self._reset_game(game_obj)
        
        # Show the welcome page on the screen.
        game_obj.root.current = "welcome_page"
        self.manager.transition.direction = "right"
    
    def _reset_game(self, game_obj):
        """This method changes attributes to default values and clears message 
        variables and entry fields at the end of a game."""
        
        game_obj.winning_number = 0
        game_obj.active = False
        game_obj.score = 100
        game_obj.hints.clear()
        game_obj.redundant_hints.clear()
        game_obj.feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
        self.manager.welcome_page.ids.low_range.text = ""
        self.manager.welcome_page.ids.high_range.text = ""
        self.manager.welcome_page.ids.range_error_msg.text = ""
        self.manager.game_page.ids.guess.text = ""
        self.manager.game_page.ids.hint_text.text = ""
        self.ids.feedback_text.text = ""
        self.ids.last_msg.text = ""
    


class PageManager(ScreenManager):
    welcome_page = ObjectProperty(None)
    game_page = ObjectProperty(None)
    farewell_page = ObjectProperty(None)



display = Builder.load_file("guess_that_number_design.kv")



class GuessThatNumberGame(App):
    def __init__(self):
        super().__init__()
        
        self.level_of_difficulty = 0
        self.number_range = ()
        self.winning_number = 0
        self.active = False
        self.score = 100
        self.penalty = 0
        self.num_obj = Number()
        self.hint_obj = None
        self.hints = []
        self.redundant_hints = []
        self.feedback = pd.DataFrame(columns=["hint_type", "hint", "guess", "feedback_ind"])
        self.app_text = AppText()
        self.session = Session(self)
    
        self.welcome_page = WelcomePage()
        self.game_page = GamePage()
        self.farewell_page = FarewellPage()
        
    def build(self):
        Window.clearcolor = (0,.7,0,1)
        
        return display



if __name__ == "__main__":
    GuessThatNumberGame().run()