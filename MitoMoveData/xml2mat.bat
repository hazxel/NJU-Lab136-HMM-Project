@echo off

set DIR=Z:\AchivedWorkbyName\ChenXudong\MitochondrialTransport
set SOURCEDIR=%DIR%\MitoMoveData\trajectory
set TARGETDIR=%DIR%\HMM
echo %DIR%
echo %SOURCEDIR%
echo %TARGETDIR%

for /d %%t in (27 30 32 37) do (
  C:\ProgramData\Anaconda3\python.exe %DIR%\MitoMoveData\trackmate.py -vv --mat Z:\AchivedWorkbyName\ChenXudong\MitochondrialTransport\HMM\mito%%t\trajectory.mat Z:\AchivedWorkbyName\ChenXudong\MitochondrialTransport\MitoMoveData\trajectory ^.*Div7MitoMove%%tC.*\.xml$
)

pause
