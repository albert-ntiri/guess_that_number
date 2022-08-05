"""
The dataframes.py module is part of the analytics package.  It consists of a set of classes, each of
which represents historical data for a particular scenario.  These classes define how their data is
derived and what it includes.  The classes largely depend on each other, as they build on previous ones
until all historical data is collected and prepared.

Classes:
    AppDataDF
    NoGamesDF
    GamesDF
    RangeErrorsDF
    GamesStartedDF
    GamesSummaryDF
    GamesNotFinishedDF
    GamesFinishedDF
    GamesWonDF
"""


from app_data.analytics.dataframe_components import Dataframe
from resources.variables.dataframe_vars import *



class AppDataDF(Dataframe):
    """
    The AppDataDF class inherits from Dataframe.  It is for all historical data from the application.
    """
    
    def _create_df(self):
        game_data, range_error_data, guess_error_data = self._pull_historical_data()
        
        self._add_error_cols(game_data, range_error_data, "game_id", ["range_error_type_id", "range_error_type"], 10)
        self._add_error_cols(game_data, guess_error_data, "guess_id", ["guess_error_type_id", "guess_error_type"], 21)
        
        datetime_cols = ["app_start_time", "game_start_time", "guess_entry_time", "game_end_time"]
        for col in datetime_cols:
            self._formatter.transform_col(game_data, col, "date")
        
        return game_data
    
    def _pull_historical_data(self):
        game_data = self._creator.create_df_from_query(happy_path_query, game_data_cols)
        range_error_data = self._creator.create_df_from_query(range_error_query, range_error_cols)
        guess_error_data = self._creator.create_df_from_query(guess_error_query, guess_error_cols)
        
        return game_data, range_error_data, guess_error_data
    
    def _add_error_cols(self, df, error_df, id_col, error_cols, start):
        for index, col in enumerate(error_cols, start=start):
            self._formatter.add_col(df, col, df[id_col].map(error_df.set_index(id_col)[col]), insert=True, index=index)



class NoGamesDF(Dataframe):
    """
    The NoGamesDF class inherits from Dataframe.  It is for instances when the app was opened but closed
    without initiating any games.  It is a subset of the dataframe from the GameDataDF class.
    """
    
    def _create_df(self):
        no_games_cols = ["session_id", "app_start_time"]
        no_games = self._creator.create_df_from_subset(self._base_df, self._base_df["game_id"].isna(), no_games_cols)
        
        return no_games



class GamesDF(Dataframe):
    """
    The GamesDF class inherits from Dataframe.  It is for instances when the app was opened and games
    were initiated.  It is a subset of the dataframe from the GameDataDF class.
    """
    
    def _create_df(self):
        games = self._creator.create_df_from_subset(self._base_df, self._base_df["game_id"].notna())
        
        return games



class RangeErrorsDF(Dataframe):
    """
    The RangeErrorsDF class inherits from Dataframe.  It is for instances when a games was initiated but
    there was a validation error in the user input of a custom range.  It is a subset of the dataframe
    from the GamesDF class.
    """
    
    def _create_df(self):
        range_errors_cols = ["session_id", "app_start_time", "game_id", "game_start_time", "range_error", 
                             "range_error_type_id", "range_error_type"]
        range_errors = self._creator.create_df_from_subset(self._base_df, self._base_df["range_error"] == 1, range_errors_cols)
        
        return range_errors



class GamesStartedDF(Dataframe):
    """
    The GamesStartedDF class inherits from Dataframe.  It is for instances when a games was initiated
    without any validation errors in the user input of a custom range.  It is a subset of the dataframe
    from the GamesDF class.
    """
    
    def __init__(self, db, base_df, cols):
        super().__init__(db, base_df, cols)
        self._format_df()
    
    def _create_df(self):
        games_started = self._creator.create_df_from_subset(self._base_df, self._base_df["range_error"] == 0, self._cols)
        
        return games_started
    
    def _format_df(self):
        self._df = self._formatter.format_df(self._df, "drop null", "guess_id")
        for col in ["low_range", "high_range"]:
            self._df = self._formatter.transform_col(self._df, col, "cast", datatype="int")
        
        self._df = self._formatter.add_col(self._df, "range_size", self._df.high_range - self._df.low_range + 1, insert=True,
                                           index=7)
        self._df = self._formatter.add_col(self._df, "avg_guess_time", self._df.guess_id.apply(self._calc_avg_guess_time),
                                           insert=True, index=16)
        self._df = self._formatter.add_col(self._df, "positive_feedback_percent",
                                           self._df.guess_id.apply(self._calc_positive_feedback_percent), insert=True, index=17)
    
    def _calc_avg_guess_time(self, guess_id):
        """This method takes in a guess_id, calculates the average number of seconds it takes the user
        to enter a guess for a specific game, and returns it."""
        
        game_id = self._df.loc[self._df.guess_id == guess_id, "game_id"].iloc[0]
        subset_df = self._df[self._df.game_id == game_id]
        guess_ids = list(subset_df.guess_id.unique())
        guess_ids.sort()
        guess_index = guess_ids.index(guess_id)
        
        guess_entry_time = subset_df.loc[subset_df.guess_id == guess_id, "guess_entry_time"].iloc[0]
        game_start_time = subset_df.loc[subset_df.guess_id == guess_id, "game_start_time"].iloc[0]
        game_time = (game_start_time - game_start_time).total_seconds()
        
        avg_guess_time = round(game_time / (guess_index + 1), 4)
        
        return avg_guess_time
    
    def _calc_positive_feedback_percent(self, guess_id):
        session_id = self._df.loc[self._df.guess_id == guess_id, "session_id"].iloc[0]
        subset_df = self._df[(self._df.session_id == session_id) & 
                             (self._df.guess_id <= guess_id) & 
                             (~self._df.feedback.isna())]
        
        positive_feedback_count = len(subset_df[subset_df.feedback == "good"])
        total_feedback_count = len(subset_df)
        
        if total_feedback_count:
            positive_feedback_percent = positive_feedback_count / total_feedback_count
            
            return positive_feedback_percent



class GamesSummaryDF(Dataframe):
    """
    The GamesSummaryDF class inherits from Dataframe.  It contains game-level data from the games started.
    It is created using a pivot table from the dataframe from the GamesStartedDF class.
    """
    
    def __init__(self, db, base_df, cols=None):
        super().__init__(db, base_df, cols)
        self._format_df()
    
    def _create_df(self):
        games_summary_cols = ["session_id", "app_start_time", "level_of_difficulty_type_id", 
                              "level_of_difficulty_type", "low_range", "high_range", "range_size", "winning_number", 
                              "game_start_time", "outcome_id", "outcome_type_id", "outcome_type", "score", 
                              "feedback_type", "improvement_area_id", "recommendation_type", "game_end_time", 
                              "play_again"]
        
        games_summary = self._creator.create_df_from_pivot_table(self._base_df, "game_id", "guess_id", len)
        
        for col in games_summary_cols:
            self._formatter.add_col(games_summary, col,
                                   self._base_df.pivot_table(index="game_id", values=col, aggfunc=max, dropna=False)[col])
        
        return games_summary
    
    def _format_df(self):
        self._df = self._formatter.format_df(self._df, "rename columns", col_names_dict={"guess_id": "total_guesses"})
        
        self._df = self._formatter.add_col(
            self._df, "total_hints", self._base_df.pivot_table(index="game_id", values="hint_number", aggfunc=max,
                                                             fill_value=0)["hint_number"])
        self._df = self._formatter.add_col(
            self._df, "total_guess_errors", self._base_df.pivot_table(index="game_id", values="guess_error", aggfunc=sum,
                                                                    fill_value=0)["guess_error"])
        
        games_summary_col_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 19, 20, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        self._df = self._formatter.format_df(self._df, "reorder columns", col_order=games_summary_col_order)



class GamesNotFinishedDF(Dataframe):
    """
    The GamesNotFinishedDF class inherits from Dataframe.  It is for instances when a game was started but
    the app was closed before an outcome was reached.  It is a subset of the dataframe from the GamesStartedDF
    class.
    """
    
    def _create_df(self):
        games_not_finished = self._creator.create_df_from_subset(self._base_df, self._base_df["outcome_id"].isna(), self._cols)
        
        return games_not_finished



class GamesFinishedDF(Dataframe):
    """
    The GamesFinishedDF class inherits from Dataframe.  It is for instances when a game was finished.  It
    is a subset of the dataframe from the GamesStartedDF class.
    """
    
    def __init__(self, db, base_df, cols=None):
        super().__init__(db, base_df, cols)
        self._format_df()
    
    def _create_df(self):
        games_finished = self._creator.create_df_from_subset(self._base_df, self._base_df["outcome_id"].notna())
        
        return games_finished
    
    def _format_df(self):
        self._df = self._formatter.transform_col(self._df, "total_hints", "fill na")
        self._df = self._formatter.add_col(self._df, "total_duration", self._df.game_end_time - self._df.game_start_time,
                                           insert=True, index=34)
        self._df = self._formatter.transform_col(self._df, "total_duration", "convert to seconds")
        self._df = self._formatter.add_col(self._df, "won", self._df.game_id.apply(self._calc_won), insert=True, index=35)
        self._df = self._formatter.add_col(self._df, "game_count", self._df.session_id.apply(self._calc_game_count),
                                           insert=True, index=2)
        self._df = self._formatter.add_col(self._df, "win_game_percent", self._df.game_id.apply(self._calc_perc_games_won),
                                           insert=True, index=37)
    
    def _calc_won(self, game_id):
        """This method takes in a game_id and returns an indicator of whether the user won the game."""
        
        game_results = self._df[self._df.game_id == game_id]
        outcome = game_results.outcome_type_id.unique()[0]
        won = 1 if outcome == 1 else 0
        return won
    
    def _calc_game_count(self, session_id):
        """This method takes in a session_id and returns the number of game_ids that session_id has."""
        
        game_ids = list(self._df.loc[self._df.session_id == session_id, "game_id"].unique())
        game_count = len(game_ids)
        return game_count
    
    def _calc_perc_games_won(self, game_id):
        try:
            session_id = self._df.loc[self._df.game_id == game_id, "session_id"].iloc[0]
            subset_df = self._df[(self._df.session_id == session_id) &
                                 (self._df.game_id <= game_id) &
                                 (self._df.outcome_type.isin(["win", "lose"]))]
            
            games_played = len(subset_df.game_id.unique())
            games_won = len(subset_df[subset_df.won == 1].game_id.unique())
            
            if games_played:
                percent_games_won = games_won / games_played
                
                return percent_games_won
        
        except IndexError:
            return



class GamesWonDF(Dataframe):
    """
    The GamesWonDF class inherits from Dataframe.  It is for instances when a game was won.  It is a subset
    of the dataframe from the GamesFinishedDF class.
    """
    
    def __init__(self, db, base_df, cols=None):
        super().__init__(db, base_df, cols)
        self._format_df()
    
    def _create_df(self):
        games_won = self._creator.create_df_from_subset(self._base_df, self._base_df["outcome_type_id"] == 1)
        
        return games_won
    
    def _format_df(self):
        self._df = self._formatter.format_df(self._df, "drop null", "score")
        self._df = self._formatter.add_col(self._df, "guess_time_ratio", self._df.game_id.apply(self._calc_guess_time_ratio),
                                         insert=True, index=35)
    
    def _calc_guess_time_ratio(self, game_id):
        """This method takes a game_id, calculates the guess_time_ratio (the ratio of the longest time before a 
        guess to the shortest time before a guess), and returns the ratio."""
    
        game_results = self._df[self._df.game_id == game_id]
        guess_ids = list(game_results.guess_id.sort_values())
        times_before_guess = []
        
        for guess_id in guess_ids:
            guess_time = game_results.loc[game_results.guess_id == guess_id, "guess_entry_time"]
            
            if not times_before_guess:
                time = guess_time - game_results.game_start_time.iloc[0]
            else:
                previous_guess_time = game_results.loc[game_results.guess_id == guess_id - 1, 
                                                       "guess_entry_time"].iloc[0]
                time = guess_time - previous_guess_time
            
            time = time.dt.total_seconds()
            time = time.iat[0]
            times_before_guess.append(time)
        
        guess_time_ratio = round(max(times_before_guess) / min(times_before_guess), 5)
        
        return guess_time_ratio