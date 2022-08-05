"""
The outcome_data_storers.py module is part of the data_storers package.  It consists of classes for storing
data at the end of a game, based on the outcome, feedback, and whether the user elected to play again.

Classes:
    OutcomeDataStorer
    OutcomeEntry
    OutcomeUpdater
    PlayAgainUpdate
    FeedbackUpdate
    OutcomeStorageManager
"""


from app_data.data_storers.data_storer_components import GameComponentStorer, StorageManager



class OutcomeDataStorer(GameComponentStorer):
    """
    The OutcomeDataStorer class inherits from GameComponentStorer.  It is for entries into the outcome table
    in the database.  It does not add any new functionality; it is there for organizational purposes.
    """
    
    def update_db_table(self):
        pass
    
    def _set_parameters(self):
        pass



class OutcomeEntry(OutcomeDataStorer):
    """
    The OutcomeEntry class inherits from OutcomeDataStorer.  It implements the updates for the conclusion of
    a game.
    """
    
    _update_query = """
        INSERT INTO outcome(game_id, session_id, outcome_type_id, score, time, play_again) 
        VALUES (:game_id, :session_id, :outcome_type_id, :score, datetime('now', 'localtime'), :play_again);
        """
    _update_query_no_score = """
        INSERT INTO outcome(game_id, session_id, outcome_type_id, time, play_again) 
        VALUES (:game_id, :session_id, :outcome_type_id, datetime('now', 'localtime'), :play_again);
        """
    
    def __init__(self, session, outcome_obj):
        super().__init__(session)
        self._outcome_obj = outcome_obj
        self._outcome_type_id = self._outcome_obj.get_id()
    
    def update_db_table(self):
        self._set_parameters()
        if self._outcome_obj.get_name() == "win":
            self._db.run_query(OutcomeEntry._update_query, self._parameters, _db_path=self._session._db_path)
        else:
            self._db.run_query(OutcomeEntry._update_query_no_score, self._parameters, _db_path=self._session._db_path)
    
    def _set_parameters(self):
        self._parameters.update({
            'outcome_type_id': int(self._outcome_type_id),
            'play_again': 0
        })
        
        if self._outcome_obj.get_name() == "win":
            self._parameters.update({'score': int(self._outcome_obj.score)})



class OutcomeUpdater(OutcomeDataStorer):
    """
    The OutcomeUpdater class inherits from OutcomeDataStorer.  It is for new updates to the outcome table
    in the database after the original outcome record was inserted.
    """
    
    def __init__(self, session):
        super().__init__(session)
        
        outcome_id_query = self._session.build_query("outcome_id", "outcome", "game_id", str(self._game_id))
        self._outcome_id = self._db.run_query(outcome_id_query, fetch='one', _db_path=self._session._db_path)[0]
    
    def update_db_table(self):
        pass



class PlayAgainUpdate(OutcomeUpdater):
    """
    The PlayAgainUpdate class inherits from OutcomeUpdater.  It implements the updates for users electing to
    play another game.
    """
    
    _update_query = "UPDATE outcome SET play_again = 1 WHERE outcome_id = {};"
    
    def __init__(self, session):
        super().__init__(session)
    
    def update_db_table(self):
        update_query = PlayAgainUpdate._update_query.format(self._outcome_id)
        self._db.run_query(update_query, _db_path=self._session._db_path)



class FeedbackUpdate(OutcomeUpdater):
    """
    The FeedbackUpdate class inherits from OutcomeUpdater.  It implements the updates for feedback users receive
    about their game.  The feedback could be an improvement area or a recommendation for their next game.
    """
    
    _update_query = "UPDATE outcome SET feedback_type = '{}', {} = {} WHERE outcome_id = {};"
    
    def __init__(self, session, feedback_type=None, improvement_area_id=None, recommendation_type=None):
        super().__init__(session)
        self._feedback_type = feedback_type
        self._improvement_area_id = improvement_area_id
        self._recommendation_type = recommendation_type
        
    def update_db_table(self):
        update_col, update_val = self._set_parameters()
        
        update_query = FeedbackUpdate._update_query.format(self._feedback_type, update_col, update_val, self._outcome_id)
        self._db.run_query(update_query, _db_path=self._session._db_path)
    
    def _set_parameters(self):
        if self._improvement_area_id:
            update_col = "improvement_area_id"
            update_val = self._improvement_area_id
        elif self._recommendation_type:
            update_col = "recommendation_type"
            update_val = f"'{self._recommendation_type}'"
        else:
            return
        
        return update_col, update_val



class OutcomeStorageManager(StorageManager):
    """
    The OutcomeStorageManager class is the manager class for database updates when a game is finished.  It
    inherits from StorageManager.
    """
    
    def __init__(self, session, objects):
        super().__init__(session, objects)
        self._record_type = "Outcome"
    
    def update_database(self, db_update_params):
        if db_update_params["entry_type"] == "New":
            self._add_outcome_record_to_db(db_update_params)
        elif db_update_params["entry_type"] == "Updated":
            self._update_outcome_record_in_db(db_update_params)
    
    def _add_outcome_record_to_db(self, db_update_params):
        """This method adds a record to the outcome table in the database when a game is concluded."""
        
        outcome_entry_obj = OutcomeEntry(self._session, db_update_params["outcome_obj"])
        self._process_update(outcome_entry_obj)
    
    def _update_outcome_record_in_db(self, db_update_params):
        """This method takes the outcome record for the most recent game and updates play_again to 1 when 
        the user clicks on the play again button."""
        
        if db_update_params["update_type"] == "play_again":
            outcome_update_obj = PlayAgainUpdate(self._session)
        elif db_update_params["update_type"] == "feedback" and db_update_params["feedback_type"]:
            outcome_update_obj = FeedbackUpdate(self._session, db_update_params["feedback_type"],
                                                db_update_params["improvement_area_id"], db_update_params["recommendation_type"])
        else:
            return
        
        self._process_update(outcome_update_obj, entry_type="Updated")