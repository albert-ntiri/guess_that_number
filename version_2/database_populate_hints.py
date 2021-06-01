# -*- coding: utf-8 -*-
"""
Created on Wed May 26 15:11:48 2021

@author: alber
"""

import sqlite3
import pandas as pd
from application_text import AppText
from hints import HintGenerator



# Connect to a database.
conn = sqlite3.connect('guess_that_number.db')

# Create a cursor.
c = conn.cursor()



# Update description column in hint type table in database with definitions from the web.

hint_descriptions = pd.read_csv("hint_descriptions.csv")

factor_def = hint_descriptions.loc[hint_descriptions.hint_type == "factor", "hint_description"].iloc[0]
multiple_def = hint_descriptions.loc[hint_descriptions.hint_type == "multiple", "hint_description"].iloc[0]
prime_def = hint_descriptions.loc[hint_descriptions.hint_type == "prime", "hint_description"].iloc[0]
even_odd_def = hint_descriptions.loc[hint_descriptions.hint_type == "even_odd", "hint_description"].iloc[0]
perfect_square_def = hint_descriptions.loc[hint_descriptions.hint_type == "perfect_square", "hint_description"].iloc[0]
digit_sum_def = hint_descriptions.loc[hint_descriptions.hint_type == "digit_sum", "hint_description"].iloc[0]
digit_length_def = hint_descriptions.loc[hint_descriptions.hint_type == "digit_length", "hint_description"].iloc[0]

# Factor - id = 1
c.execute("UPDATE hint_type SET description = " + "'{}'".format(factor_def) + "WHERE id = 1")

# Multiple - id = 2
c.execute("UPDATE hint_type SET description = " + "'{}'".format(multiple_def) + "WHERE id = 2")

# Prime - id = 3
c.execute("UPDATE hint_type SET description = " + "'{}'".format(prime_def) + "WHERE id = 3")

# Even Odd - id = 4
c.execute("UPDATE hint_type SET description = " + "'{}'".format(even_odd_def) + "WHERE id = 4")

# Perfect Square - id = 5
c.execute("UPDATE hint_type SET description = " + "'{}'".format(perfect_square_def) + "WHERE id = 5")

# Digit Sum - id = 6
c.execute("UPDATE hint_type SET description = " + "'{}'".format(digit_sum_def) + "WHERE id = 6")

# Digit Length - id = 7
c.execute("UPDATE hint_type SET description = " + "'{}'".format(digit_length_def) + "WHERE id = 7")



# Hint table
a = AppText()

for i in range(1, 101):
    hint_obj = HintGenerator(i)
    hints = hint_obj.generate_hints(check_db=False, filter_results=False)
    for hint in hints:
        hint_type = a.get_hint_type(hint)
        hint_type_id = c.execute("SELECT id FROM hint_type WHERE code = " + "'{}'".format(hint_type)).fetchone()[0]
        c.execute("INSERT INTO hint(hint_type_id, number, hint) VALUES (:hint_type_id, :number, :hint)",
                      {
                          'hint_type_id': int(hint_type_id),
                          'number': int(i),
                          'hint': hint
                      }
                  )



# Commit changes.
conn.commit()

# Close the connection.
conn.close()