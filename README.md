# Guess That Number
## Overview
Guess That Number is a game I built using Tkinter in Python.  The object of the game is to guess a number between a specific range in as few tries as possible, using the hints given.  It has 3 levels of difficulty and an ability to set a custom range if the user chooses.


## Structure
This application has 3 pages:
- **Welcome Page**: This is the landing page for the game.  It consists of a description of how the game works, options to select a level of difficulty or a custom range, and a play button to start the game.
- **Game Page**: This is the page the user sees while actively playing the game.  It consists of text indicating the range in which the winning number is contained, an entry box for the user to type a number, hints that display if the user guesses incorrectly, and buttons to submit their guess or quit the game.
- **Farewell Page**: This is the final page the user sees once the game has ended.  It consists of a message that displays based on the outcome of the game and a button to play again if the user chooses.
