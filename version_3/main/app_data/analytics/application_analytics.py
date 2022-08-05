"""
The application_analytics.py module is part of the analytics package.  It consists of classes for making
specific types of predictions during a game.

Classes:
    Predictor
    ScorePredictor
    OutcomePredictor
    AnalyticsManager
"""


from resources.infrastructure.subsystem import BaseClass, Manager

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from sklearn import linear_model

from app_data.analytics.user_metrics import UserMetricsManager
from app_data.analytics.data_compiler import DataCompiler
from app_data.analytics.model import Model
from resources.infrastructure.log_entries import TrainingDataLogEntry
from resources.infrastructure.iterable_log_entries import FeatureMeansLogEntry, ModelMetricsLogEntry
from resources.infrastructure.iterable_log_entries import ModelCoefficientsLogEntry, PredictionFeaturesLogEntry



class Predictor(BaseClass):
    """
    The Predictor class is the base class for making predictions about a user's game.
    """
    
    _date_format = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, objects, data):
        """The constructor method for this class queries the database for all historical data from the 
        application and stores it in a dataframe.  It also splits the main dataframe, game_data, into 
        a few subset dataframes, capturing specific types of information: no_games, range_errors, 
        games_not_finished, games_finished, and games_won."""
        
        super().__init__()
        
        self._pred_type = ""
        self._algorithm_type = ""
        self._comp_df = None
        self._features = []
        
        self._objects = objects
        self._session = self._objects.get_object("session")
        self._user_metrics = self._objects.get_object("user_metrics")
        self._logs = self._objects.get_object("logs")
        self._db = self._session.get_database()
        self._data = data
        
        self._obj_id_method = self.get_pred_type
        self._standardized_method = self.predict
    
    def predict(self):
        pass
    
    def _calc_game_info(self, game_id, pred_type):
        """This method takes in a game_id and prediction type and returns a list of values for the features
        of the appropriate model, based on the prediction type."""
        
        game_info_query = """
                          SELECT
                              gm.time game_start_time,
                              o.time game_end_time,
                              gm.range_high high_range,
                              gm.range_low low_range,
                              MAX(gs.hint_number) total_hints
                          FROM game gm
                              LEFT JOIN guess gs ON gm.game_id = gs.game_id
                              LEFT JOIN outcome o ON gm.game_id = o.game_id
                          WHERE gm.game_id = """ + str(game_id) + """
                          GROUP BY
                              gm.time,
                              o.time,
                              gm.range_high,
                              gm.range_low
                          """
        
        game_start_time, game_end_time, high_range, low_range, total_hints = self._db.run_query(game_info_query, fetch='all')[0]
        
        range_size = int(high_range) - int(low_range) + 1
        total_hints = int(total_hints) if total_hints else 0
        game_start_time, game_end_time = self._format_dates([game_start_time, game_end_time])
        total_duration = (game_end_time - game_start_time).total_seconds()
        
        game_info = [range_size, total_hints, total_duration]
        
        if pred_type == "score":
            guess_time_ratio = self._calc_guess_time_ratio(game_id, game_start_time)
            game_info.append(guess_time_ratio)
        
        feedback_percent, win_game_percent = self._user_metrics.get_metric_values()
        game_info = game_info + [feedback_percent, win_game_percent]
        
        return game_info
    
    def _format_dates(self, variables):
        formatted_variables = [datetime.strptime(var, Predictor._date_format) for var in variables]
        return formatted_variables
    
    def _log_feature_means(self):
        feature_means = {col: round(self._data[col].mean(), 1) for col in self._features}
        feature_means_log_entry = FeatureMeansLogEntry(self._logs, self._pred_type, feature_means)
        feature_means_log_entry.add_log_entry("prediction")
    
    def _log_model_metrics(self):
        model_metrics = {col: self._comp_df.loc[self.get_model_name(), col] for col in self._comp_df.columns}
        model_metrics_log_entry = ModelMetricsLogEntry(self._logs, self._pred_type, model_metrics)
        model_metrics_log_entry.add_log_entry("prediction")
    
    def _log_prediction_features(self, game_info):
        prediction_features = {col: val for col, val in zip(self._features, game_info)}
        prediction_features_log_entry = PredictionFeaturesLogEntry(self._logs, self._pred_type, prediction_features)
        prediction_features_log_entry.add_log_entry("prediction")
    
    def get_model_name(self):
        return f"{self._algorithm_type.title()} - {self._pred_type.title()}"
    
    def get_pred_type(self):
        return self._pred_type



class ScorePredictor(Predictor):
    """
    The ScorePredictor model inherits from Predictor.  It implements the functionality for predicting the
    score of a game.
    """
    
    _metrics = ["Training R2", "Test R2", "Test RMSE", "Cross Validation Score"]
    
    def __init__(self, objects, data):
        super().__init__(objects, data)
        self._pred_type = "score"
        self._algorithm_type = "linear reg"
        self._features = [
            "range_size",
            "total_hints",
            "total_duration",
            "guess_time_ratio",
            "positive_feedback_percent",
            "win_game_percent"
        ]
        
        lreg = linear_model.LinearRegression()
        self._comp_df = pd.DataFrame(columns=ScorePredictor._metrics)
        data = self._data[(self._data.positive_feedback_percent.notna()) &
                          (self._data.positive_feedback_percent != "") &
                          (self._data.win_game_percent.notna())]
        # data = data.iloc[data.groupby("game_id")["guess_entry_time"].agg(pd.Series.idxmax)]   # intention: 1 row per game
        self._score_predict_model = self._objects.create_object(Model, "score_predict_model", ScorePredictor, lreg, data,
                                                               self._features, "score", "Regression", self.get_model_name())
        self._score_predict_model.build_model(self._comp_df)
        self._score_predict_model.cross_validate(3, self._comp_df)
        
        self._log_feature_means()
        self._log_model_metrics()
        
        coefficients = self._score_predict_model.get_coefficients()
        model_coefficients_log_entry = ModelCoefficientsLogEntry(self._logs, self._pred_type, coefficients)
        model_coefficients_log_entry.add_log_entry("prediction")
    
    def predict(self, game_id):
        game_info = self._calc_game_info(game_id, self._pred_type)
        self._log_prediction_features(game_info)
        predicted_score = self._score_predict_model.predict([game_info])[0]
        predicted_score = int(round(predicted_score))
        
        return predicted_score
    
    def _calc_guess_time_ratio(self, game_id, game_start_time):
        guess_time_query = self._session.build_query("time", "guess", "game_id", str(game_id))
        guess_times = self._db.run_query(guess_time_query, fetch='all')
        guess_times = [x[0] for x in guess_times]
        guess_times = self._format_dates(guess_times)
        guess_durations = [guess_times[0] - game_start_time] + [guess_times[i+1] - guess_times[i] for i in range(len(guess_times) - 1)]
        guess_durations = [x.total_seconds() for x in guess_durations]
        
        guess_time_ratio = round(max(guess_durations) / min(guess_durations), 2)
        
        return guess_time_ratio



class OutcomePredictor(Predictor):
    """
    The OutcomePredictor model inherits from Predictor.  It implements the functionality for predicting the
    outcome of a game.
    """
    
    _metrics = ["Training Accuracy", "Test Accuracy", "Test Precision", "Test Recall"]
    
    def __init__(self, objects, data):
        super().__init__(objects, data)
        self._pred_type = "outcome"
        self._algorithm_type = "logistic reg"
        self._features = [
            "range_size",
            "total_hints",
            "total_duration",
            "positive_feedback_percent",
            "win_game_percent"
        ]
        
        log_reg = linear_model.LogisticRegression(C=1)
        self._comp_df = pd.DataFrame(columns=OutcomePredictor._metrics)
        data = self._data[(self._data.positive_feedback_percent.notna()) &
                          (self._data.positive_feedback_percent != "") &
                          (self._data.win_game_percent.notna())]
        # data = data.iloc[data.groupby("game_id")["guess_entry_time"].agg(pd.Series.idxmax)]   # intention: 1 row per game
        self._outcome_predict_model = self._objects.create_object(Model, "outcome_predict_model", OutcomePredictor, log_reg,
                                                                 data, self._features, "won", "Classification",
                                                                 self.get_model_name())
        self._outcome_predict_model.build_model(self._comp_df)
        
        self._log_feature_means()
        self._log_model_metrics()
    
    def predict(self, game_id):
        game_info = self._calc_game_info(game_id, self._pred_type)
        self._log_prediction_features(game_info)
        predicted_outcome = self._outcome_predict_model.predict([game_info])[0]
        predicted_outcome = "win" if predicted_outcome == 1 else "lose"
        
        return predicted_outcome



class AnalyticsManager(Manager):
    """
    The AnalyticsManager class is composed of an object of the DataCompiler class, as well as objects of
    the ScorePredictor and OutcomePredictor classes.  It uses the DataCompiler object to aggregate the
    historical data from the app and delegates predictions to the Predictor subclasses.
    """
    
    def __init__(self, objects):
        self._objects = objects
        self._session = self._objects.get_object("session")
        self._logs = self._objects.get_object("logs")
        self._db = self._session.get_database()
        self._user_metrics = self._objects.create_object(UserMetricsManager, "user_metrics", AnalyticsManager, self._objects)
        self._data_compiler = self._objects.create_object(DataCompiler, "data_compiler", AnalyticsManager, self._db)
        
        self._games_finished = self._data_compiler.get_df("games_finished")
        self._games_won = self._data_compiler.get_df("games_won")
        training_data_log_entry = TrainingDataLogEntry(self._logs, len(self._games_won), len(self._games_finished))
        training_data_log_entry.add_log_entry("prediction")
        
        self._score_predictor = self._objects.create_object(ScorePredictor, "score_predictor", AnalyticsManager, self._objects,
                                                       self._games_won)
        self._outcome_predictor = self._objects.create_object(OutcomePredictor, "outcome_predictor", AnalyticsManager,
                                                             self._objects, self._games_finished)
        
        super().__init__(Predictor)
    
    def predict(self, pred_type, game_id):
        prediction = self.run_subclass_method(pred_type, game_id)
        return prediction
    
    def update_user_metrics(self, context):
        self._user_metrics.update_user_metrics(context)