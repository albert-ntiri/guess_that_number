import sqlite3



class Session:
    """
    The Session class captures information about a live session of a user, including information about the 
    games played, guesses, hints, and outcome.  It enters this information into the database during the 
    session.  It also contains helper methods to query the database for specific information as needed.
    
    Attributes:
        game_obj: An object of the GuessThatNumberGame class.
        session_id: A unique identifier for a session (user opening and using the app).
        game_ids: A list of ids representing each game the user plays during a session.
        app_data: An object of the AppData class.
    
    Class Attributes:
        db_name: The name of the database storing data from the app.
    """
    
    db_name = 'guess_that_number.db'
    
    def __init__(self, game_obj):
        """The constructor method for this class takes in a game object and saves it as an attribute.  It 
        also creates a session, adds it to the session table in the database, saves the session_id as an 
        attribute and instantiates an AppData object."""
        
        self.game_obj = game_obj
        
        self.add_session_record_to_db()
        self.session_id = self._get_session_id()
        
        self.game_ids = []
    
    def add_session_record_to_db(self):
        """This method adds a new record to the session table in the database when the app is opened."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        c.execute("INSERT INTO session(time) VALUES (datetime('now', 'localtime'))")
        
        conn.commit()
        conn.close()
    
    def add_game_record_to_db(self, error=False, error_type=None):
        """This method adds a new record to the game table in the database when a new game is started.  
        If error is True, it adds the error_type_id corresponding to the error_type that is passed in 
        and leaves the range, level of difficulty and winning number blank."""
        
        if error:
            conn = sqlite3.connect(Session.db_name)
            c = conn.cursor()
            
            error_type_id = c.execute("SELECT id FROM error_type WHERE code = " + "'{}'".format(error_type)).fetchone()[0]
            
            c.execute("""INSERT INTO game(
                session_id,
                time,
                error,
                error_type_id
                )
            VALUES (
                :session_id,
                datetime('now', 'localtime'),
                :error,
                :error_type_id
                )""",
            {
                'session_id': int(self.session_id),
                'error': 1,
                'error_type_id': int(error_type_id)
                }
            )
    
            game_id = c.execute("""SELECT game_id 
                                   FROM game 
                                   WHERE session_id = """ + str(self.session_id) + """ 
                                   ORDER BY time DESC 
                                   LIMIT 1""").fetchone()[0]
            self.game_ids.append(game_id)
            
            conn.commit()
            conn.close()
            
        else:
            conn = sqlite3.connect(Session.db_name)
            c = conn.cursor()
            
            c.execute("""INSERT INTO game(
                session_id,
                level_of_difficulty_type_id,
                range_low,
                range_high,
                winning_number,
                time,
                error
                ) 
            VALUES (
                :session_id,
                :level_of_difficulty_type_id,
                :range_low,
                :range_high,
                :winning_number,
                datetime('now', 'localtime'),
                :error
                )""",
            {
                'session_id': int(self.session_id),
                'level_of_difficulty_type_id': int(self.game_obj.level_of_difficulty),
                'range_low': int(self.game_obj.number_range[0]),
                'range_high': int(self.game_obj.number_range[1]),
                'winning_number': int(self.game_obj.winning_number),
                'error': 0
                }
            )
            
            game_id = c.execute("""SELECT game_id 
                                   FROM game 
                                   WHERE session_id = """ + str(self.session_id) + """ 
                                   ORDER BY time DESC 
                                   LIMIT 1""").fetchone()[0]
            self.game_ids.append(game_id)
            
            conn.commit()
            conn.close()

    def add_guess_record_to_db(self, guess, hint=None, error=False, error_type=None):
        """This method adds a record to the guess table in the database when a new guess is entered by 
        the user.  If there is no hint, it omits those columns.  If error is True, it adds the error_type_id 
        corresponding to the error_type that is passed in and leaves the hint information blank."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        if error:
            error_type_id = c.execute("SELECT id FROM error_type WHERE code = " + "'{}'".format(error_type)).fetchone()[0]
            
            c.execute("""INSERT INTO guess(
                game_id,
                session_id,
                time,
                guess,
                error,
                error_type_id
                ) 
            VALUES (
                :game_id,
                :session_id,
                datetime('now', 'localtime'),
                :guess,
                :error,
                :error_type_id
                )""",
            {
                'game_id': int(self.game_ids[-1]),
                'session_id': int(self.session_id),
                'guess': guess,
                'error': 1,
                'error_type_id': int(error_type_id)
                }
            )
    
        elif not hint:
            c.execute("""INSERT INTO guess(
                game_id,
                session_id,
                time,
                guess,
                error
                ) 
            VALUES (
                :game_id,
                :session_id,
                datetime('now', 'localtime'),
                :guess,
                :error
                )""",
            {
                'game_id': int(self.game_ids[-1]),
                'session_id': int(self.session_id),
                'guess': guess,
                'error': 0
                }
            )
            
        else:
            hint_number = self.get_total_hints_given()
            hint_number = 1 if not hint_number else hint_number[0] + 1
            hint_type = self.game_obj.app_text.get_hint_type(hint)
            hint_type_id = c.execute("SELECT id FROM hint_type WHERE code = " + "'{}'".format(hint_type)).fetchone()[0]
            hint = hint if hint else None
            
            c.execute("""INSERT INTO guess(
                game_id,
                session_id,
                hint_type_id,
                hint,
                hint_number,
                time,
                guess,
                error
                ) 
            VALUES (
                :game_id,
                :session_id,
                :hint_type_id,
                :hint,
                :hint_number,
                datetime('now', 'localtime'),
                :guess,
                :error
                )""",
            {
                'game_id': int(self.game_ids[-1]),
                'session_id': int(self.session_id),
                'hint_type_id': int(hint_type_id),
                'hint': hint,
                'hint_number': int(hint_number),
                'guess': guess,
                'error': 0
                }
            )
            
        conn.commit()
        conn.close()
    
    def add_outcome_record_to_db(self, outcome, score=None):
        """This method adds a record to the outcome table in the database when a game is concluded."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        outcome_type_id = c.execute("SELECT id FROM outcome_type WHERE code = " + "'{}'".format(outcome)).fetchone()[0]
        score = score if score else None
        
        c.execute("""INSERT INTO outcome(
            game_id,
            session_id,
            outcome_type_id,
            score,
            time,
            play_again
            ) 
        VALUES (
            :game_id,
            :session_id,
            :outcome_type_id,
            :score,
            datetime('now', 'localtime'),
            :play_again
            )""",
        {
            'game_id': int(self.game_ids[-1]),
            'session_id': int(self.session_id),
            'outcome_type_id': int(outcome_type_id),
            'score': score,
            'play_again': 0
            }
        )
        
        conn.commit()
        conn.close()
    
    def update_outcome_record_in_db(self):
        """This method takes the outcome record for the most recent game and updates play_again to 1 when 
        the user clicks on the play again button."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        outcome_id = c.execute("SELECT outcome_id FROM outcome WHERE game_id = " + str(self.game_ids[-1])).fetchone()[0]
        c.execute("UPDATE outcome SET play_again = 1 WHERE outcome_id = " + str(outcome_id))
        
        conn.commit()
        conn.close()
    
    def get_hint_list(self, number):
        """This method takes the number that is passed in, queries the hint table for its corresponding 
        hints and returns those hints."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        hints = c.execute("""SELECT t.code, h.hint 
                             FROM hint h
                                 JOIN hint_type t ON h.hint_type_id = t.id
                             WHERE h.number = """ + str(number)).fetchall()
        
        conn.commit()
        conn.close()
        
        return hints
    
    def get_total_hints_given(self):
        """This method returns the number of hints that were given for the most recent game of a session."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        total_hints_given = c.execute("""SELECT COUNT(hint) 
                                         FROM guess 
                                         WHERE game_id = """ + str(self.game_ids[-1]) + """ 
                                         AND hint IS NOT NULL""").fetchone()
        
        conn.commit()
        conn.close()
        
        return total_hints_given
    
    def get_last_hint(self):
        """This method returns the last hint and hint type that was given for the most recent game of a 
        session."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        hint_type, hint = c.execute("""SELECT t.code, g.hint 
                                       FROM guess g
                                           JOIN hint_type t ON g.hint_type_id = t.id
                                       WHERE g.game_id = """ + str(self.game_ids[-1]) + """ 
                                       ORDER BY g.time DESC LIMIT 1""").fetchone()
        
        conn.commit()
        conn.close()
        
        return hint_type, hint
        
    def get_hint_description(self, hint_type):
        """This method takes the hint type that is passed in and returns its corresponding description."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        hint_description = c.execute("SELECT description FROM hint_type WHERE code = " + "'{}'".format(hint_type)).fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return hint_description
    
    def _get_next_level_of_difficulty(self):
        """This method returns the level of difficulty that is one level higher than that of the most recent 
        game.  If the most recent level is the highest, it returns that same level."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        level_of_difficulty_type_id = c.execute("""SELECT level_of_difficulty_type_id
                                                   FROM game
                                                   WHERE game_id = """ + str(self.game_ids[-1])).fetchone()[0]
        
        next_level_of_difficulty_type_id = int(level_of_difficulty_type_id) + 1 if level_of_difficulty_type_id < 4 else 4
        
        next_level_of_difficulty = c.execute("""SELECT code
                                                FROM level_of_difficulty_type
                                                WHERE id = """ + str(next_level_of_difficulty_type_id)).fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return next_level_of_difficulty
    
    def _get_session_id(self):
        """This method returns the most recent session_id from the session table."""
        
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        session_id = c.execute("SELECT id FROM session ORDER BY time DESC LIMIT 1").fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return session_id