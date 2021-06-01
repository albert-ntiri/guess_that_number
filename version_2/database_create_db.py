# -*- coding: utf-8 -*-
"""
Created on Sun May 23 13:12:30 2021

@author: alber
"""

# Import libraries.
import sqlite3



# Connect to a database.
conn = sqlite3.connect('guess_that_number.db')

# Create a cursor.
c = conn.cursor()



# Create tables.

# Level of difficulty type table
c.execute("""CREATE TABLE level_of_difficulty_type (
                id INTEGER NOT NULL PRIMARY KEY,
                code TEXT NOT NULL,
                description TEXT
                )""")

# Hint type table
c.execute("""CREATE TABLE hint_type (
                id INTEGER NOT NULL PRIMARY KEY,
                code TEXT NOT NULL,
                description TEXT
                )""")

# Outcome type table
c.execute("""CREATE TABLE outcome_type (
                id INTEGER NOT NULL PRIMARY KEY,
                code TEXT NOT NULL,
                description TEXT
                )""")

# Error type table
c.execute("""CREATE TABLE error_type (
                id INTEGER NOT NULL PRIMARY KEY,
                category TEXT NOT NULL,
                code TEXT NOT NULL,
                description TEXT
                )""")

# Hint table
c.execute("""CREATE TABLE hint (
                hint_id INTEGER NOT NULL PRIMARY KEY,
                hint_type_id INTEGER,
                number INTEGER,
                hint TEXT,
                FOREIGN KEY (hint_type_id) REFERENCES hint_type (id)
                )""")

# Session table
c.execute("""CREATE TABLE session (
                id INTEGER NOT NULL PRIMARY KEY,
                time TEXT NOT NULL
                )""")

# Game table
c.execute("""CREATE TABLE game (
                game_id INTEGER NOT NULL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                level_of_difficulty_type_id INTEGER,
                range_low TEXT,
                range_high TEXT,
                winning_number INTEGER,
                time TEXT,
                error INTEGER NOT NULL,
                error_type_id INTEGER,
                FOREIGN KEY (session_id) REFERENCES session (id),
                FOREIGN KEY (level_of_difficulty_type_id) REFERENCES level_of_difficulty_type (id),
                FOREIGN KEY (error_type_id) REFERENCES error_type (id)
                )""")

# Guess table
c.execute("""CREATE TABLE guess (
                guess_id INTEGER NOT NULL PRIMARY KEY,
                game_id INTEGER NOT NULL,
                session_id INTEGER NOT NULL,
                hint_type_id INTEGER,
                hint TEXT,
                hint_number INTEGER,
                time TEXT,
                guess TEXT,
                error INTEGER,
                error_type_id INTEGER,
                FOREIGN KEY (game_id) REFERENCES game (game_id),
                FOREIGN KEY (session_id) REFERENCES session (session_id),
                FOREIGN KEY (hint_type_id) REFERENCES hint_type (id),
                FOREIGN KEY (error_type_id) REFERENCES error_type (id)
                )""")

# Outcome table
c.execute("""CREATE TABLE outcome (
                outcome_id INTEGER NOT NULL PRIMARY KEY,
                game_id INTEGER NOT NULL,
                session_id INTEGER NOT NULL,
                outcome_type_id INTEGER NOT NULL,
                score INTEGER,
                time TEXT,
                play_again INTEGER NOT NULL,
                FOREIGN KEY (game_id) REFERENCES game (game_id),
                FOREIGN KEY (session_id) REFERENCES session (session_id),
                FOREIGN KEY (outcome_type_id) REFERENCES outcome_type (id)
                )""")



# Commit changes.
conn.commit()

# Close the connection.
conn.close()