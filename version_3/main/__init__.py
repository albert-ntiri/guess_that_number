"""
Main Package: main

Description: The main package is the main package that contains all other files that are
    part of the application.  The main module, guess_that_number.py is part of this package.  This
    package has central files such as the database and the kv file, which lays out the design of the
    user interface.


Modules:
    guess_that_number.py

Sub Packages:
    game
    concepts
    app_data
    resources

Other Files:
    guess_that_number_design.kv
    sqlite_guess_that_number.db
    webscraping_for_definitions.py
    hint_descriptions.csv
"""


# Set directory with guess_that_number.py file as the main directory for the app.

import os.path
import sys

current_directory = os.path.dirname(os.path.abspath('guess_that_number.py'))
sys.path.append(current_directory)