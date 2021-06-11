import sqlite3
import pandas as pd
from datetime import datetime, timedelta

from sklearn import linear_model

from model import Model



class AppData:
    """
    The AppData class contains information about all previous data from the application.  It pulls data 
    from the database and uses it to make predictions for live users.
    
    Attributes:
        game_data: A dataframe containing all historical data from the application.
        range_error_data: A dataframe containing all the errors made when entering custom ranges.
        guess_error_data: A dataframe containing all the errors made when entering guesses.
        no_games: A subset of game_data with all the sessions where no game was initiated.
        range_errors: A subset of game_data with games initiated but errors in the custom range entry.
        games_started: A subset of game_data with games initiated and no custom range errors.
        games_summary: A dataframe with summary data from guesses and hints from each game started.
        games_not_finished: A subset of games_started with games initiated but no outcome.
        games_finished: A subset of games_started with games initiated and an outcome.
        games_won: A subset of games_finished with games that have an outcome_type_id of 1 (win).
    
    Class Attributes:
        db_name: The name of the database storing data from the app.
        happy_path_query: The query to pull data for the game_data dataframe.
        range_error_query: The query to pull data for the range_error_data dataframe.
        guess_error_query: The query to pull data for the guess_error_data dataframe.
        game_data_cols: The list of columns for the game_data dataframe.
        range_error_cols: The list of columns for the range_error_data dataframe.
        guess_error_cols: The list of columns for the guess_error_data dataframe.
        score_pred_features: The list of features for the regression model predicting the score of a game.
        outcome_pred_features: The list of features for the classification model predicting the outcome of a game.
    """
    
    db_name = 'guess_that_number.db'
    
    happy_path_query = """
    SELECT
        s.id session_id,
        s.time app_start_time,
        gm.game_id,
        gm.level_of_difficulty_type_id,
        l.code level_of_difficulty_type,
        gm.range_low low_range,
        gm.range_high high_range,
        gm.winning_number,
        gm.time game_start_time,
        gm.error range_error,
        gs.guess_id,
        gs.hint_type_id,
        h.code hint_type,
        gs.hint,
        gs.hint_number,
        gs.time guess_entry_time,
        gs.guess,
        gs.error guess_error,
        o.outcome_id,
        o.outcome_type_id,
        ot.code outcome_type,
        o.score,
        o.time game_end_time,
        o.play_again
    FROM session s
        LEFT JOIN game gm ON s.id = gm.session_id
        LEFT JOIN guess gs ON gm.game_id = gs.game_id
        LEFT JOIN outcome o ON gm.game_id = o.game_id
        LEFT JOIN level_of_difficulty_type l ON gm.level_of_difficulty_type_id = l.id
        LEFT JOIN hint_type h ON gs.hint_type_id = h.id
        LEFT JOIN outcome_type ot ON o.outcome_type_id = ot.id
    ORDER BY session_id, gm.game_id, gs.guess_id
    """
    
    range_error_query = """
    SELECT
        s.id session_id,
        s.time app_start_time,
        gm.game_id,
        gm.time game_start_time,
        gm.error_type_id,
        e.code range_error_type
    FROM session s
        LEFT JOIN game gm ON s.id = gm.session_id
        JOIN error_type e ON gm.error_type_id = e.id
    WHERE gm.error = 1
    """
    
    guess_error_query = """
    SELECT
        s.id session_id,
        s.time app_start_time,
        gm.game_id,
        gm.level_of_difficulty_type_id,
        l.code level_of_difficulty_type,
        gm.range_low low_range,
        gm.range_high high_range,
        gm.winning_number,
        gm.time game_start_time,
        gs.guess_id,
        gs.time guess_entry_time,
        gs.guess,
        gs.error_type_id,
        e.code guess_error_type
    FROM session s
        LEFT JOIN game gm ON s.id = gm.session_id
        LEFT JOIN guess gs ON gm.game_id = gs.game_id
        LEFT JOIN level_of_difficulty_type l ON gm.level_of_difficulty_type_id = l.id
        JOIN error_type e ON gs.error_type_id = e.id
    WHERE gs.error = 1
    """
    
    game_data_cols = [
        "session_id",
        "app_start_time",
        "game_id",
        "level_of_difficulty_type_id",
        "level_of_difficulty_type",
        "low_range",
        "high_range",
        "winning_number",
        "game_start_time",
        "range_error",
        "guess_id",
        "hint_type_id",
        "hint_type",
        "hint",
        "hint_number",
        "guess_entry_time",
        "guess",
        "guess_error",
        "outcome_id",
        "outcome_type_id",
        "outcome_type",
        "score",
        "game_end_time",
        "play_again"
    ]
    
    range_error_cols = [
        "session_id",
        "app_start_time",
        "game_id",
        "game_start_time",
        "range_error_type_id",
        "range_error_type"
    ]
    
    guess_error_cols = [
        "session_id",
        "app_start_time",
        "game_id",
        "level_of_difficulty_type_id",
        "level_of_difficulty_type",
        "low_range",
        "high_range",
        "winning_number",
        "game_start_time",
        "guess_id",
        "guess_entry_time",
        "guess",
        "guess_error_type_id",
        "guess_error_type"
    ]
    
    score_pred_features = [
        "range_size",
        "total_hints",
        "total_duration",
        "guess_time_ratio"
    ]
    
    outcome_pred_features = [x for x in score_pred_features if x != "guess_time_ratio"]
    
    def __init__(self):
        """The constructor method for this class queries the database for all historical data from the 
        application and stores it in a dataframe.  It also splits the main dataframe, game_data, into 
        a few subset dataframes, capturing specific types of information: no_games, range_errors, 
        games_not_finished, games_finished, and games_won."""
        
        
        # Query database for all data from previous games.
        
        conn = sqlite3.connect(AppData.db_name)
        c = conn.cursor()
        
        game_data_results = c.execute(AppData.happy_path_query).fetchall()
        range_error_data_results = c.execute(AppData.range_error_query).fetchall()
        guess_error_data_results = c.execute(AppData.guess_error_query).fetchall()
        
        conn.commit()
        conn.close()
        
        
        
        # Put query results into dataframes.
        
        self.game_data = pd.DataFrame(game_data_results, columns=AppData.game_data_cols)
        self.range_error_data = pd.DataFrame(range_error_data_results, columns=AppData.range_error_cols)
        self.guess_error_data = pd.DataFrame(guess_error_data_results, columns=AppData.guess_error_cols)
        
        
        
        # Pull info from range_error_data and guess_error_data into main game_data dataframe.
        
        self.game_data.insert(10, "range_error_type_id", self.game_data.game_id.map(
            self.range_error_data.set_index("game_id").range_error_type_id))
        self.game_data.insert(11, "range_error_type", self.game_data.game_id.map(
            self.range_error_data.set_index("game_id").range_error_type))
        self.game_data.insert(19, "guess_error_type_id", self.game_data.game_id.map(
            self.guess_error_data.set_index("guess_id").guess_error_type_id))
        self.game_data.insert(20, "guess_error_type", self.game_data.game_id.map(
            self.guess_error_data.set_index("guess_id").guess_error_type))
        
        
        
        # Convert time columns into datetime format.
        
        datetime_cols = ["app_start_time", "game_start_time", "guess_entry_time", "game_end_time"]
        for col in datetime_cols:
            self.game_data[col] = pd.to_datetime(self.game_data[col])
        
        
        
        # Split game_data into no_games (app opened but no game played) and games.
        
        self.no_games = self.game_data[self.game_data.game_id.isna()].copy()
        games = self.game_data[self.game_data.game_id.notna()].copy()
        
        
        
        # Split games into range_errors (game not started b/c of invalid range entry) and 
        # games_started.  Convert low_range and high_range columns to integers and calculate
        # range_size from them.
        
        self.range_errors = games[games.range_error == 1].copy()
        
        self.games_started = games[games.range_error == 0].copy()
        self.games_started["low_range"] = self.games_started.low_range.astype("int")
        self.games_started["high_range"] = self.games_started.high_range.astype("int")
        self.games_started.insert(7, "range_size", 
                                  self.games_started.high_range - self.games_started.low_range + 1)
        
        
        
        # Create games_summary dataframe with aggregate data from the guesses and hints for each game.
        
        self.games_summary = self.games_started.pivot_table(index="game_id", values="guess_id", aggfunc=len)
        self.games_summary.rename(columns={"guess_id": "total_guesses"}, inplace=True)
        self.games_summary["total_hints"] = self.games_summary.index.map(
            self.games_started.pivot_table(index="game_id", values="hint_number", aggfunc=max).hint_number)
        self.games_summary["guess_errors"] = self.games_summary.index.map(
            self.games_started.pivot_table(index="game_id", values="guess_error", aggfunc=sum).guess_error)
        
        
        
        # Add aggregate data from games_summary into games_started.
        
        self.games_started.insert(10, "total_guesses", self.games_started.game_id.map(
            self.games_summary.total_guesses))
        self.games_started.insert(11, "total_hints", self.games_started.game_id.map(
            self.games_summary.total_hints))
        self.games_started.insert(12, "total_guess_errors", self.games_started.game_id.map(
            self.games_summary.guess_errors))
        
        
        
        # Split games_started into games_not_finished (started but no outcome) and games_finished.
        # Derive total_duration and won columns from games_finished.
        
        self.games_not_finished = self.games_started[self.games_started.outcome_id.isna()].copy()
        
        self.games_finished = self.games_started[self.games_started.outcome_id.notna()].copy()
        self.games_finished.insert(30, "total_duration", 
                                   self.games_finished.game_end_time - self.games_finished.game_start_time)
        self.games_finished["total_duration"] = self.games_finished.total_duration.dt.total_seconds()
        self.games_finished = self.games_finished[self.games_finished.guess_id.notna()].copy()
        self.games_finished.total_hints.fillna(0, inplace=True)
        self.games_finished.insert(32, "won", self.games_finished.game_id.apply(self._calc_won))
        
        
        
        # Create games_won from games_finished (games with an outcome_type_id of 1).  Derive 
        # guess_time_ratio column from games_won.
        
        self.games_won = self.games_finished[self.games_finished.outcome_type_id == 1].copy()
        self.games_won = self.games_won[self.games_won.score.notna()].copy()
        self.games_won.insert(31, "guess_time_ratio", self.games_won.game_id.apply(self._calc_guess_time_ratio))
    
    
    
    def predict_score(self, game_id):
        """This method runs a regression model to predict the score of the game based on the game_id that is 
        passed in, and returns the predicted score."""
        
        lreg = linear_model.LinearRegression()
        comp_df = pd.DataFrame(columns=["Training R2", "Test R2", "Test RMSE", "Cross Validation Score"])
        score_predict_model = Model(lreg, self.games_won, AppData.score_pred_features, 
                                    "score", "Regression", "Linear Reg - Score")
        score_predict_model.build_model(comp_df)
        
        game_info = self._calc_game_info(game_id, "score")
        predicted_score = score_predict_model.predict([game_info])[0]
        predicted_score = round(predicted_score)
        
        return predicted_score
    
    def predict_outcome(self, game_id):
        """This method runs a classification model to predict the outcome of the game based on the game_id that is 
        passed in, and returns the predicted outcome."""
        
        log_reg = linear_model.LogisticRegression(C=1)
        comp_df = pd.DataFrame(columns=["Training Accuracy", "Test Accuracy", "Test Precision", "Test Recall"])
        outcome_predict_model = Model(log_reg, self.games_finished, AppData.outcome_pred_features, 
                                    "won", "Classification", "Logistic Reg - Outcome")
        outcome_predict_model.build_model(comp_df)
        
        game_info = self._calc_game_info(game_id, "outcome")
        predicted_outcome = outcome_predict_model.predict([game_info])[0]
        predicted_outcome = "win" if predicted_outcome == 1 else "lose"
        
        return predicted_outcome
    
    def _calc_game_info(self, game_id, pred_type):
        """This method takes in a game_id and prediction type and returns a list of values for the features of the 
        appropriate model, based on the prediction type."""
        
        conn = sqlite3.connect(AppData.db_name)
        c = conn.cursor()
        
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
        
        game_start_time, game_end_time, high_range, low_range, total_hints = c.execute(game_info_query).fetchall()[0]
        
        range_size = int(high_range) - int(low_range) + 1
        total_hints = int(total_hints) if total_hints else 0
        date_format = "%Y-%m-%d %H:%M:%S"
        game_start_time = datetime.strptime(game_start_time, date_format) # '2021-06-10 02:17:36'
        game_end_time = datetime.strptime(game_end_time, date_format)
        total_duration = (game_end_time - game_start_time).total_seconds()
        
        game_info = [range_size, total_hints, total_duration]
        
        if pred_type == "score":
            guess_time_query = "SELECT time FROM guess WHERE game_id = " + str(game_id)
            guess_times = c.execute(guess_time_query).fetchall()
            guess_times = [datetime.strptime(x[0], date_format) for x in guess_times]
            guess_durations = [guess_times[0] - game_start_time] + [guess_times[i+1] - guess_times[i] for i in range(len(guess_times) - 1)]
            guess_durations = [x.total_seconds() for x in guess_durations]
            
            guess_time_ratio = round(max(guess_durations) / min(guess_durations), 2)
            game_info.append(guess_time_ratio)
        
        conn.commit()
        conn.close()
        
        return game_info
    
    def _calc_guess_time_ratio(self, game_id):
        """This method takes a game_id, calculates the guess_time_ratio (the ratio of the longest time before a 
        guess to the shortest time before a guess), and returns the ratio."""
    
        game_results = self.games_won[self.games_won.game_id == game_id]
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
        
        guess_time_ratio = round(max(times_before_guess) / min(times_before_guess), 2)
        
        return guess_time_ratio
    
    def _calc_won(self, game_id):
        """This method takes in a game_id and returns an indicator of whether the user won the game."""
        
        game_results = self.games_finished[self.games_finished.game_id == game_id]
        outcome = game_results.outcome_type_id.unique()[0]
        won = 1 if outcome == 1 else 0
        return won