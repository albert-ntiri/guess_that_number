# -*- coding: utf-8 -*-
"""
Created on Fri May 28 01:02:45 2021

@author: alber
"""

import sqlite3

class Session:
    db_name = 'guess_that_number.db'
    
    def __init__(self, game_obj):
        self.game_obj = game_obj
        
        self.add_session_record_to_db()
        self.session_id = self._get_session_id()
        
        self.game_ids = []
    
    def add_session_record_to_db(self):
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        c.execute("INSERT INTO session(time) VALUES (datetime('now', 'localtime'))")
        
        conn.commit()
        conn.close()
    
    def add_game_record_to_db(self, error=False, error_type=None):
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
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        outcome_id = c.execute("SELECT outcome_id FROM outcome WHERE game_id = " + str(self.game_ids[-1])).fetchone()[0]
        c.execute("UPDATE outcome SET play_again = 1 WHERE outcome_id = " + str(outcome_id))
        
        conn.commit()
        conn.close()
        
    def get_hint_list(self, number):
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
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        hint_description = c.execute("SELECT description FROM hint_type WHERE code = " + "'{}'".format(hint_type)).fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return hint_description
    
    def _get_session_id(self):
        conn = sqlite3.connect(Session.db_name)
        c = conn.cursor()
        
        session_id = c.execute("SELECT id FROM session ORDER BY time DESC LIMIT 1").fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return session_id