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
from application_data import AppData
import pandas as pd



class WelcomePage(Screen):
    """
    The WelcomePage class is for the landing page of the app.  On this page, the user sees the 
    instructions, options to select a level of difficulty or a custom range, and a start button to 
    begin the game.  The layout is determined by the .kv file.
    
    Class Attributes:
        low_range: A Kivy variable for the low_range TextInput widget.
        high_range: A Kivy variable for the high_range TextInput widget.
        range_error_msg: A Kivy variable for the label displaying error messages regarding the custom range.
    """
    
    low_range = ObjectProperty(None)
    high_range = ObjectProperty(None)
    range_error_msg = ObjectProperty(None)
    
    def start_game(self, game_obj):
        """This method begins the game, setting the active flag to True, setting the level of 
        difficulty, generating the winning number, generating a list of hints based on the winning 
        number, and prompting the user to enter their first guess.  It also adds a game record to 
        the database."""
        
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
        """This method returns the level of difficulty that was selected by the user.  If a custom 
        range was entered, the level of 4 is returned."""
        
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
        """This method sets the range for the game based on user inputs or the selected level of 
        difficulty."""
        
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
        """This method determines a level of difficulty (easy, medium, or hard) based on the user's 
        selection on the app and sets the number range and penalty attributes based on that level."""
        
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
    """
    The GamePage class is for the page that is displayed while the user is playing the game.  On this page, 
    the user sees the range to guess between, a TextInput box to enter a guess, the number of guesses remaining, 
    a hint to guide the user, an enter a button to submit the user's guess, and a quit button to leave the 
    game.  The layout is determined by the .kv file.
    
    Class Attributes:
        guess_prompt_text: A Kivy variable for the label displaying range the user should guess between.
        status_text: A Kivy variable for the label displaying the number of guesses the user has left.
        guess: A Kivy variable for the TextInput widget where the user enters a guess.
        hint_text: A Kivy variable for the label displaying hints.
    """
    
    guess_prompt_text = ObjectProperty(None)
    status_text = ObjectProperty(None)
    guess = ObjectProperty(None)
    hint_text = ObjectProperty(None)
    
    def check_answer(self, game_obj):
        """This method takes in a number guessed by the user and evaluates whether it matches the winning 
        number.  If it is correct, it displays a congratulatory message and ends the game.  If it is not 
        correct, it deducts the penalty from the score and displays the appropriate message depending on 
        the situation."""
        
        # Retrieve the user's guess from the guess text input widget.
        guess = self.ids.guess.text
        
        # Use the Number object to convert it to an integer.  Display an error message if it is not an integer.
        if not game_obj.num_obj.convert_to_int(guess) and game_obj.num_obj.convert_to_int(guess) != 0:
            message = game_obj.app_text.get_error_msg("game_page", "guess_entry", "non_integer")
            self._display_hint(game_obj, guess, message, error=True, error_type="non_integer")
            return
        else:
            guess = game_obj.num_obj.convert_to_int(guess)
        
        # Evaluate whether the guess is correct and end the game or display a hint based on that.  If the 
        # score runs out, end the game.
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
        """This method concludes the game, adds an outcome record to the database, and displays feedback and a 
        thank you message to the user."""
        
        # Update outcome table in database.
        game_obj.session.add_outcome_record_to_db(outcome, score)
        
        # Generate feedback text from feedback dataframe.
        self._compile_feedback(game_obj, score)
        
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
        """This method takes a hint and displays it on the game page and adds a guess record to the database 
        for the guess and hint that are passed in."""
        
        self.ids.hint_text.text = hint
        if error:
            game_obj.session.add_guess_record_to_db(guess, hint, error=True, error_type=error_type)
        else:
            game_obj.session.add_guess_record_to_db(guess, hint)
    
    def _update_status(self, game_obj):
        """This method calculates the number of guesses the user has left and displays it on the game page."""
        
        guesses_remaining = int(game_obj.score / game_obj.penalty)
        status = game_obj.app_text.get_status(guesses_remaining)
        self.ids.status_text.text = status
    
    def _compile_feedback(self, game_obj, score):
        """This method takes the feedback attribute of the GuessThatNumberGame object and uses it to gather 
        feedback on the most prominent development area for the user.  If the user does not have any developmental 
        feedback, it gets a recommendation for the user.  The resulting message, whether feedback or recommendation 
        is then displayed on the feedback label."""
        
        improvement_areas = game_obj.feedback[(game_obj.feedback.feedback_ind == "bad") & (game_obj.feedback.hint_type != "greater_less")]
        
        if len(improvement_areas):
            top_improvement_area = list(improvement_areas.hint_type.value_counts().index)[0]
            hint_description = game_obj.session.get_hint_description(top_improvement_area)
            
            examples = improvement_areas.loc[improvement_areas.hint_type == top_improvement_area, ["guess", "hint"]].copy()
            examples = examples.values.tolist()
            
            feedback = game_obj.app_text.get_feedback(top_improvement_area, hint_description, examples)
            
            self.manager.farewell_page.ids.feedback_text.text = feedback
            
        elif score:
            recommendation = self._get_recommendation(game_obj, score)
            
            if type(recommendation) == int:
                recommendation_msg = game_obj.app_text.get_recommendation_msg("target score", recommendation)
            elif type(recommendation) == str:
                recommendation_msg = game_obj.app_text.get_recommendation_msg("level of difficulty", recommendation)
            
            self.manager.farewell_page.ids.feedback_text.text = recommendation_msg
    
    def _get_recommendation(self, game_obj, score):
        """This method gets a predicted score and predicted outcome for the user and returns a recommendation 
        based on comparing the predicted score to the actual score.  If the user has played more than 1 game and 
        performed well enough, the user is recommended the next level of difficulty."""
        
        predicted_score = game_obj.app_data.predict_score(game_obj.session.game_ids[-1])
        target_score = 100 if predicted_score > 100 else predicted_score if score < predicted_score else score
        
        if len(game_obj.session.game_ids) > 1:
            predicted_outcome = game_obj.app_data.predict_outcome(game_obj.session.game_ids[-1])
            if predicted_outcome == "win" and target_score > 100 - (game_obj.penalty * 2):
                next_level_of_difficulty = game_obj.session._get_next_level_of_difficulty()
                recommendation = next_level_of_difficulty
            else:
                recommendation = target_score
        else:
            recommendation = target_score
        
        return recommendation
    
    def _generate_feedback(self, game_obj, guess):
        """This method takes in a guess and determines whether the guess matches the last hint that was given.  
        The hint type, hint, guess and feedback indicator are added to the feedback attribute of the 
        GuessThatNumberGame object."""
        
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
    """
    The FarewellPage class is for the last page of the app.  On this page, the user sees a message 
    congratulating and showing a score if he/she won, thanking them for playing, and inviting them to play
    again.  In some cases, it also shows feedback, which could be tips for improvement or a recommendation 
    for a more challenging game.  The layout is determined by the .kv file.
    
    Class Attributes:
        last_msg: A Kivy variable for the label displaying the congratulations and/or farewell message.
        feedback_text: A Kivy variable for the label displaying feedback or a recommendation for the next game.
    """
    
    last_msg = ObjectProperty(None)
    feedback_text = ObjectProperty(None)
    
    def play_again(self, game_obj):
        """This method updates the outcome record to set play_again to 1, resets the game and brings the user 
        back to the welcome page to play the game again."""
        
        # Update play_again column to 1 on outcome record in database.
        game_obj.session.update_outcome_record_in_db()
        
        # Reset game object attributes to default values.
        self._reset_game(game_obj)
        
        # Show the welcome page on the screen.
        game_obj.root.current = "welcome_page"
        self.manager.transition.direction = "right"
    
    def _reset_game(self, game_obj):
        """This method changes attributes to default values and clears message variables and entry fields when 
        the user elects to play another game."""
        
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
    """
    The PageManager class inherits from Kivy's ScreenManager class.  It defines the pages the app is comprised 
    of: welcome page, game page, and farewell page.
    
    Class Attributes:
        welcome_page: A Kivy variable for the welcome page.
        game_page: A Kivy variable for the game page.
        farewell_page: A Kivy variable for the farewell page.
    """
    
    welcome_page = ObjectProperty(None)
    game_page = ObjectProperty(None)
    farewell_page = ObjectProperty(None)



display = Builder.load_file("guess_that_number_design.kv")



class GuessThatNumberGame(App):
    """
    The GuessThatNumberGame class is the main class for the application.  It inherits from Kivy's App class.  
    This is where the app is built and run.
    
    Attributes:
        level_of_difficulty: A field selected by the user, which determines the number range and the penalty.
        number_range: The range in which the winning number is contained.
        winning_number: The number the user has to guess to win the game.
        active: A boolean value indicating whether the game is currently being played.
        score: The current score for the user.
        penalty: The number of points deducted from the score for each incorrect guess.
        num_obj: An object of the Number class.
        hint_obj: An object of the HintGenerator class.
        hints: A list of hints generated to help the user guess the winning number.
        redundant_hints: A list of hints generated from the user's previous guesses to prevent hints that don't
            provide new information.
        feedback: A dataframe of guesses, hints, hint types, and whether the guesses match the hints.
        app_text: An object of the AppText class.
        session: An object of the Session class.
        app_data: An object of the AppData class.
        
        welcome_page: An object of the WelcomePage class.
        game_page: An object of the GamePage class.
        farewell_page: An object of the FarewellPage class.
    """
    
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
        self.app_data = AppData()
    
        self.welcome_page = WelcomePage()
        self.game_page = GamePage()
        self.farewell_page = FarewellPage()
        
    def build(self):
        Window.clearcolor = (.45,.9,0,0)
        
        return display



if __name__ == "__main__":
    GuessThatNumberGame().run()