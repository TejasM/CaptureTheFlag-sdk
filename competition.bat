@ECHO OFF
REM Run this script if you'd like to simulate mant CTF games with your
REM chosen bots.  You can either pass them in on the command line, or
REM modify the various environment variables below.  You should edit
REM the lines that start with the SET command.


REM START! ------- 8< -------- You should customize the next parameters.

REM Customize which commander AIs are run against each other...
SET COMPETITORS=examples


REM STOP! ------- 8< -------- No changes below this line are required.

REM Override the competitors with teh specified command line.
IF NOT ["%1"]==[""] SET COMPETITORS=%1

CALL game\run.bat "%~dp0competition.py" %COMPETITORS%

PAUSE
