@echo off

if "%1"=="" (
  echo Usage %~nx0 ^<filename^>
  exit /b
)

set PYTHON=C:\Users\DENIS\venv\myCompilator\Scripts\python.exe
set JBC_SAMPLE=C:\Users\DENIS\Desktop\Немного_прог\3_курс\Теория компиляторов\JBC
set TK=C:\Users\DENIS\Desktop\Немного_прог\3_курс\Теория компиляторов\myCompilator

set JASPER="C:\Program Files\Java\jdk1.8.0_144\bin\java.exe" -jar "%JBC_SAMPLE%\jasper\jasper.jar"
set JASMIN="C:\Program Files\Java\jdk1.8.0_144\bin\java.exe" -jar "%JBC_SAMPLE%\jasmin-2.4\jasmin.jar"



set FILENAME=%~nx1

del %FILENAME%.class %FILENAME%.j >nul 2>nul

"%PYTHON%" "%TK%\main.py" "%FILENAME%"
%JASMIN% %FILENAME%.j

exit /b

%JAVAC% -target 1.5 -source 1.5 %FILENAME%.java
rem %JAVAP% -p -c %FILENAME%.class >%FILENAME%.javap
%JASPER% %FILENAME%.class
del %FILENAME%.class >nul 2>nul
%JASMIN% %FILENAME%.j
