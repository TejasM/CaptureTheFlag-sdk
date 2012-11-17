Welcome to the AI Sandbox Capture The Flag SDK

Capture the Flag is a strategic game played by two teams of bots. Points are scored whenever a team retrieves the other teams flag and returns it to its flag scoring location. The winner is the team that scores the most points. Dead bots are respawned synchronously at regular intervals.

Bots in this game can not be interactively controlled. Bots are controlled by strategic commanders which are written in python. More information describing how to write a commander can be found at http://aisandbox.com/. There you will find step by step guides to writing your own commander, API documentation and information on how to submit your commander into the competition.

To start the Capture the Flag application run simulate.bat. You can edit the COMPETITORS variable within simulate.bat to specify which commanders should be run against each other.

Keyboard Controls
    H                         - Show/Hide help screen

    W,S                       - Camera Forward, back
    A,D,Q,E, middle mouse     - Camera Panning
    Right mouse               - Camera Rotation
    Home                      - Reset camera position
    Shift                     - Faster camera motion modifier
    Ctrl                      - Slower camera motion modifier

    F1-F4                     - Debug visualizations
    F9                        - Performance visualization
    End                       - Hide debug sidebar


