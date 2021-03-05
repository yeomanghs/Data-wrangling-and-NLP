@echo off
::open anaconda command prompt
call D:\Users\%username%\Anaconda3\Scripts\activate.bat
::check if virtualenv is installed
REM SET checkVirtual=import virtualenv
REM REM start cmd /k "echo %checkVirtual%"
REM start cmd /k "python -c "%checkVirtual%" & echo ^$^?"


::&& execute next after finish first
::in command line use %, batch file use %%
::install virtualenv first &&
REM pip install virtualenv &&
::create virtual env named mytest & activate it
REM cd D:\Users\%username%\Documents & virtualenv mytest & cd mytest\Scripts & activate &&
::go back to desktop
REM cd D:\Users\%username%\Desktop
REM FOR /F "delims=" %%i IN ('dir /b/s requirements.txt') DO set requirement=%%i
::find loc of requirement.txt - install packages
SET requirement=D:\Users\%username%\Desktop\LabelNER\requirements.txt
SET pyFile=D:\Users\%username%\Desktop\LabelNER\textLabel.py
start cmd /k "pip install virtualenv && cd D:\Users\%username%\Documents & virtualenv mytest && cd mytest\Scripts & activate && cd D:\Users\%username%\Desktop && pip install -r %requirement% && streamlit run %pyFile%"

REM SET cmd1=echo a 
REM SET cmd2=echo b
REM SET "allCmd=%cmd1% && %cmd2%"
REM start cmd /k "%allCmd%"


REM SET requirementTxt=D:\Users\%username%\Desktop\Batch\requirements.txt
REM FOR /F "delims=" %i IN ('date /t') DO set today=%i

REM start cmd /k "cd D:\Users\%username%\Documents & virtualenv mytest & cd mytest\Scripts & activate & cd D:\Users\%username%\Desktop"
REM start cmd /k FOR /F "delims=" %i IN ('dir /b/s requirements.txt') DO set requirement=%i

REM start cmd /k "pip install virtualenv && FOR /F "delims=" %%i IN ('date /t') DO set today=%%i & echo %today"

REM SET app=dir /b/s textLabel.py
REM pip install -r %requirement%"
REM streamlit run %app%


