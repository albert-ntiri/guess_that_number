import sqlite3

conn = sqlite3.connect('sqlite_guess_that_number.db')
c = conn.cursor()



# # Session table.
# sessions = c.execute("SELECT * FROM session").fetchall()
# session_cols = tuple([x[0] for x in c.description])
# print("Sessions\n")
# print(session_cols)
# for session in sessions:
#     print(session)

# # Game table.
# games = c.execute("SELECT * FROM game").fetchall()
# game_cols = tuple([x[0] for x in c.description])
# print("Games\n")
# print(game_cols)
# for game in games:
#     print(game)

# # Guess table.
# guesses = c.execute("SELECT * FROM guess").fetchall()
# guess_cols = tuple([x[0] for x in c.description])
# print("Guesses\n")
# print(guess_cols)
# for guess in guesses:
#     print(guess)

# # Outcome table.
# outcomes = c.execute("SELECT * FROM outcome").fetchall()
# outcome_cols = tuple([x[0] for x in c.description])
# print("Outcomes\n")
# print(outcome_cols)
# for outcome in outcomes:
#     print(outcome)


# # Data for most recent session
# last_session = c.execute("""SELECT *
#                             FROM session s
#                                 LEFT JOIN game gm ON s.id = gm.session_id
#                                 LEFT JOIN guess gs ON gm.game_id = gs.game_id
#                                 LEFT JOIN outcome o ON gm.game_id = o.game_id
#                             WHERE s.id = (SELECT MAX(id) FROM session)
#                             ORDER BY gm.game_id, gs.guess_id
#                             """).fetchall()
# last_session_cols = tuple([x[0] for x in c.description])
# print("Last Session\n")
# print(last_session_cols)
# for session in last_session:
#     print(session)


# # Custom
# guesses = c.execute("SELECT time FROM guess WHERE game_id = 2").fetchall()
# for guess in guesses:
#     print(guess)



conn.commit()
conn.close()