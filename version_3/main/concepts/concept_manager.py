"""
The concept_manager.py module is part of the concepts package.  It is for aggregating all of the hints generated
for each of the concepts and delegating the evaluation of guesses to the appropriate concept's subclass of
MathConcept, the base class for concepts.

Classes:
    ConceptManager
"""


from resources.infrastructure.subsystem import Manager
from concepts.math_concept import MathConcept
from concepts.hints import MainHint, DigitHint, FactorHint

from concepts.factor import Factor
from concepts.multiple import Multiple
from concepts.prime import PrimeNumber
from concepts.even_odd import EvenOdd
from concepts.perfect_exponents import PerfectSquare, PerfectCube
from concepts.digit_concepts import DigitSum, DigitLength



class ConceptManager(Manager):
    """
    The ConceptManager class serves as a centralized location for generating hints and evaluating guesses for each math
    concept included in the app.  It is composed of objects of each of the subclasses of MathConcept, as well as some
    helper objects.
    """
    
    def __init__(self, number, numbers_obj, db, data):
        self._number = number
        self._numbers_obj = numbers_obj
        self._db = db
        self._data = data
        
        self._factor = Factor(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "factor"))
        self._multiple = Multiple(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "multiple"))
        self._prime = PrimeNumber(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "prime"))
        self._even_odd = EvenOdd(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "even_odd"))
        self._perfect_square = PerfectSquare(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "perfect_square"))
        self._perfect_cube = PerfectCube(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "perfect_cube"))
        self._digit_sum = DigitSum(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "digit_sum"))
        self._digit_length = DigitLength(self._number, self._numbers_obj, self._data.get_sub_data_object("hints", "digit_length"))
        super().__init__(MathConcept)
        
        self._game_concepts = self._subclass_list
        self._main_concepts = self.get_class_instances(MainHint)
        self._digit_concepts = self.get_class_instances(DigitHint)
        self._factor_concepts = self.get_class_instances(FactorHint)
    
    def generate_hints(self, check_db=True, filter_results=True, _db_path=None):
        """This is the main method for generating hints.  It checks the database for hints first to avoid extra
        processing.  If a set of hints does not exist, it uses the MathConcept subclasses to generate new hints and
        aggregates them."""
        
        game_concepts = self._create_hint_concept_list()
        
        if check_db:
            hint_types = [concept.get_name() for concept in game_concepts]
            hints = self._get_hints_from_db(hint_types, _db_path=_db_path)
        else:
            hints = []
        
        if not hints:
            for concept in game_concepts:
                if concept.get_name() == "multiple":
                    concept_hints = concept.generate_hints(filter_results)
                else:
                    concept_hints = concept.generate_hints()
                
                hints = hints + concept_hints
        
        return hints
    
    def evaluate_guess(self, hint_type, guess, hint):
        feedback = self.run_subclass_method(hint_type, guess, hint)
        
        return feedback
    
    @staticmethod
    def check_greater_or_less(guess, number):
        """This method is used after all possible hints specific to the number have been used."""
        
        tag = "Higher" if guess < number else "Lower"
        hint = f"Nice try!  {tag}."
        return hint
    
    def _create_hint_concept_list(self, concepts=None):
        concepts = concepts if concepts else self._game_concepts
        game_concepts = [concept for concept in concepts if concept.include_concept()]
        return game_concepts
    
    def _get_hints_from_db(self, hint_types, _db_path=None):
        hints = self._check_db_for_hints(hint_types, _db_path=_db_path)
        
        # The logic below ensures no more than 2 multiple hints are included to keep the hint list balanced.
        if hints:
            multiple_hints = [hint for hint in hints if hint[0] == "multiple"]
            other_hints = [hint for hint in hints if hint[0] != "multiple"]
            if len(multiple_hints) > 2:
                indexes = self._numbers_obj.get_random_numbers((0, len(multiple_hints)), n=2)
                hints = [multiple_hints[index] for index in indexes] + other_hints
            
            hints = [hint[1] for hint in hints]
        
        return hints
    
    def _check_db_for_hints(self, hint_types, _db_path=None):
        hint_types_string = self._format_hint_types(hint_types)
        
        query = """SELECT t.code, h.hint
                   FROM hint h
                       JOIN hint_type t ON h.hint_type_id = t.id
                   WHERE h.number = """ + str(self._number) + f"""
                       AND t.code IN ({hint_types_string})"""
        
        hints = self._db.run_query(query, fetch='all', _db_path=_db_path)
        
        return hints
    
    @staticmethod
    def _format_hint_types(hint_types):
        hint_types_string = ""
        for hint_type in hint_types[:-1]:
            hint_types_string = hint_types_string + f"'{hint_type}',"
        
        hint_types_string = hint_types_string + f"'{hint_types[-1]}'"
        
        return hint_types_string