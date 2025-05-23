# Local Pomodoro Application

How to **run** the application:

On Linux:
    setup.sh -> installs the required modules
    start.sh -> runs the app
    python3 src/main.py -drop -> resets database and runs the app
    python3 src/main.py -config -> updates the config and runs the app

On Windows:
    pip install -r requirements.txt -> installs the required modules
    python src/main.py -> runs the app
    python src/main.py -drop -> resets database and runs the app
    python src/main.py -config -> updates the config and runs the app

Pomodoro is a focus technique used to enhance productivity. It's known to help focus and maintain a state of flow. It works by diving the work schedule in 25 minute blocks (pomodoros) and allowing a 5 minute break between each block.

There are many different ways to use this technique, 25/5, 50/10, 120/30. The goals is always the same, consistent focus and consistent rest.

This application is meant to be used locally and fit to the users needs. It's easy to configure and set up.

Current features:

    - load an inspiring quote at the beginning of each session
    - set and use a default quote of your own
    - set suggested actions for the breaks
    - display the average session and break time (allowing you to gauge how you tend to prefer to work over time)
    - configure whether the sessions and breaks should start automatically or if they should wait for user input
    - changing the default values of the sessions and breaks to better suit your needs
    - SQLite integration
