"""
The create_db_queries.py module is part of the variables package.  It lists the set of queries that creates
the database for the app.  It also has a variable that collects these query variables in one group for easy
access.

Variables:
    create_level_of_difficulty_type_table
    create_hint_type_table
    create_outcome_type_table
    create_error_type_table
    create_hint_table
    create_session_table
    create_game_table
    create_guess_table
    create_outcome_table
    create_table_queries
"""


create_level_of_difficulty_type_table = """
        CREATE TABLE level_of_difficulty_type (
            id INTEGER NOT NULL PRIMARY KEY,
            code TEXT NOT NULL,
            description TEXT
        );"""

create_hint_type_table = """
        CREATE TABLE hint_type (
            id INTEGER NOT NULL PRIMARY KEY,
            code TEXT NOT NULL,
            description TEXT
        );"""

create_outcome_type_table = """
        CREATE TABLE outcome_type (
            id INTEGER NOT NULL PRIMARY KEY,
            code TEXT NOT NULL,
            description TEXT
        );"""

create_error_type_table = """
        CREATE TABLE error_type (
            id INTEGER NOT NULL PRIMARY KEY,
            category TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT
        );"""

create_hint_table = """
        CREATE TABLE hint (
            hint_id INTEGER NOT NULL PRIMARY KEY,
            hint_type_id INTEGER,
            number INTEGER,
            hint TEXT,
            FOREIGN KEY (hint_type_id) REFERENCES hint_type (id)
        );"""

create_session_table = """
        CREATE TABLE session (
            id INTEGER NOT NULL PRIMARY KEY,
            time TEXT NOT NULL
        );"""

create_game_table = """
        CREATE TABLE game (
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
        );"""

create_guess_table = """
        CREATE TABLE guess (
            guess_id INTEGER NOT NULL PRIMARY KEY,
            game_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            hint_type_id INTEGER,
            hint TEXT,
            hint_number INTEGER,
            time TEXT,
            guess TEXT,
            feedback TEXT,
            error INTEGER,
            error_type_id INTEGER,
            FOREIGN KEY (game_id) REFERENCES game (game_id),
            FOREIGN KEY (session_id) REFERENCES session (id),
            FOREIGN KEY (hint_type_id) REFERENCES hint_type (id),
            FOREIGN KEY (error_type_id) REFERENCES error_type (id)
        );"""

create_outcome_table = """
        CREATE TABLE outcome (
            outcome_id INTEGER NOT NULL PRIMARY KEY,
            game_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            outcome_type_id INTEGER NOT NULL,
            score INTEGER,
            feedback_type TEXT,
            improvement_area_id INTEGER,
            recommendation_type TEXT,
            time TEXT,
            play_again INTEGER NOT NULL,
            FOREIGN KEY (game_id) REFERENCES game (game_id),
            FOREIGN KEY (session_id) REFERENCES session (id),
            FOREIGN KEY (outcome_type_id) REFERENCES outcome_type (id),
            FOREIGN KEY (improvement_area_id) REFERENCES hint_type (id)
        );"""

create_table_queries = [
    ("level_of_difficulty_type", create_level_of_difficulty_type_table),
    ("hint_type", create_hint_type_table),
    ("outcome_type", create_outcome_type_table),
    ("error_type", create_error_type_table),
    ("hint", create_hint_table),
    ("session", create_session_table),
    ("game", create_game_table),
    ("guess", create_guess_table),
    ("outcome", create_outcome_table)
]

db_tables = [row[0] for row in create_table_queries]
type_tables = [table for table in db_tables if "type" in table]
non_type_tables = [table for table in db_tables if table not in type_tables and table != "hint"]
