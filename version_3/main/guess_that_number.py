"""
This file contains the main, high-level classes for the Guess That Number application, including building
the app, running it, and serving as a bridge between the logic of the game and the Kivy implementation of
the user interface.
"""


# Import modules.

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from resources.object_manager import ObjectManager
from resources.games_manager import GamesManager
from resources.infrastructure.text_displayers import TextDisplayManager
from resources.infrastructure.log_entries import PlayAgainLogEntry

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
    
    def start_game(self, app):
        """This method begins the game, setting the active flag to True, setting the level of 
        difficulty, generating the winning number, generating a list of hints based on the winning 
        number, and prompting the user to enter their first guess.  It also adds a game record to 
        the database."""
        
        objects = app.get_objects()
        objects.create_object(TextDisplayManager, "text_display", WelcomePage, objects, self.manager)
        
        games = objects.get_object("games")
        result = games.add_game()
        if result != "error":
            # Show the game page.
            app.root.current = "game_page"
            self.manager.transition.direction = "left"
    
    def set_level_of_difficulty(self, instance, app, value, level="easy"):
        """This method determines a level of difficulty (easy, medium, or hard) based on the user's 
        selection on the app and sets the number range and penalty attributes based on that level."""
        
        objects = app.get_objects()
        data = objects.get_object("data")
        level_obj = data.get_sub_data_object("levels", level)
        app.update_level_obj(level_obj)



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
    
    def check_answer(self, app):
        """This method takes in a number guessed by the user and evaluates whether it matches the winning 
        number.  If it is correct, it displays a congratulatory message and ends the game.  If it is not 
        correct, it deducts the penalty from the score and displays the appropriate message depending on 
        the situation."""
        
        objects = app.get_objects()
        games = objects.get_object("games")
        outcome = games.add_guess_to_current_game()
        
        if outcome:
            self.end_game(app, outcome)
    
    def end_game(self, app, outcome):
        """This method concludes the game, adds an outcome record to the database, and displays feedback and a 
        thank you message to the user."""
        
        objects = app.get_objects()
        games = objects.get_object("games")
        games.end_current_game(outcome)
        
        # Show the farewell page.
        app.root.current = "farewell_page"
        self.manager.transition.direction = "left"



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
    
    feedback_text = ObjectProperty(None)
    last_msg = ObjectProperty(None)
    
    def play_again(self, app):
        """This method updates the outcome record to set play_again to 1, resets the game and brings the user 
        back to the welcome page to play the game again."""
        
        objects = app.get_objects()
        session = objects.get_object("session")
        db_update_params = {"entry_type": "Updated", "update_type": "play_again", "feedback_type": None,
                            "improvement_area_id": None, "recommendation_type": None}
        session.update_database("outcome", db_update_params)
        self._reset_game(app)
        
        # Show the welcome page.
        app.root.current = "welcome_page"
        self.manager.transition.direction = "right"
        
        logs = objects.get_object("logs")
        play_again_log_entry = PlayAgainLogEntry(logs)
        play_again_log_entry.log_all()
    
    def _reset_game(self, app):
        """This method changes attributes to default values and clears message variables and entry fields when 
        the user elects to play another game."""
        
        objects = app.get_objects()
        games = objects.get_object("games")
        games.reset_current_game()
    


class PageManager(ScreenManager):
    """
    The PageManager class inherits from Kivy's ScreenManager class.  It defines the pages the app is comprised 
    of: welcome page, game page, and farewell page.  This class needs to exist to allow the turning of pages
    in the UI and accessing of Kivy variables on the different pages.
    
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
        _objects: An object of the ObjectManager class.  This is the only place this object is instantiated.
        
        Level_obj: An object of a subclass of the Level class, used to capture the user's selection of level
        of difficulty.
        
        _games: An object of the GamesManager class.
        
        welcome_page: An object of the WelcomePage class.
        game_page: An object of the GamePage class.
        farewell_page: An object of the FarewellPage class.
    """
    
    def __init__(self):
        super().__init__()
        self._objects = ObjectManager(self)
        
        # User Inputs
        self.level_obj = None
        
        # Games
        self._games = self._objects.create_object(GamesManager, "games", GuessThatNumberGame, self._objects)
        
        # Pages
        self.welcome_page = self._objects.create_object(WelcomePage, "welcome_page", GuessThatNumberGame)
        self.game_page = self._objects.create_object(GamePage, "game_page", GuessThatNumberGame)
        self.farewell_page = self._objects.create_object(FarewellPage, "farewell_page", GuessThatNumberGame)
    
    def get_objects(self):
        return self._objects
    
    def update_level_obj(self, level_obj):
        self._objects.add_object("level_obj", level_obj)
        self.level_obj = level_obj
    
    def build(self):
        Window.clearcolor = (.45,.9,0,0)
        
        return display



if __name__ == "__main__":
    GuessThatNumberGame().run()