from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder

from main.tests.test_object_manager import ObjectManagerFake
from main.resources.infrastructure.number import Number, Validator
from main.resources.infrastructure.application_text import TextManager
from main.resources.infrastructure.data import DataManager
from main.game.game_settings import GameSettings
from main.game.game_stats import GameStatsManager
from main.game.hint_manager import HintManager
from main.game.guess import GuessManager
from main.app_data.db import DBManager, SqliteDBConnector
from main.app_data.data_storers.session import Session
from main.resources.infrastructure.text_displayers import TextDisplayManager
from main.game.feedback import FeedbackManager
from main.resources.games_manager import GamesManager



### Setup ObjectManager resource to test other modules

class WelcomePageFake(Screen):
    low_range = ObjectProperty(None)
    high_range = ObjectProperty(None)
    range_error_msg = ObjectProperty(None)

class GamePageFake(Screen):
    guess_prompt_text = ObjectProperty(None)
    status_text = ObjectProperty(None)
    guess = ObjectProperty(None)
    hint_text = ObjectProperty(None)

class FarewellPageFake(Screen):
    feedback_text = ObjectProperty(None)
    last_msg = ObjectProperty(None)

class PageManagerFake(ScreenManager):
    welcome_page = ObjectProperty(None)
    game_page = ObjectProperty(None)
    farewell_page = ObjectProperty(None)

display = Builder.load_file("tests/kv_test_design.kv")

page_manager_fake = PageManagerFake()


objects_fake_global_dict = {}
objects_fake_global_easy = ObjectManagerFake()
objects_fake_global_medium = ObjectManagerFake()
objects_fake_global_hard = ObjectManagerFake()
objects_list = [objects_fake_global_easy, objects_fake_global_medium, objects_fake_global_hard]

for level, objects_fake_global in zip(["easy", "medium", "hard"], objects_list):
    numbers = objects_fake_global.create_object(Number, "numbers", ObjectManagerFake)
    text = objects_fake_global.create_object(TextManager, "text", ObjectManagerFake)
    data = objects_fake_global.create_object(DataManager, "data", ObjectManagerFake, text)
    
    db_manager = objects_fake_global.create_object(DBManager, "db_manager", ObjectManagerFake, numbers, data)
    db_path = "tests/sqlite_guess_that_number.db"
    session = objects_fake_global.create_object(Session, "session", ObjectManagerFake, objects_fake_global, db_path)
    db_connector = SqliteDBConnector()
    db_connector.run_query(f"DELETE FROM session;", _db_path=db_path)
    
    difficulty_level = data.get_sub_data_object("levels", level)
    objects_fake_global.add_object("level_obj", difficulty_level)
    settings = objects_fake_global.create_object(GameSettings, "settings", ObjectManagerFake, numbers, difficulty_level)
    settings.set_game_settings("", "")
    
    text_display = objects_fake_global.create_object(TextDisplayManager, "text_display", ObjectManagerFake, objects_fake_global,
                                                     page_manager_fake)
    stats = objects_fake_global.create_object(GameStatsManager, "stats", ObjectManagerFake, objects_fake_global)
    hints = objects_fake_global.create_object(HintManager, "hints", ObjectManagerFake, objects_fake_global)
    guesses = objects_fake_global.create_object(GuessManager, "guesses", ObjectManagerFake, objects_fake_global)
    feedback = objects_fake_global.create_object(FeedbackManager, "feedback", ObjectManagerFake, objects_fake_global)
    
    objects_fake_global_dict[level] = objects_fake_global


objects_game_level = ObjectManagerFake()
numbers = objects_game_level.create_object(Number, "numbers", ObjectManagerFake)
text = objects_game_level.create_object(TextManager, "text", ObjectManagerFake)
data = objects_game_level.create_object(DataManager, "data", ObjectManagerFake, text)
text_display = objects_game_level.create_object(TextDisplayManager, "text_display", ObjectManagerFake, objects_game_level,
                                                 page_manager_fake)

db_manager = objects_game_level.create_object(DBManager, "db_manager", ObjectManagerFake, numbers, data)
db_path = "tests/sqlite_guess_that_number.db"
session = objects_game_level.create_object(Session, "session", ObjectManagerFake, objects_game_level, db_path)
db_connector = SqliteDBConnector()
db_connector.run_query(f"DELETE FROM session;", _db_path=db_path)

difficulty_level = data.get_sub_data_object("levels", "easy")
objects_game_level.add_object("level_obj", difficulty_level)
games_manager = objects_game_level.create_object(GamesManager, "games", ObjectManagerFake, objects_game_level)

objects_fake_global_dict["game_level"] = objects_game_level


text_display.clear_all_variables()