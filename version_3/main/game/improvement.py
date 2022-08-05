"""
The improvement.py module is part of the game package.  It is for gathering all feedback from guesses during
a game and generating the feedback users see at the end of a game, based on their largest area of improvement.
The area of improvement is based on the current game and previous games played in the same session.

Classes:
    Improvement
"""


from resources.infrastructure.log_entries import TopImprovementAreaLogEntry, FeedbackComponentLogEntry
from resources.infrastructure.iterable_log_entries import ImprovementAreasLogEntry
from resources.infrastructure.data import FeedbackHintType



class Improvement:
    """
    The Improvement class is instantiated by the GameFeedback class.  It is for when there is an improvement
    area to be shown to the user.
    """
    
    def __init__(self, objects, hints_obj):
        self._objects = objects
        self._games = self._objects.get_object("games")
        self._feedback = self._objects.get_object("feedback")
        self._logs = self._objects.get_object("logs")
        
        self._top_improvement_area = self._get_top_improvement_area()
        self._imp_area_obj = hints_obj.get_hint_obj_from_hint_type(self._top_improvement_area)
    
    def get_feedback(self):
        """This method gets the different components of user feedback and returns the overall message."""
        
        general_feedback, example_feedback, description_feedback = self._get_all_feedback_parts()
        feedback = general_feedback + "\n\n" + example_feedback + "\n\n" + description_feedback
        
        return feedback
    
    def _get_all_feedback_parts(self):
        general_feedback = self._get_feedback_component("general", self._get_imp_area_display_name())
        
        examples = self._get_examples()
        example_feedback = self._get_example_feedback(examples)
        
        description_feedback = self._get_feedback_component("description", self._imp_area_obj.get_description())
        
        return general_feedback, example_feedback, description_feedback
    
    def _get_examples(self):
        df = self._feedback.get_feedback_df()
        examples = df.loc[(df.hint_type == self._top_improvement_area) & (df.feedback_ind == "bad"), ["guess", "hint"]].copy()
        examples = examples.values.tolist()
        
        return examples
    
    def _get_top_improvement_area(self):
        cur_improvement_areas_ranked = self._get_ranked_improvement_areas()
        top_improvement_area = cur_improvement_areas_ranked[0]
        
        if self._games.get_game_count() > 1:
            agg_improvement_areas_ranked = self._get_ranked_improvement_areas(current=False)
            for area in agg_improvement_areas_ranked:
                if area in cur_improvement_areas_ranked:
                    top_improvement_area = area
                    break
        
        if self._logs:
            top_impr_area_log_entry = TopImprovementAreaLogEntry(self._logs, top_improvement_area)
            top_impr_area_log_entry.add_log_entry("feedback")
        
        return top_improvement_area
    
    def _get_imp_area_display_name(self):
        return self._imp_area_obj.get_feedback_display_name() if isinstance(self._imp_area_obj, FeedbackHintType) else ""
    
    def _get_ranked_improvement_areas(self, current=True):
        df = self._feedback._feedback.copy() if current else self._games.get_aggregate_feedback()
        scope = "Current" if current else "Aggregate"
        
        improvement_areas = df[(df.feedback_ind == "bad") & (~df.hint_type.isin(["greater_less", "perfect_cube"]))]
        improvement_areas_ranked = list(improvement_areas.hint_type.value_counts().index)
        if self._logs:
            for index, imp_area_data in enumerate([improvement_areas.hint_type.value_counts(), improvement_areas_ranked]):
                ranked = True if index else False
                improvement_areas_log_entry = ImprovementAreasLogEntry(self._logs, scope, imp_area_data, ranked=ranked)
                improvement_areas_log_entry.add_log_entry("feedback")
        
        return improvement_areas_ranked
    
    def _get_example_feedback(self, examples):
        example_feedback = []
        for ex in examples:
            guess, hint = ex
            ex_feedback = self._get_feedback_component("example", guess, hint)
            example_feedback.append(ex_feedback)
        
        if len(example_feedback) == 1:
            example_feedback = example_feedback[0]
        elif len(example_feedback) > 1:
            example_feedback = "\n".join(example_feedback)
        
        return example_feedback
    
    def _get_feedback_component(self, component_type, *args):
        text = self._objects.get_object("text")
        feedback = text.get_text(f'improvement_{component_type}', *args)
        if self._logs:
            feedback_component_log_entry = FeedbackComponentLogEntry(self._logs, component_type, feedback)
            feedback_component_log_entry.add_log_entry("feedback")
        return feedback
    
    def get_improvement_area_id(self):
        return self._imp_area_obj.get_id()