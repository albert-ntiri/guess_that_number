"""
The data_compiler.py module is part of the analytics package.  It is for pulling historical data for
the app, which is used as the training data for predictions.

Classes:
    DataCompiler
"""


from app_data.analytics.dataframes import *
from app_data.analytics.dataframe_components import DFFormatter
import pandas as pd



class DataCompiler:
    """
    The DataCompiler class queries the database for all historical data from the app, to be used for game predictions.
    """
    
    def __init__(self, db):
        """The constructor method for this class queries the database for all historical data from the 
        application and stores it in a dataframe.  It also splits the main dataframe, game_data, into 
        a few subset dataframes, capturing specific types of information: no_games, range_errors, 
        games_not_finished, games_finished, and games_won."""
        
        self._db = db
        self._formatter = DFFormatter()
        
        # Create game_data, no_games, and range_errors dataframes.
        self._app_data = AppDataDF(self._db)
        self._no_games = NoGamesDF(self._db, base_df=self._app_data._df)
        self._games = GamesDF(self._db, base_df=self._app_data._df)
        self._range_errors = RangeErrorsDF(self._db, base_df=self._games._df)
        
        # Create games_started, and games_summary dataframes.
        games_started_cols = [x for x in list(self._games._df.columns) if x not in ["range_error", "range_error_type_id", 
                                                                          "range_error_type"]]
        self._games_started = GamesStartedDF(self._db, base_df=self._games._df, cols=games_started_cols)
        self._games_summary = GamesSummaryDF(self._db, base_df=self._games_started._df)
        
        # Add aggregate data from games_summary into games_started.
        self._add_agg_cols_to_games_started_df()
        
        # Create games_not_finished (started but no outcome) and games_finished.
        games_not_finished_cols = list(self._games_started._df.loc[:, :"guess_error"].columns)
        self._games_not_finished = GamesNotFinishedDF(self._db, base_df=self._games_started._df, cols=games_not_finished_cols)
        self._games_finished = GamesFinishedDF(self._db, base_df=self._games_started._df)
        
        # Add total_duration, won, and game_count columns to games_summary.
        self._add_games_finished_stats_to_game_summary_df()
        
        # Create games_won from games_finished (games with an outcome_type_id of 1).
        self._games_won = GamesWonDF(self._db, base_df=self._games_finished._df)
        
        # Save dataframes to CSV files.
        self._export_dfs()
    
    def get_df(self, df_name):
        if df_name == "games_finished":
            return self._games_finished._df
        elif df_name == "games_won":
            return self._games_won._df
    
    def _add_agg_cols_to_games_started_df(self):
        for index, col in enumerate(["total_guesses", "total_hints", "total_guess_errors"], start=10):
            self._games_started._df = self._formatter.add_col(
                self._games_started._df, col, self._games_started._df.game_id.map(self._games_summary._df[col]),
                                   insert=True, index=index)
    
    def _add_games_finished_stats_to_game_summary_df(self):
        self._games_summary._df = self._formatter.add_col(
            self._games_summary._df, "total_duration", self._games_summary._df.game_end_time - self._games_summary._df.game_start_time,
                               insert=True, index=20)
        self._games_summary._df = self._formatter.transform_col(self._games_summary._df, "total_duration", "convert to seconds")
        self._games_summary._df = self._formatter.add_col(self._games_summary._df, "won", self._games_summary._df.index.map(
            lambda x: 1 if self._games_summary._df.at[x, "outcome_type_id"] == 1 else 0), insert=True, index=21)
        self._games_summary._df = self._formatter.add_col(self._games_summary._df, "game_count", self._games_summary._df.session_id.apply(
            lambda x: self._games_summary._df.session_id.value_counts()[x]), insert=True, index=2)
    
    def _export_dfs(self):
        app_dfs = [
            (self._app_data._df, "game_data"),
            (self._no_games._df, "no_games"),
            (self._range_errors._df, "range_errors"),
            (self._games_not_finished._df, "games_not_finished"),
            (self._games_finished._df, "games_finished"),
            (self._games_won._df, "games_won")
        ]
        
        if sum(self._games_started._df.recommendation_type.notna()):
            app_dfs.append((self._games_summary._df, "games_summary"))
        
        for df, name in app_dfs:
            df.to_csv("app_data/data/{}.csv".format(name), index=False)