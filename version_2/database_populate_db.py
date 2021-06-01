# -*- coding: utf-8 -*-
"""
Created on Wed May 26 15:11:48 2021

@author: alber
"""

import sqlite3
from application_text import AppText
import pandas as pd



# Connect to a database.
conn = sqlite3.connect('guess_that_number.db')

# Create a cursor.
c = conn.cursor()



# Use AppText object to pull values for type tables.

a = AppText()
app_text = a.application_text

hints = [x[1] for x in list(app_text['dynamic']['hint'])]

outcomes = [x[1] for x in list(app_text['dynamic']['outcome'])]


error_categories = [x[1] for x in list(app_text['dynamic']['error_message'])]

error_dfs = []
for index, category in enumerate(error_categories):
    page = list(app_text['dynamic']['error_message'])[index][0]
    errors = list(app_text['dynamic']['error_message'][(page, category)])
    errors_df = pd.DataFrame(pd.Series(errors), columns=['error_type'])
    errors_df.insert(0, 'category', category)
    error_dfs.append(errors_df)

errors = pd.concat(error_dfs, ignore_index=True)



# Populate type tables.

# Level of difficulty type table
for index, level in enumerate(['easy', 'medium', 'hard', 'custom'], start=1):
    c.execute("INSERT INTO level_of_difficulty_type VALUES (:id, :code, :description)",
                  {'id': index,
                    'code': level,
                    'description': level}
              )

# Hint type table
for index, hint in enumerate(hints, start=1):
    c.execute("INSERT INTO hint_type VALUES (:id, :code, :description)",
              {
                  'id': index,
                  'code': hint,
                  'description': hint
              }
              )

# Outcome type table
for index, outcome in enumerate(outcomes, start=1):
    c.execute("INSERT INTO outcome_type VALUES (:id, :code, :description)",
              {
                  'id': index,
                  'code': outcome,
                  'description': outcome
              }
              )

# Error type table
for index, row in errors.iterrows():
    c.execute("INSERT INTO error_type VALUES (:id, :category, :code, :description)",
                  {'id': index + 1,
                    'category': row['category'],
                    'code': row['error_type'],
                    'description': row['error_type']
                    }
              )



# Commit changes.
conn.commit()

# Close the connection.
conn.close()