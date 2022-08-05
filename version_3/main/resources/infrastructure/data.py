"""
The data.py module is part of the infrastructure package.  It contains a set of a classes that define the
possible values for commonly used categorical fields, including level of difficulty types, error types,
hint types, and outcome types.  These are used to populate the type tables in the database, as well as
serve as the reference point for their values when they are used in the app.

Classes:
    DataPoint
    
    Level
    StandardLevel
    CustomLevel
    LevelOfDifficultyTypes
    
    Error
    RangeEntryError
    GuessEntryError
    ErrorTypes
    
    HintType
    FeedbackHintType
    NoFeedbackHintType
    HintTypes
    
    GameOutcome
    SuccessfulOutcome
    UnsuccessfulOutcome
    OutcomeTypes
    
    DataManager
"""


from resources.infrastructure.subsystem import BaseClass, Manager
import re



class DataPoint:
    """
    The DataPoint class is the base class for all other classes that represent categorical fields
    of a particular type of value.
    """
    
    def __init__(self, name, _id):
        self._name = name
        self._id = _id
        
        self._obj_id_method = self.get_name
        self._standardized_method = self._get_data_point_info
    
    def get_name(self):
        return self._name
    
    def get_id(self):
        return self._id
    
    def _get_data_point_info(self):
        return self._id, self._name



class Level(DataPoint, BaseClass):
    """
    The Level class is the base class for level of difficulty types.  Each difficulty level has a
    number range and a penalty associated with it.  It inherits from DataPoint.
    """
    
    def __init__(self, name, _id, num_range, penalty):
        super().__init__(name, _id)
        self._number_range = num_range
        self._penalty = penalty
    
    def get_number_range(self):
        return self._number_range
    
    def get_penalty(self):
        return self._penalty



class StandardLevel(Level):
    """
    The StandardLevel class is for the difficulty levels with preset ranges.  It inherits from Level.
    """
    
    def __init__(self, name, _id, num_range, penalty):
        super().__init__(name, _id, num_range, penalty)



class CustomLevel(Level):
    """
    The CustomLevel class allows users to set their own range.  It inherits from Level.
    """
    
    def __init__(self, name="custom", _id=4, num_range=None, penalty=10):
        super().__init__(name, _id, num_range, penalty)



class LevelOfDifficultyTypes(Manager):
    """
    The LevelOfDifficultyTypes class is composed of objects of the subclasses of Level that represent
    all of the possible values for level of difficulty types.
    """
    
    _category = "levels"
    
    def __init__(self):
        self._easy = StandardLevel("easy", 1, num_range=(1,10), penalty=10)
        self._medium = StandardLevel("medium", 2, num_range=(1,100), penalty=20)
        self._hard = StandardLevel("hard", 3, num_range=(1,1000), penalty=25)
        self._custom = CustomLevel()
        super().__init__(Level)
    
    def get_level_obj(self, level):
        level_obj = self.get_subclass_obj(level)
        return level_obj
    
    @classmethod
    def get_category(cls):
        return LevelOfDifficultyTypes._category



class Error(DataPoint, BaseClass):
    """
    The Error class is the base class for error types.  It inherits from DataPoint.
    """
    
    def __init__(self, name, _id, message):
        super().__init__(name, _id)
        self._category = ""
        self._message = message
    
    def get_category(self):
        return self._category
    
    def get_message(self):
        return self._message
    
    def _get_data_point_info(self):
        return self._id, self._category, self._name



class RangeEntryError(Error):
    """
    The RangeEntryError class is for error types that occur when entering a number range.  It inherits
    from Error.
    """
    
    category = "range_entry"
    
    def __init__(self, name, _id, message):
        super().__init__(name, _id, message)
        self._category = RangeEntryError.category



class GuessEntryError(Error):
    """
    The GuessEntryError class is for error types that occur when entering a guess.  It inherits from
    Error.
    """
    
    category = "guess_entry"
    
    def __init__(self, name, _id, message):
        super().__init__(name, _id, message)
        self._category = GuessEntryError.category



class ErrorTypes(Manager):
    """
    The ErrorTypes class is composed of objects of the subclasses of Error that represent all of the
    possible values for error types.
    """
    
    _category = "errors"
    
    def __init__(self, text_obj):
        self._text = text_obj
        
        self._comparison_error = self._create_error_obj(RangeEntryError, "comparison", 1)
        self._missing_error = self._create_error_obj(RangeEntryError, "missing", 2)
        self._invalid_error = self._create_error_obj(RangeEntryError, "invalid", 3)
        self._non_integer_error = self._create_error_obj(GuessEntryError, "non_integer", 4)
        self._out_of_range_error = self._create_error_obj(GuessEntryError, "out_of_range", 5)
        super().__init__(Error)
    
    def get_error_obj(self, error_type):
        error_obj = self.get_subclass_obj(error_type)
        return error_obj
    
    def _create_error_obj(self, error_class, error_type, i):
        error_message = self._text.get_text(f"{error_class.category}_{error_type}")
        error_obj = error_class(error_type, i, error_message)
        return error_obj
    
    @classmethod
    def get_category(cls):
        return ErrorTypes._category



class HintType(DataPoint, BaseClass):
    """
    The HintType class is the base class for hint types.  It inherits from DataPoint.
    """
    
    def __init__(self, name, _id, description, main_hint, hint_display_name):
        super().__init__(name, _id)
        self._description = description
        self._main_hint = main_hint
        self._hint_display_name = hint_display_name
    
    def get_description(self):
        return self._description
    
    def get_main_hint(self):
        return self._main_hint
    
    def get_hint_display_name(self):
        return self._hint_display_name
    
    def _get_data_point_info(self):
        return self._id, self._name, self._description



class FeedbackHintType(HintType):
    """
    The FeedbackHintType class is for hint types that feedback is provided for.  It inherits from
    HintType.
    """
    
    def __init__(self, name, _id, description, main_hint, hint_display_name, feedback_display_name):
        super().__init__(name, _id, description, main_hint, hint_display_name)
        self._feedback_display_name = feedback_display_name
    
    def get_feedback_display_name(self):
        return self._feedback_display_name



class NoFeedbackHintType(HintType):
    """
    The NoFeedbackHintType class is for hint types that feedback is not provided for.  No feedback is
    provided when a definition was not found when scraping for definitions of the concept, or for the
    greater/less concept.  It inherits from HintType.
    """
    
    def __init__(self, name, _id, description, main_hint, hint_display_name):
        super().__init__(name, _id, description, main_hint, hint_display_name)



class HintTypes(Manager):
    """
    The HintTypes class is composed of objects of the subclasses of HintType that represent all of the
    possible values for hint types.
    """
    
    _category = "hints"
    
    def __init__(self, text_obj):
        self._text = text_obj
        
        self._factor = self._create_hint_obj(FeedbackHintType, "factor", 1, "factor|divisible", "factors")
        self._multiple = self._create_hint_obj(FeedbackHintType, "multiple", 2, "multiple", "multiples")
        self._prime = self._create_hint_obj(FeedbackHintType, "prime", 3, "prime", "prime numbers")
        self._even_odd = self._create_hint_obj(FeedbackHintType, "even_odd", 4, "even|odd", "even/odd numbers")
        self._perfect_square = self._create_hint_obj(FeedbackHintType, "perfect_square", 5, "perfect square", "perfect squares")
        self._perfect_cube = self._create_hint_obj(NoFeedbackHintType, "perfect_cube", 6, "perfect cube")
        self._digit_sum = self._create_hint_obj(FeedbackHintType, "digit_sum", 7, "sum", "digit sums")
        self._digit_length = self._create_hint_obj(FeedbackHintType, "digit_length", 8, "-digit number", "n-digit numbers")
        self._greater_less = self._create_hint_obj(NoFeedbackHintType, "greater_less", 9, "Higher|Lower")
        super().__init__(HintType)
    
    def get_hint_obj_from_hint_type(self, hint_type):
        hint_obj = self.get_subclass_obj(hint_type)
        return hint_obj
    
    def get_hint_obj_from_hint(self, hint):
        hint_objs = [self._subclass_list[i] for i in [1, 2, 0, 4, 5, 3, 8, 6, 7]]
        for hint_obj in hint_objs:
            match = re.findall(re.compile(hint_obj.get_hint_display_name()), hint)
            if match:
                return hint_obj
    
    def _create_hint_obj(self, hint_class, hint_type, i, hint_display_name, feedback_display_name=None):
        main_hint = self._text.get_text(hint_type)
        description = self._text.get_hint_description(hint_type)
        
        args = [hint_type, i, description, main_hint, hint_display_name]
        if hint_class == FeedbackHintType:
            args.append(feedback_display_name)
        
        hint_obj = hint_class(*args)
        
        return hint_obj
    
    @classmethod
    def get_category(cls):
        return HintTypes._category



class GameOutcome(DataPoint, BaseClass):
    """
    The GameOutcome class is the base class for outcome types.  It inherits from DataPoint.
    """
    
    def __init__(self, name, _id, message):
        super().__init__(name, _id)
        self._message = message
    
    def get_message(self):
        return self._message



class SuccessfulOutcome(GameOutcome):
    """
    The SuccessfulOutcome class is for outcome types where the user guesses the winning number.  For
    successful outcomes, a score is provided.  It inherits from GameOutcome.
    """
    
    def __init__(self, name, _id, message):
        super().__init__(name, _id, message)
        self._score = None
    
    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        self._score = value
        self._message = self._message.format(value)



class UnsuccessfulOutcome(GameOutcome):
    """
    The UnsuccessfulOutcome class is for outcome types where the user runs out of guesses or quits.
    It inherits from GameOutcome.
    """
    
    def __init__(self, name, _id, message):
        super().__init__(name, _id, message)



class OutcomeTypes(Manager):
    """
    The OutcomeTypes class is composed of objects of the subclasses of GameOutcome that represent all
    of the possible values for outcome types.
    """
    
    _category = "outcomes"
    
    def __init__(self, text_obj):
        self._text = text_obj
        
        self._win = self._create_outcome_obj(SuccessfulOutcome, "win", 1)
        self._lose = self._create_outcome_obj(UnsuccessfulOutcome, "lose", 2)
        self._quit = self._create_outcome_obj(UnsuccessfulOutcome, "quit", 3)
        super().__init__(GameOutcome)
    
    def get_outcome_obj(self, outcome_type):
        outcome_obj = self.get_subclass_obj(outcome_type)
        return outcome_obj
    
    def reset(self):
        self._win.score = None
        self._win._message = self._text.get_text('outcome_win')
    
    def _create_outcome_obj(self, outcome_class, outcome_type, i):
        outcome_message = self._text.get_text(f"outcome_{outcome_type}")
        outcome_obj = outcome_class(outcome_type, i, outcome_message)
        return outcome_obj
    
    @classmethod
    def get_category(cls):
        return OutcomeTypes._category



class DataManager:
    """
    The DataManager class is composed of objects of the different type classes: LevelOfDifficultyTypes,
    ErrorTypes, HintTypes, and OutcomeTypes.  It serves as a centralized place to access information
    about any of the other classes in this module.
    """
    
    def __init__(self, text_obj):
        self._text = text_obj
        
        self._levels = LevelOfDifficultyTypes()
        self._errors = ErrorTypes(self._text)
        self._hints = HintTypes(self._text)
        self._outcomes = OutcomeTypes(self._text)
        self._object_types = {
            "level_of_difficulty_types": self._levels,
            "error_types": self._errors,
            "hint_types": self._hints,
            "outcome_types": self._outcomes
        }
    
    def get_data_object(self, object_type):
        return self._object_types[object_type]
    
    def get_sub_data_object(self, category, sub_object_type):
        if category == "levels":
            return self._levels.get_level_obj(sub_object_type)
        elif category == "errors":
            return self._errors.get_error_obj(sub_object_type)
        elif category == "hints":
            return self._hints.get_hint_obj_from_hint_type(sub_object_type)
        elif category == "outcomes":
            return self._outcomes.get_outcome_obj(sub_object_type)
    
    def get_type_list(self, category):
        for data_object in self._object_types.values():
            if data_object.get_category() == category:
                return data_object.run_all_subclass_methods()
    
    def get_hint_obj_from_hint(self, hint):
        return self._hints.get_hint_obj_from_hint(hint)
    
    def reset(self):
        self._outcomes.reset()