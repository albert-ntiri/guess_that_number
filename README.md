# Guess That Number
## Overview
Guess That Number is a game I built using Tkinter in Python.  The object of the game is to guess a number between a specific range in as few tries as possible, using the hints given.  It has 3 levels of difficulty and an ability to set a custom range if the user chooses.

## Files
Here are the relevant files for this application:
- [**README**](https://github.com/albert-ntiri/guess_that_number/blob/main/README.md): This file contains a high-level walkthrough of the project.
- [**Guess_That_Number.ipynb**](https://github.com/albert-ntiri/guess_that_number/blob/main/Guess_That_Number.ipynb): This file contains the code for the application.  It is written in Jupyter Notebook.
- [**images**](https://github.com/albert-ntiri/guess_that_number/blob/main/images): This folder has screenshots of the application.

## Structure
This application has 3 pages:
- **Welcome Page**: This is the landing page for the game.  It consists of a description for the game, options for selecting a level of difficulty or inputting a custom range, and a play button to start the game.

<p align='center'>
  <img src='images/Welcome_Page.png' alt='welcome_page' width='400'/> <img src='images/Welcome_Page2.png' alt='welcome_page2' width='400'/>
</p>

- **Game Page**: This is the page the user sees while actively playing the game.  It consists of text indicating the range containing the winning number, an entry box for the user to type a number, hints that display if the user guesses incorrectly, and buttons to submit their guess or quit the game.

<p align='center'>
  <img src='images/Game_Page.png' alt='game_page' width='400'/> <img src='images/Game_Page2.png' alt='game_page2' width='400'/>
</p>

- **Farewell Page**: This is the final page the user sees once the game has ended.  It consists of a message that displays based on the outcome of the game and a button to play again if the user chooses.

<p align='center'>
  <img src='images/Farewell_Page.png' alt='farewell_page' width='400'/> <img src='images/Farewell_Page2.png' alt='farewell_page2' width='400'/>
</p>

## Code Structure
The code follows an object-oriented programming format.  It consists of 10 classes:
- **Number**: This class validates user entries from both the custom range and guess fields to determine whether they are integers and if the range is ordered properly.  It also generates random numbers, which are used to select a winning number and pick some of the hints.
- **HintGenerator**: This class takes the winning number and uses it to generate a list of hints.  These hints include but are not limited to prime numbers, factors, multiples, and characteristics about the digits.
- **Page**: This class serves as a toolkit with methods used to create widgets and a list of attributes defining the styles and colors to be used on the application.
- **Header**: This class uses methods inherited from the Page class to specify each widget on the header along with its size and location.
- **WelcomePage**: This class uses methods inherited from the Page class to specify each widget on the Welcome Page along with its size and location.
- **GamePage**: This class uses methods inherited from the Page class to specify each widget on the Game Page along with its size and location.
- **FarewellPage**: This class uses methods inherited from the Page class to specify each widget on the Farewell Page along with its size and location.
- **AppText**: This class serves as a centralized location for all of the text displayed on the application.  It contains a dictionary attribute with all of that text, along with methods for other classes to retrieve specific text.
- **AppManager**: This class builds the header and all of the pages.  It specifies the styles of the widgets, assigns those styles and the colors to different widgets, configures the buttons with their commands and text variables with their label widgets, and manages which page shows on the screen.
- **Game**: This class operates the game from setting it up and starting it, to verifying answers and providing hints, to ending it and determining the final score.

## Process
To develop this app, I followed a process that included 4 main components:
1. Develop the back end.
2. Design the front end.
3. Connect the front and back ends.
4. Refactor.

### 1. Develop the back end.

### 2. Design the front end.

### 3. Connect the front and back ends.

### 4. Refactor.

## Testing
