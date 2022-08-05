"""
The dataframe_vars.py module is part of the variables package.  It lists the set of queries and column lists
used in the dataframes.py module to pull historical data from the app for modeling purposes.

Variables:
    happy_path_query
    range_error_query
    guess_error_query
    game_data_cols
    range_error_cols
    guess_error_cols
"""


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
    gs.feedback,
    gs.error guess_error,
    o.outcome_id,
    o.outcome_type_id,
    ot.code outcome_type,
    o.score,
    o.feedback_type,
    o.improvement_area_id,
    o.recommendation_type,
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
    "feedback",
    "guess_error",
    "outcome_id",
    "outcome_type_id",
    "outcome_type",
    "score",
    "feedback_type",
    "improvement_area_id",
    "recommendation_type",
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

