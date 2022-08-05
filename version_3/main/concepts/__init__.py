"""
Package: concepts

Description: The concepts package contains all the modules relating to generating hints and evaluating
    guesses based on the winning number for a game.  It is broken up into different math concepts, each of
    which contains logic to create hints and check guesses based on characteristics of the number relating to
    that concept.
    
    The types of hints include the following:
        main hints: a general characteristic about the number related to the concept,
        factor hints: the number of factors of the number that fit a characteristic related to the concept,
        digit hints: the number of digits of the number that fit a characteristic related to the concept.
    
    Many of the concepts also contain logic to determine when hints for that concept will be created, allowing
    for customization based on relevancy and helpfulness of the hints for each concept based on the winning
    number.


Modules:
    concept_manager.py
    factor.py
    multiple.py
    prime.py
    even_odd.py
    perfect_exponents.py
    digit_concepts.py
    math_concept.py
    hints.py
"""